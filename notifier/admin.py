"""
Customization of the admin site for `notifier` app.
"""

from django.contrib import admin

from . import models

admin.site.register(
    [
        models.NotificationEvent,
        models.Status,
    ]
)


def repeats(obj: models.Banner) -> str:
    if obj.scheduler:
        return abs(obj.scheduler.repeats) - 1
    else:
        return "0"


@admin.register(models.BannerEvent)
class BannerEventAdmin(admin.ModelAdmin):
    """
    Custom admin model site for `BannerEvent` model.
    """

    list_display = ["id", "banner", "term", "created_on"]
    list_filter = [
        "term",
    ]
    search_fields = [
        "user__username",
    ]


@admin.register(models.Banner)
class BannerAdmin(admin.ModelAdmin):
    """
    Custom admin model site for `Banner` model.
    """

    list_display = [
        "id",
        "user",
        "active",
        repeats,
        "updated_on",
        "created_on",
    ]
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

    autocomplete_fields = ["user"]
    list_display = ["id", "user", "channels", "updated_on"]
    list_filter = [
        "channels",
    ]
    filter_horizontal = []
    search_fields = [
        "user__username",
    ]


@admin.register(models.RegisterCourse)
class RegisterCourseAdmin(admin.ModelAdmin):
    """
    Custom settings for `RegisterCourse` app in admin site.
    """

    list_display = ["id", "strategy", "tracking_list"]
    list_filter = [
        "strategy",
    ]
    autocomplete_fields = [
        "tracking_list",
        "course",
        "with_add",
        "with_drop",
    ]
    search_fields = [
        "tracking_list__user__username",
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
e   """
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
