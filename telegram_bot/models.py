"""
All `telegram_bot` models.

models: 
    - TelegramProfile
"""

from django.db import models

from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()

class TelegramProfile(models.Model):
    """
    A class to represent the link between a django user and the telegram account
    """

    telegram_user_id = models.CharField(_("telegram user ID"), max_length=256)
    telegram_username = models.CharField(_("telegram username"), max_length=256)

    user = models.OneToOneField(User, verbose_name=_("user"), on_delete=models.CASCADE)
