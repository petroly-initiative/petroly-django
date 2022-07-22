"""
This module provides some utilities for `telegram_bot` app.
It also helps converting some ORM methods into async.
"""
from typing import List
from asgiref.sync import sync_to_async

from telegram import Update
from django.contrib.auth import get_user_model
from notifier.models import Course

from .models import TelegramProfile, Token

User = get_user_model()


@sync_to_async
def get_user(user_id: int):

    return TelegramProfile.objects.get(id=user_id).user

async def user_from_telegram(user_id: int, update: Update) -> User:

    try:
        return await get_user(user_id)

    except TelegramProfile.DoesNotExist:
        await update.message.reply_text(
            text="You don't have a TelegramProfile. Connect your Telegram"
        )

def formatt_courses(couerses: List[Course]):

    msg = "*CRN* \- *Department*\n\n"
    for course in couerses:
        msg += f'{course.crn} \- {course.department}\n'

    return msg

@sync_to_async
def tracked_courses_(user: User):

    return formatt_courses(user.tracking_list.courses.all())
    return user.tracking_list.courses.all()


@sync_to_async
def verify_user_from_token(
    token: str, user_id: int, chat_id: int, username: str
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
