"""
This module provides some utilities for `telegram_bot` app.
It also helps converting some ORM methods into async.
"""

import re
from typing import List
from asgiref.sync import sync_to_async, async_to_sync

from telegram import Update
from telegram.ext import Application
from telegram.constants import ParseMode
from django.contrib.auth import get_user_model
from django.conf import settings

from notifier import utils as notifier_utils
from notifier.models import Course

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
        await update.message.reply_text(
            text=f"You don't have a TelegramProfile. Connect your Telegram {user_id}"
        )

        raise TelegramProfile.DoesNotExist from exc


def format_courses(courses: List[Course]):
    """Format the courses list"""

    msg = "*CRN* \- *Department*\n\n"
    for course in courses:
        msg += f"{course.crn} \- {course.department}\n"

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
