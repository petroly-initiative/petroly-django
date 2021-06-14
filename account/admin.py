from django.contrib.admin.filters import BooleanFieldListFilter
from django_email_verification.tests.settings import verified
from django.contrib import admin
from .models import Profile
from django.apps import apps
from graphql_auth.models import UserStatus
from django.contrib.auth.admin import UserAdmin
from graphql_auth.models import UserStatus
from django.core.mail import send_mail
from django.contrib.auth.models import User
# Register your models here.

@admin.decorators.display(description="Verified", boolean=True)
def is_verified(obj):
    return obj.status.verified

@admin.action(description="Send them the message email")
def send_message_email(self, request, queryset):
    with open('./templates/message_email.html', 'r') as f:
        html = f.read()
        for user in queryset:
            send_mail("An pology", message=None, from_email=None, 
                html_message=html, recipient_list=[user.email, ])
            print(user.email)

admin.site.site_title = 'Petroly'
admin.site.index_title = 'Administration'
admin.site.site_header = 'Petroly Administration'
admin.site.login_template = 'registration/login.html'
UserAdmin.list_display = ["username", "email", "is_staff", is_verified, "date_joined"]
UserAdmin.actions += [send_message_email]


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