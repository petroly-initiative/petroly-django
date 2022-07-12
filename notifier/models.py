"""
Here are the related models definition for the `notifier` app.

## Models:
    - `Course` model, to abstract and store related info of each corse
    from KFUPM API identify by its `crn`.
        ### Fields:
            - `crn`: a pk
    - `TrackingList` model, to assign each users to what `Course` they are willing to track
        ### Fields:
            - `courses`
            - `user`

    - `NotificationEvent` model, to track the number, channel , and date of the notifications.
        ### Fields:
            - `user`
            - `channel`
            - `sent_on`
"""

from enum import Enum

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from django_choices_field import TextChoicesField


class Course(models.Model):
    """
    It abstracts and store related info of each corse from KFUPM API identify by its `crn`.
    pk: `crn`
    """

    crn = models.CharField(_("CRN"), max_length=5, primary_key=True)


class TrackingList(models.Model):
    """
    It assigns each users to what `Course` they are willing to track.
    pk: django default `id`.
    """

    user = models.OneToOneField(
        User, verbose_name=_("user"), on_delete=models.CASCADE
    )
    courses = models.ManyToManyField(Course, verbose_name=_("courses"))


class NotificationEvent(models.Model):
    """
    It tracks the number, channel , and date of the notifications.
    """

    class ChannelEnum(Enum):
        """Choices of `channel` as Enum"""

        SMS = "sms", _("sms")
        PUSH = "push", _("push")
        EMAIL = "email", _("email")
        WHATSAPP = "whatsapp", _("whatsapp")
        TELEGRAM = "telegram", _("telegram")

    success = models.BooleanField(_("success"), default=True, blank=True)
    channel = TextChoicesField(
        verbose_name=_("channel"), max_length=15, choices_enum=ChannelEnum
    )
    sent_on = models.DateTimeField(
        _("sent on"), auto_now=False, auto_now_add=True
    )
    user = models.ForeignKey(
        User, verbose_name=_("user"), on_delete=models.CASCADE
    )
