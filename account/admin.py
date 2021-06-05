from django_email_verification.tests.settings import verified
from django.contrib import admin
from .models import Profile
from django.apps import apps
from graphql_auth.models import UserStatus
# Register your models here.

admin.site.site_title = 'Petroly'
admin.site.index_title = 'Administration'
admin.site.site_header = 'Petroly Administration'
admin.site.login_template = 'registration/login.html'

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    list_display = ['user', 'major', 'year']


# app = apps.get_app_config('graphql_auth')
# for model_name, model in app.models.items():
#     admin.site.register(model)


@admin.register(UserStatus)
class UserStatusAdmin(admin.ModelAdmin):

    list_display = ['user', 'verified', 'archived']
    list_filter = ['verified']
    actions = ['make_verified', 'make_unverified', 'make_archived', 'make_unarchived']
    
    def make_verified(self, request, queryset):
        queryset.update(verified=True)

    def make_unverified(self, request, queryset):
        queryset.update(verified=False)

    def make_archived(self, request, queryset):
        queryset.update(archived=True)

    def make_unarchived(self, request, queryset):
        queryset.update(archived=False)