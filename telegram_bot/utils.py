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

from notifier.utils import fetch_data
from notifier.models import Course, Term
from notifier import utils as notifier_utils
from data import DepartmentEnum

from .models import TelegramProfile, Token


User = get_user_model()


def escape_md(txt) -> str:
    """To escape special characters:
    `_`,  and `*`"""
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
        msg += rf"{course.crn} \- {course.department}\n"

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

    raw_courses = fetch_data(term, dept)
    raw_courses = {x["course_number"] for x in raw_courses}
    # print(raw_courses)
    return list(raw_courses)


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
) -> List[str]:

    dept_courses = fetch_data(term, department=dept)
    tracked_sections = await get_tracked_crns(user_id)
    # filtering already tracked sections, and course-specific sections
    course_sections = [
        section
        for section in dept_courses
        if section["course_number"] == course
        and section["crn"] not in tracked_sections
    ]
    course_sections = [
        format_section(
            course=section["course_number"],
            section=section["section_number"],
            seats=section["available_seats"],
            class_days=section["class_days"],
            start_time=section["start_time"],
            end_time=section["end_time"],
        )
        for section in course_sections
    ]

    return course_sections


####### formatting utilities ####


def format_section(
    course: str,
    section: str,
    seats: int,
    class_days: str,
    start_time: str,
    end_time: str,
) -> str:
    return f"""
    {course}-{section} {"🔴 full" if seats <= 0 else f'🟢 {seats} seats left'}
    {class_days} | {start_time[0:2]}:{start_time[2:]}-{start_time[0:2]}:{end_time[2:]}
    """


def construct_reply_callback_grid(
    list_: List,
    row_length: int,
    prev_callback_data: Dict[str, str] = None,
    is_callback_different: bool = False,
) -> List[List[InlineKeyboardButton]]:

    if prev_callback_data is None:
        prev_callback_data = {}

    result = []

    if is_callback_different:
        for i in range(int(len(list_) / row_length)):
            result.append(
                [
                    InlineKeyboardButton(
                        text=el[0], callback_data=(el[1], prev_callback_data)
                    )
                    for el in list_[
                        i * row_length : i * row_length + row_length
                    ]
                ]
            )
        if len(list_) % row_length != len(list_) / row_length:
            result.append(
                [
                    InlineKeyboardButton(
                        text=el[0], callback_data=(el[1], prev_callback_data)
                    )
                    for el in list_[int(len(list_) / row_length) * row_length :]
                ]
            )
    else:
        for i in range(int(len(list_) / row_length)):

            result.append(
                [
                    InlineKeyboardButton(
                        text=el, callback_data=(el, prev_callback_data)
                    )
                    for el in list_[
                        i * row_length : i * row_length + row_length
                    ]
                ]
            )
            print(len(result))
        if len(list_) % row_length != len(list_) / row_length:
            result.append(
                [
                    InlineKeyboardButton(
                        text=el, callback_data=(el, prev_callback_data)
                    )
                    for el in list_[int(len(list_) / row_length) * row_length :]
                ]
            )
            print(len(result))
    return result
