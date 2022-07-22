from django.contrib import admin
from .models import TelegramProfile, Token

admin.site.register(
    [
        TelegramProfile,
    ]
)


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):

    list_display = ["token", "user"]
