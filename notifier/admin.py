"""
Customization of the admin site for `notifier` app.
"""

from django.contrib import admin
from . import models

admin.site.register(
    [
        models.Course,
        models.NotificationEvent,
        models.NotificationChannel,
        models.Term
    ]
)


@admin.register(models.TrackingList)
class TrackingListAdmin(admin.ModelAdmin):
    """
    Custom settings for `TrackingList` app in admin site.
    """

    filter_horizontal = ["courses", "channels"]
