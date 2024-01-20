from django.contrib import admin

from whatsguard import models


@admin.register(models.Chat)
class ChatAdmin(admin.ModelAdmin):
    """
    Custom admin model site for `Chat` model.
    """

    list_display = ["id", "name", "is_group"]
    list_filter = [
        "is_group",
    ]
    search_fields = ["id", "name"]


@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    """
    Custom admin model site for `Contact` model.
    """

    list_display = ["id", "pushname", "number", "created_on"]
    list_filter = [
        "ignore",
    ]
    search_fields = ["id", "pushname", "number"]


@admin.register(models.Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Custom admin model site for `Message` model.
    """

    list_display = ["id", "author", "chat", "contact", "created_on"]
    list_filter = ["device_type"]
    search_fields = ["id", "pushname", "number"]
