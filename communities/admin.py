from django.contrib import admin
from . import models

@admin.register(models.Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ['name', 'verified', 'archived', 'date',
        'owner']
    list_filter = ['verified', 'archived']
    actions = ['make_verified', 'make_unverified', 
        'make_archived']

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
        list_display = ['community', 'reason', 'reporter', 'created_on']
        list_filter = ['reason', 'community']
        # actions = ['make_verified', 'make_unverified', 
        #     'make_archived']