"""
This module provides some utilities for `telegram_bot` app.
It also helps converting some ORM methods into async.
"""

from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model

from .models import TelegramProfile, Token

User = get_user_model()


@sync_to_async
def user_from_telegram(user_id: int) -> User:

    return TelegramProfile.objects.get(id=user_id).user


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
