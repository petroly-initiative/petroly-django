"""
This module provides some utilities for `telegram_bot` app.
It also helps converting some ORM methods into async.
"""

from collections.abc import Callable
import os
import re
import logging
from io import BytesIO
from typing import Awaitable, Dict, List, Tuple, overload
from asgiref.sync import sync_to_async, async_to_sync

from telegram import error
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application
from telegram.constants import ParseMode
from django.conf import settings
from django.contrib.auth import get_user_model
from PIL import Image, ImageFont, ImageDraw
import requests

from notifier import utils as notifier_utils
from notifier.models import Course, Term
from data import SubjectEnum

from .models import TelegramProfile, Token


User = get_user_model()
logger = logging.getLogger(__name__)


def escape_md(txt) -> str:
    """To escape special characters:
    `_`,  and `*` and `.` and `-`"""
    match_md = r"((([_*-\.]).+?\3[^_*-\.]*)*)([_*-\.])"

    return re.sub(match_md, r"\g<1>\\\g<4>", txt)


@sync_to_async
def get_user(user_id: int):

    return TelegramProfile.objects.get(id=user_id).user


async def user_from_telegram(user_id: int, update: Update) -> User:

    try:
        return await get_user(user_id)

    except TelegramProfile.DoesNotExist as exc:
        raise TelegramProfile.DoesNotExist from exc


def format_courses(courses: List[Course]):
    """Format the courses list"""

    msg = r"*CRN* \- *Department*\n\n"
    for course in courses:
        msg += f"{course.crn} \\- {course.department}\n"

    return msg


@async_to_sync
async def send_telegram_message(chat_id: int, msg: str):
    """Useful to send one-time message.
    To make this method as sync

    Args:
        chat_id (int): like user's id
        msg (str): a MD text message
    """
    async with Application.builder().token(settings.TELEGRAM_TOKEN).build() as app:
        try:
            await app.bot.send_message(
                chat_id=chat_id,
                text=msg,
                parse_mode=ParseMode.MARKDOWN_V2,
            )

        except error.Forbidden as exc:
            logger.error("The user %s might have blocked us - %s", chat_id, exc)

        except Exception as exc:
            logger.error("Couldn't send to Telegram: %s - %s", chat_id, exc)


def mass_send_telegram_message(chat_ids: List[int], message: str) -> None:
    """send many message to many users

    Args:
        chat_ids (List[int]): list of users to send them
        message (str): the message to send
    """

    for chat_id in chat_ids:
        send_telegram_message(chat_id, message)


@async_to_sync
async def send_telegram_changes(chat_id: int, msg: str):
    """Sending the changes notification.
    To make this method as sync

    Args:
        chat_id (int): like user's id
        msg (str): a MD text message
    """
    async with Application.builder().token(settings.TELEGRAM_TOKEN).build() as app:
        await app.bot.send_message(
            chat_id=chat_id,
            text=msg,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Go to Banner Now",
                            url="https://banner9-registration.kfupm.edu.sa/StudentRegistrationSsb/ssb/term/termSelection?mode=registration",
                        )
                    ]
                ]
            ),
        )


@sync_to_async
def tracked_courses_(user: User):
    """To make ORM async"""

    return notifier_utils.formatter_md(user.tracking_list.courses.all())


@sync_to_async
def verify_user_from_token(token: str, user_id: int, username: str) -> User | None:
    """To make connection between user's Petroly account
    and Telegram's one"""

    tokens = Token.objects.filter(token=token)
    if tokens:
        if tokens[0].revoked:
            return None

        # store the user Telegram info
        user: User = tokens[0].user
        try:
            TelegramProfile.objects.get(user=user)

        except TelegramProfile.DoesNotExist:
            TelegramProfile.objects.create(
                user=user,
                id=user_id,
                username=username,
            )

        # revoke the token
        tokens[0].revoked = True
        tokens[0].save()

        return user

    return None


async def get_terms(user_id: int) -> List[Tuple[str, str]]:
    """getting all allowed terms form DB"""

    return await fetch_terms()


@sync_to_async
def fetch_terms() -> List[Tuple[str, str]]:
    """a function to format term objects into accpetable format for InlineKEyboardButton callback data"""
    return [(term.short, term.long) for term in Term.objects.filter(allowed=True)]


@sync_to_async
def get_departments() -> List[str]:
    """a function to retrieve all stored departments"""
    result = SubjectEnum.values
    result.pop(0)
    return result


@sync_to_async
def fetch_data_async(term, department):
    data = notifier_utils.fetch_data(term, department)

    # sort sections according to the `section_number`
    data.sort(key=lambda el: el["sequenceNumber"])
    return data


