"""
This module provides some utilities for `telegram_bot` app.
It also helps converting some ORM methods into async.
"""

import re
from typing import Dict, List, Union, cast
from asgiref.sync import sync_to_async

from telegram import InlineKeyboardButton, Update
from django.contrib.auth import get_user_model
from data import DepartmentEnum

from notifier.utils import fetch_data, formatter_md
from notifier.models import Course, Term

from .models import TelegramProfile, Token


User = get_user_model()


def escape_md(txt) -> str:
    """To escape special characters:
    `_`,  and `*`"""
    match_md = r"((([_*\.]).+?\3[^_*\.]*)*)([_*\.])"

    return re.sub(match_md, "\g<1>\\\\\g<4>", txt)


@sync_to_async
def get_user(user_id: int):
  
    return TelegramProfile.objects.get(id=user_id).user


async def user_from_telegram(user_id: int, update: Update) -> User:  # type: ignore
    try:
        return await get_user(user_id)

    except TelegramProfile.DoesNotExist as exc:
        # await update.message.reply_text(
        #     text=f"You don't have a TelegramProfile. Connect your Telegrammmm"
        # )

        raise TelegramProfile.DoesNotExist from exc


def format_courses(courses: List[Course]):
    """Format the courses list"""

    msg = "*CRN* \- *Department*\n\n"
    for course in courses:
        msg += f"{course.crn} \- {course.department}\n"

    return msg


@sync_to_async
def tracked_courses_(user: User):
    """To make ORM async"""

    if(len(user.tracking_list.courses.all()) != 0):
        return formatter_md(user.tracking_list.courses.all())
    else: 
        return "No Courses are currently tracked"


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


async def get_terms() -> List[str]:
    return await fetch_terms();

@sync_to_async
def fetch_terms() -> List[str]:
    return[term.short for term in Term.objects.filter(allowed= True)];

@sync_to_async
def get_departments() -> List[str]:
    result = DepartmentEnum.values;
    result.pop(0)
    return result;

def get_courses(term: str, dept: str) -> List[str]:

    raw_courses  = fetch_data(term, dept)
    print(raw_courses)
    raw_courses = {x["course_number"] for x in raw_courses}
    print(raw_courses)
    return cast( List[str] , raw_courses);

@sync_to_async
def get_tracked_crns(user_id: int) -> List[str]:
    courses = TelegramProfile.objects.get(id=user_id).user.tracking_list.courses;
    return [course.crn for course in courses];

# ! we need to filter hybrid sections, and eliminate already tracked courses
async def get_sections(term: str, dept: str, course: str, user_id: int) -> List[str]:

    dept_courses = fetch_data(term, department=dept)
    tracked_sections = await get_tracked_crns(user_id);
    # filtering already tracked sections, and course-specific sections
    course_sections = [section for section in dept_courses 
    if section["course_number"] == course and section["crn"] not in tracked_sections]
    course_sections = [
        f"""
    {section["course_number"]}\-{section["section_number"]} {"**🔴 full**" if section["available_seats"] <= 0 else f'🟢 **{section["available_seats"]}** seats left'}
    {section["class_days"]}\| {section["start_time"][0:2]}:{section["start_time"][2:]}-{section["end_time"][0:2]}:{section["end_time"][2:]}
    """ for section in course_sections]

    return course_sections


def construct_reply_callback_grid(list: List, row_length: int = 3, prev_callback_data: Dict[str, str] = {}) -> List[List[InlineKeyboardButton]]:
    result = [];
    for i in range(int(len(list) / row_length)):
      
        result.append([
            InlineKeyboardButton(text=el, callback_data=(el, prev_callback_data)) for el in list[i * row_length: i*row_length + row_length]
        ])

    if(len(list) % row_length != len(list) / row_length):
        result.append([
            InlineKeyboardButton(text=el, callback_data=(el, prev_callback_data)) for el in list[int(len(list) / row_length * row_length):]
        ])
    return result;