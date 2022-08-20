"""
Customization of the admin site for `notifier` app.
"""

from django.contrib import admin
from . import models

admin.site.register(
    [
        models.NotificationEvent,
        models.Cache,
    ]
)


@admin.register(models.TrackingList)
class TrackingListAdmin(admin.ModelAdmin):
    """
    Custom settings for `TrackingList` app in admin site.
    """

    list_display = [
        "id",
        "user",
        "channels",
    ]
    list_filter = [
        "channels",
    ]
    filter_horizontal = [
        "courses",
    ]


@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    """
    Custom settings for `Course` app in admin site.
    """

    list_display = [
        "crn",
        "term",
        "available_seats",
        "waiting_list_count",
        "department",
    ]
    list_filter = [
        "term",
        "department",
    ]


@admin.register(models.Term)
class TermAdmin(admin.ModelAdmin):
    """
    Custom settings for `Term` app in admin site.
    """

    list_display = [
        "short",
        "allowed",
    ]
