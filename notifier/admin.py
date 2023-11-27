"""
Customization of the admin site for `notifier` app.
"""

from django.contrib import admin
from . import models

admin.site.register([models.NotificationEvent, models.Status, models.BannerEvent])


def repeats(obj: models.Banner) -> str:
    return abs(obj.scheduler.repeats) - 1


@admin.register(models.Banner)
class BannerAdmin(admin.ModelAdmin):
    """
    Custom admin model site for `Banner` model.
    """

    list_display = ["id", "user", "active", repeats]
    list_filter = [
        "active",
    ]
    search_fields = [
        "user__username",
    ]


@admin.register(models.TrackingList)
class TrackingListAdmin(admin.ModelAdmin):
    """
    Custom settings for `TrackingList` app in admin site.
    """

    list_display = ["id", "user", "channels", "updated_on"]
    list_filter = [
        "channels",
    ]
    filter_horizontal = [
        "courses",
        "register_courses",
    ]
    search_fields = [
        "user__username",
    ]


@admin.decorators.display(description="Valid", boolean=True)
def valid(obj) -> bool:
    return obj.is_valid()


@admin.register(models.Cache)
class CacheAdmin(admin.ModelAdmin):
    """
    Custom settings for `Cache` model in admin site.
    """

    list_display = [
        "id",
        "term",
        "department",
        "updated_on",
        "stale",
        valid,
    ]
    list_filter = [
        "term",
        "department",
    ]
    actions = ["add_5_seconds", "sub_5_seconds", "make_stale_false"]

    def make_stale_false(self, request, queryset):
        """Toggle the value of `stale` field"""
        queryset.update(stale=False)

    def add_5_seconds(self, request, queryset):
        """add 5 to `swr` & age"""
        for q in queryset:
            q.age = q.age + 5
            q.swr = q.swr + 5
            q.save()

    def sub_5_seconds(self, request, queryset):
        """subtract 5 to `swr` & age"""
        for q in queryset:
            q.age = q.age - 5
            q.swr = q.swr - 5
            q.save()


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
    search_fields = ["crn"]


@admin.register(models.Term)
class TermAdmin(admin.ModelAdmin):
    """
    Custom settings for `Term` app in admin site.
    """

    list_display = [
        "short",
        "allowed",
    ]
