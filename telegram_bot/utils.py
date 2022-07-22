"""
This module provides some utilities for `telegram_bot` app.
It also helps converting some ORM methods into async.
"""

from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model

from .models import TelegramProfile

User = get_user_model()

@sync_to_async
def user_from_telegram(user_id:int) -> User:

    return TelegramProfile.objects.get(id=user_id).user

