from django.contrib import admin
from . import models

@admin.register(models.Community)
class CommunityAdmin(admin.ModelAdmin):
    ordering = ['date',]
    list_display = ['name', 'verified', 'archived', 'date',
        'owner']
    list_filter = ['verified', 'archived']
    actions = ['make_verified', 'make_unverified', 
        'make_archived']
    search_fields = ['name']

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
        ordering = ['created_on',]
        list_display = ['community', 'reason', 'reporter', 'created_on']
        list_filter = ['reason']
        search_fields = ['community']