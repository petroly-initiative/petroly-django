from django.contrib import admin
from .models import Profile
from django.apps import apps
from graphql_auth.models import UserStatus
# Register your models here.


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    list_display = ['user', 'major', 'year', 'profile_pic']


# app = apps.get_app_config('graphql_auth')
# for model_name, model in app.models.items():
#     admin.site.register(model)
@admin.register(UserStatus)
class UserStatusAdmin(admin.ModelAdmin):

    list_display = ['user', 'verified', 'archived']
    list_filter = ['verified']