@sync_to_async
def get_courses(term: str, dept: str) -> List[str]:
    """a function to retrieve all courses under specified department and term"""

    raw_courses = notifier_utils.fetch_data(term, dept)
    raw_courses = list({x["subjectCourse"] for x in raw_courses})
    raw_courses.sort()

    return raw_courses


@sync_to_async
def get_tracked_crns(user_id: int) -> List[str]:
    """a function to retrieve all CRNs in your tracking list"""
    tracked_list = TelegramProfile.objects.get(id=user_id).user.tracking_list
    tracked_courses = list(tracked_list.courses.all())

    return [course.crn for course in tracked_courses if len(tracked_courses) != 0]


# ! we need to filter hybrid sections, and eliminate already tracked courses
async def get_sections(
    term: str, dept: str, course: str, user_id: int
) -> List[Tuple[str, Dict[str, str | int]]]:
    """a function to return all untracked sections from a specific course, term, and a department"""

    dept_courses = await fetch_data_async(term, dept)
    tracked_sections = await get_tracked_crns(user_id)

    # filtering already tracked sections, and course-specific sections
    course_sections = [
        section
        for section in dept_courses
        if section["subjectCourse"] == course
        and section["courseReferenceNumber"] not in tracked_sections
    ]
    course_sections = [
        (
            format_section(
                section=section["sequenceNumber"],
                seats=section["seatsAvailable"],
                class_days="",
                class_type=section["meetingsFaculty"][0]["meetingTime"][
                    "meetingScheduleType"
                ],
                start_time=section["meetingsFaculty"][0]["meetingTime"]["beginTime"],
                end_time=section["meetingsFaculty"][0]["meetingTime"]["endTime"],
                waitlist_count=section["waitAvailable"],
            ),
            {
                "crn": section["courseReferenceNumber"],
                "seats": section["seatsAvailable"],
                "waitlist": section["waitAvailable"],
            },
        )
        for section in course_sections
    ]

    return course_sections


@sync_to_async
def submit_section(
    crn: int,
    seats: int,
    waitlist_count: int,
    user_id: int,
    term: int,
    dept: str,
) -> None:
    """a function to store a section data in the user tracking list"""

    # get all currently tracked courses
    tracking_list = TelegramProfile.objects.get(id=user_id).user.tracking_list
    # get the `Course` obj, create of not exist
    # and update the status info, to be compared later
    try:
        obj = Course.objects.get(
            crn=crn,
            term=term,
            department=dept,
        )

        obj.available_seats = seats
        obj.waiting_list_count = waitlist_count
        obj.raw = notifier_utils.get_course_info(obj)
        obj.save()

        # append the course to the list
        tracking_list.courses.add(obj)

    except Course.DoesNotExist:
        # Create & append the course to the list
        obj = tracking_list.courses.create(
            crn=crn,
            term=term,
            available_seats=seats,
            waiting_list_count=waitlist_count,
            department=dept,
        )
        obj.raw = notifier_utils.get_course_info(obj)
        obj.save()

    ## ? can a user reach this point without having a tracking list instance?
    ## ? if so we need to explicitly save the object for first time in ORM


@sync_to_async
def untrack_section(crn: str, user_id: int):
    """a function to remove a section data in the user tracking list"""
    tracking_list = TelegramProfile.objects.get(pk=user_id).user.tracking_list
    tracking_list.courses.remove(tracking_list.courses.get(crn=crn))
    tracking_list.save()


@sync_to_async
def clear_tracking(term: str, user_id: int):
    """a function to remove all sections under specified terms from the tracking list"""
    tracking_list = TelegramProfile.objects.get(pk=user_id).user.tracking_list
    if term == "ALL":
        tracking_list.courses.clear()
        tracking_list.save()
    else:
        tracking_list.courses.remove()
        tracking_list.save()


#### formatting utilities ####


def format_section(
    class_type: str,
    section: str,
    seats: int,
    waitlist_count: int,
    class_days: str,
    start_time: str,
    end_time: str,
) -> str:
    """a fromatting function to format InlineKeyboardButtons for sections in /track command"""

    if start_time and end_time:
        return (
            f"{section}{'📘' if class_type == 'LC' else '🧪' if class_type == 'LB' else ''}"
            + f" {'🔴 FULL' if seats <= 0 else f'🟢 {seats}🪑 - {waitlist_count}⏳'}"
            + f" {class_days} | {start_time[0:2]}:{start_time[2:]}-{start_time[0:2]}:{end_time[2:]}"
        )

    return (
        f"{section}{'📘' if class_type == 'LC' else '🧪' if class_type == 'LB' else ''}"
        + f" {'🔴 FULL' if seats <= 0 else f'🟢 {seats}🪑 - {waitlist_count}⏳'}"
        + f" {class_days} | No time info"
    )


