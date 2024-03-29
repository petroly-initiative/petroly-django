from django.contrib import admin
from .models import TelegramProfile, Token, TelegramRecord


@admin.register(TelegramRecord)
class TelegramRecordAdmin(admin.ModelAdmin):

    list_display = ["user_id", "created_on"]
    search_fields = ["user_id"]


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):

    list_display = ["token", "user"]


@admin.register(TelegramProfile)
class TelegramProfileAdmin(admin.ModelAdmin):
    """
    Custom settings for `TelegramProfile` app in admin site.
    """

    search_fields = ["user__username"]
    search_help_text = "Search in usernames"
    list_display = [
        "user",
        "id",
        "username",
    ]
