from django.contrib import admin
from .models import TelegramProfile, Token


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):

    list_display = ["token", "user"]


@admin.register(TelegramProfile)
class TelegramProfileAdmin(admin.ModelAdmin):
    """
    Custom settings for `TelegramProfile` app in admin site.
    """

    list_display = [
        "user",
        "username",
    ]