def construct_reply_callback_grid(
    input_list: List, row_length: int = 3, is_callback_different: bool = False
) -> List[List[InlineKeyboardButton]]:
    """a formatter function to allocate buttons according to the following:

    Args:
        input_list(List[str, Tuple[str, str]]): the list which we would like to format into buttons
        row_length(int): how many buttons to place in 1 row
        is_callback_different(bool): used when the displayed text on the button is different from the
        stored callback_data.
            - When True, the input_list elements must be of type Tuple[str, str].
            - When False (default), the input_list elements must be of type str.
    """

    result = []
    if is_callback_different:
        for i in range(int(len(input_list) / row_length)):
            result.append(
                [
                    InlineKeyboardButton(text=el[0], callback_data=el[1])
                    for el in input_list[i * row_length : i * row_length + row_length]
                ]
            )
        if len(input_list) % row_length != len(input_list) / row_length:
            result.append(
                [
                    InlineKeyboardButton(text=el[0], callback_data=el[1])
                    for el in input_list[
                        int(len(input_list) / row_length) * row_length :
                    ]
                ]
            )
    else:
        for i in range(int(len(input_list) / row_length)):

            result.append(
                [
                    InlineKeyboardButton(text=el, callback_data=el)
                    for el in input_list[i * row_length : i * row_length + row_length]
                ]
            )

        if len(input_list) % row_length != len(input_list) / row_length:
            result.append(
                [
                    InlineKeyboardButton(text=el, callback_data=el)
                    for el in input_list[
                        int(len(input_list) / row_length) * row_length :
                    ]
                ]
            )
    return result


def _break_words(text: str) -> str:
    """To healp break words in multiple lines"""
    text = '"' + text + '"'
    MAX_CHAR = 20
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        if len(current_line + word) <= MAX_CHAR:
            current_line += " " + word if current_line else word
        else:
            lines.append(current_line.strip())
            current_line = word
    if current_line:
        lines.append(current_line.strip())

    return " \n".join(lines)


@sync_to_async
def generate_card(out: BytesIO, text: str, name: str) -> BytesIO:
    # it's a must to reset the file cursor to the begining
    out.seek(0)
    try:
        r = requests.post(
            "https://clipdrop-api.co/remove-background/v1",
            files={
                "image_file": ("img.png", out, "image/png"),
            },
            headers={
                "x-api-key": os.environ.get("CLIPDROP_TOKEN", ""),
            },
        )

        if r.ok:
            out.close()
            front = Image.open(BytesIO(r.content))
        else:
            r.raise_for_status()

    except Exception as e:
        raise e

    with Image.open("./template.png").convert("RGBA") as background:
        width, height = background.size
        front_h = 1800
        front_w = int(front_h / front.size[1] * front.size[0])
        front = front.resize((front_w, front_h))
        background.paste(front, (width - front_w - 100, height - front_h), front)
        # make a blank image for the text, initialized to transparent text color
        txt = Image.new("RGBA", background.size, (255, 255, 255, 0))
        txt_name = Image.new("RGBA", background.size, (255, 255, 255, 0))
        if text.isascii():
            fnt_it = ImageFont.truetype("./MinionPro-BoldCnIt.otf", 140)
        else:
            fnt_it = ImageFont.truetype("./Gulzar-Regular.ttf", 130)
        if name.isascii():
            fnt = ImageFont.truetype("./MinionPro-Regular.otf", 50)
        else:
            fnt = ImageFont.truetype("./Harir_complete_OTF_Harir.otf", 50)

        # get a drawing context
        d = ImageDraw.Draw(txt)
        d_name = ImageDraw.Draw(txt)
        # draw text quote
        d.text(
            (width // 4 - 100, height // 2 - 500),
            _break_words(text),
            font=fnt_it,
            fill=(255, 255, 255, 200),
            spacing=60,
            align="center",
        )
        # draw text name
        d_name.text(
            (width // 4, height - 150),
            f"- {name} (2023)",
            font=fnt,
            fill=(255, 255, 255, 160),
        )
        res = Image.alpha_composite(background, txt)
        res = Image.alpha_composite(res, txt_name)
        res = res.convert("RGB")

        res_io = BytesIO()
        res.save(res_io, format="jpeg")
        res_io.seek(0)

        return res_io
