"""
This module provides some utilities for `telegram_bot` app.
It also helps converting some ORM methods into async.
"""

import re
from typing import Dict, List, Tuple
from asgiref.sync import sync_to_async, async_to_sync

from telegram import InlineKeyboardButton, Update
from telegram.ext import Application
from telegram.constants import ParseMode
from django.conf import settings
from django.contrib.auth import get_user_model

from notifier import utils as notifier_utils
from notifier.models import Course, Term, TrackingList
from data import DepartmentEnum

from .models import TelegramProfile, Token


User = get_user_model()


def escape_md(txt) -> str:
    """To escape special characters:
    `_`,  and `*` and `.`"""
    match_md = r"((([_*\.]).+?\3[^_*\.]*)*)([_*\.])"

    return re.sub(match_md, r"\g<1>\\\g<4>", txt)


@sync_to_async
def get_user(user_id: int):

    return TelegramProfile.objects.get(id=user_id).user


async def user_from_telegram(user_id: int, update: Update) -> User:

    try:
        return await get_user(user_id)

    except TelegramProfile.DoesNotExist as exc:
        # await update.message.reply_text(
        #     text=f"You don't have a TelegramProfile. Connect your Telegram"
        # )

        raise TelegramProfile.DoesNotExist from exc


def format_courses(courses: List[Course]):
    """Format the courses list"""

    msg = r"*CRN* \- *Department*\n\n"
    for course in courses:
        msg += f"{course.crn} \\- {course.department}\n"

    return msg


@async_to_sync
async def send_telegram_message(chat_id: int, msg: str):
    """To make this method as sync

    Args:
        chat_id (int): like user's id
        msg (str): a MD text message
    """
    async with Application.builder().token(
        settings.TELEGRAM_TOKEN
    ).build() as app:
        await app.bot.send_message(
            chat_id=chat_id,
            text=msg,
            parse_mode=ParseMode.MARKDOWN_V2,
        )


@sync_to_async
def tracked_courses_(user: User):
    """To make ORM async"""

    return notifier_utils.formatter_md(user.tracking_list.courses.all())


@sync_to_async
def verify_user_from_token(
    token: str, user_id: int, username: str
) -> User | None:
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
    try:
        await get_user(user_id)
        return await fetch_terms()

    except TelegramProfile.DoesNotExist as exc:
        raise exc


@sync_to_async
def fetch_terms() -> List[Tuple[str, str]]:
    return [
        (term.short, term.long) for term in Term.objects.filter(allowed=True)
    ]


@sync_to_async
def get_departments() -> List[str]:
    result = DepartmentEnum.values
    result.pop(0)
    return result


def get_courses(term: str, dept: str) -> List[str]:

    raw_courses = notifier_utils.fetch_data(term, dept)
    raw_courses = list({x["course_number"] for x in raw_courses})
    raw_courses.sort()

    return raw_courses


@sync_to_async
def get_tracked_crns(user_id: int) -> List[str]:
    tracked_list = TelegramProfile.objects.get(id=user_id).user.tracking_list
    tracked_courses = list(tracked_list.courses.all())

    return [
        course.crn for course in tracked_courses if len(tracked_courses) != 0
    ]


# ! we need to filter hybrid sections, and eliminate already tracked courses
async def get_sections(
    term: str, dept: str, course: str, user_id: int
) -> List[Tuple[str, Dict[str, str | int]]]:

    dept_courses = notifier_utils.fetch_data(term, department=dept)
    # sort sections according to the `section_number`
    dept_courses.sort(key=lambda el: el["section_number"])

    tracked_sections = await get_tracked_crns(user_id)
    # filtering already tracked sections, and course-specific sections
    course_sections = [
        section
        for section in dept_courses
        if section["course_number"] == course
        and section["crn"] not in tracked_sections
    ]
    course_sections = [
        (
            format_section(
                course=section["course_number"],
                section=section["section_number"],
                seats=section["available_seats"],
                class_days=section["class_days"],
                class_type=section["class_type"],
                start_time=section["start_time"],
                end_time=section["end_time"],
                waitlist_count=section["waiting_list_count"],
            ),
            {
                "crn": section["crn"],
                "seats": section["available_seats"],
                "waitlist": section["waiting_list_count"],
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

    # get all currently tracked courses
    tracking_list = TelegramProfile.objects.get(id=user_id).user.tracking_list
    # append the course to the list
    tracking_list.courses.create(
        crn=crn,
        term=term,
        available_seats=seats,
        waiting_list_count=waitlist_count,
        department=dept,
    )
    ## ? can a user reach this point without having a tracking list instance?
    ## ? if so we need to explicitly save the object for first time in ORM 

@sync_to_async
def untrack_section(crn: str, user_id: int):
    tracking_list = TelegramProfile.objects.get(pk=user_id).user.tracking_list;
    tracking_list.courses.remove(tracking_list.courses.get(crn=crn))
    tracking_list.save()

@sync_to_async
def clear_tracking(term: str, user_id: int):
    tracking_list = TelegramProfile.objects.get(pk=user_id).user.tracking_list;
    if(term == "ALL"):
        tracking_list.courses.clear()
        tracking_list.save()
    else:
        print(tracking_list.courses.filter(term=term))
        tracking_list.courses.remove()
        tracking_list.save()


####### formatting utilities ####


def format_section(
    course: str,
    class_type: str,
    section: str,
    seats: int,
    waitlist_count: int,
    class_days: str,
    start_time: str,
    end_time: str,
) -> str:
    if start_time and end_time:
        return (
            f"{section}{'📘' if class_type == 'LEC' else '🧪' if class_type == 'LAB' else ''}"
            + f" {'🔴 FULL' if seats <= 0 else f'🟢 {seats}🪑 - {waitlist_count}⏳'}"
            + f" {class_days} | {start_time[0:2]}:{start_time[2:]}-{start_time[0:2]}:{end_time[2:]}"
        )

    return (
        f"{section}{'📘' if class_type == 'LEC' else '🧪' if class_type == 'LAB' else ''}"
        + f" {'🔴 FULL' if seats <= 0 else f'🟢 {seats}🪑 - {waitlist_count}⏳'}"
        + f" {class_days} | No time info"
    )


def construct_reply_callback_grid(
    input_list: List,
    row_length: int,
    is_callback_different: bool = False
    ) -> List[List[InlineKeyboardButton]]:
    result = [];
    if is_callback_different:
        for i in range(int(len(input_list) / row_length)):
            result.append(
                [
                    InlineKeyboardButton(text=el[0], callback_data=el[1])
                    for el in input_list[
                        i * row_length : i * row_length + row_length
                    ]
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
                    for el in input_list[
                        i * row_length : i * row_length + row_length
                    ]
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
    print(len(result))
    return result
