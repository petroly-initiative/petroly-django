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

import os

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from django_choices_field import TextChoicesField
from django.utils.timezone import timedelta, now
from django_q.tasks import async_task
from multiselectfield import MultiSelectField

from data import DepartmentEnum

User = get_user_model()


class Cache(models.Model):
    """
    This is a simple in-DB cache,

    that has:
    - `updated_on` is when the last update for the data.
    - `data` is a JSON field to store the actual data.
    - `age` number of seconds until the data is invalid.
    - `stale` True indicating new data is being fetch.
    - `swr` number of seconds until the next request
        pass the cache while new data is being fetched.
    """

    updated_on = models.DateTimeField(_("updated on"), auto_now_add=True)
    stale = models.BooleanField(_("stale"), default=False)

    data = models.JSONField(_("data"), null=True)
    department = models.CharField(_("department"), max_length=7)
    term = models.CharField(_("term"), max_length=7)

    class Meta:
        verbose_name = _("cache item")
        verbose_name_plural = _("cache items")

    def is_valid(self) -> bool:
        """Wether the data has exceeded its age
        default to 5 mins"""
        return now() <= self.updated_on + timedelta(
            seconds=int(os.environ.get("CACHE_AGE", 60 * 5))
        )

    def passed_swr(self) -> bool:
        """Wether the data has exceeded `swr` seconds
        default to 6 min"""
        return now() > self.updated_on + timedelta(
            seconds=int(os.environ.get("CACHE_SWR", 60 * 6))
        )

    def get_data(self) -> dict:
        """This check the age of date
        and triggers fetch for new data if `stale` is False"""

        if self.is_valid():
            return self.data

        if not self.stale:
            # call async to update from API
            self.stale = True
            self.save()
            async_task(
                "notifier.utils.request_data",
                self.term,
                self.department,
                task_name=f"request-data-{self.term}-{self.department}",
                group='request_data',
            )

        return self.data

    def __str__(self) -> str:
        return str(self.id)


class Term(models.Model):
    """
    A small model to store the allowed terms
    to be used in the notifier methods.
    """

    long = models.CharField(_("long"), max_length=10)
    short = models.CharField(_("short"), max_length=5)
    allowed = models.BooleanField(_("allowed"))

    class Meta:
        verbose_name = _("term")
        verbose_name_plural = _("terms")

    def __str__(self):
        return self.long


class Course(models.Model):
    """
    It abstracts and store related info of each corse from KFUPM API identify by its `crn`.
    pk: `crn`
    """

    crn = models.CharField(_("CRN"), max_length=5, unique=True)
    term = models.CharField(_("term"), max_length=6)
    created_on = models.DateTimeField(_("created on"), auto_now_add=True)
    last_updated = models.DateTimeField(_("last updated"), auto_now=True)
    available_seats = models.IntegerField(_("available seats"), default=0)
    raw = models.JSONField(_("raw info"), default=None, null=True)
    waiting_list_count = models.IntegerField(
        _("waiting list count"), default=0
    )
    department = TextChoicesField(
        verbose_name=_("department"), choices_enum=DepartmentEnum
    )

    class Meta:
        ordering = ["term", "department"]

    def __str__(self) -> str:
        return str(self.crn)


class ChannelEnum(models.TextChoices):
    """Choices of `channel` as Enum"""

    SMS = "sms", _("sms")
    PUSH = "push", _("push")
    EMAIL = "email", _("email")
    WHATSAPP = "whatsapp", _("whatsapp")
    TELEGRAM = "telegram", _("telegram")


class TrackingList(models.Model):
    """
    It assigns each users to what `Course` they are willing to track.
    pk: OneToOneField `user`.
    """

    user = models.OneToOneField(
        User,
        verbose_name=_("user"),
        on_delete=models.CASCADE,
        related_name="tracking_list",
    )
    courses = models.ManyToManyField(
        Course,
        verbose_name=_("courses"),
        related_name="tracked_courses",
        blank=True,
    )
    channels = MultiSelectField(
        choices=ChannelEnum.choices, default=ChannelEnum.EMAIL
    )


class NotificationEvent(models.Model):
    """
    It tracks the number, channels, and date of the sent notifications.
    """

    success = models.BooleanField(_("success"), default=True, blank=True)
    sent_on = models.DateTimeField(
        _("sent on"), auto_now=False, auto_now_add=True
    )
    course = models.ForeignKey(
        Course, verbose_name=_("course"), on_delete=models.CASCADE
    )
    to = models.ForeignKey(
        User, verbose_name=_("user"), on_delete=models.CASCADE
    )
    channel = models.CharField(
        _("channel"), max_length=50, choices=ChannelEnum.choices
    )
