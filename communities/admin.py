from django.contrib import admin
from . import models


@admin.register(models.Community)
class CommunityAdmin(admin.ModelAdmin):
    ordering = [
        "date",
    ]
    date_hierarchy = "date"
    list_display = ["name", "verified", "archived", "date", "owner"]
    list_filter = ["verified", "archived", "category"]
    actions = ["make_verified", "make_unverified", "make_archived", "make_unarchived"]
    search_fields = ["name"]
    filter_horizontal = [
        "likes",
    ]

    def make_ammar_owner(self, request, queryset):
        queryset.update(owner=9)

    def make_verified(self, request, queryset):
        queryset.update(verified=True)

    def make_unverified(self, request, queryset):
        queryset.update(verified=False)

    def make_archived(self, request, queryset):
        queryset.update(archived=True)

    def make_unarchived(self, request, queryset):
        queryset.update(archived=False)


@admin.register(models.Report)
class ReportAdmin(admin.ModelAdmin):
    # actions = []
    ordering = [
        "created_on",
    ]
    date_hierarchy = "created_on"
    list_display = ["community", "reason", "reporter", "created_on"]
    list_filter = ["reason"]
    search_fields = ["community"]
