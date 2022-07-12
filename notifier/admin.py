"""
Customization of the admin site for `notifier` app.
"""

from django.contrib import admin
from .models import TrackingList, Course, NotificationEvent

admin.site.register([Course, NotificationEvent])

@admin.register(TrackingList)
class TrackingListAdmin(admin.ModelAdmin):
    """
    Custom settings for `TrackingList` app in admin site.
    """

    filter_horizontal = [
        "courses",
    ]
