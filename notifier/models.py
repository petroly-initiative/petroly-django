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

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.timezone import now, timedelta
from django.utils.translation import gettext as _
from django_choices_field import IntegerChoicesField, TextChoicesField
from django_q.models import Schedule
from django_q.tasks import async_task
from multiselectfield import MultiSelectField

from data import SubjectEnum

User = get_user_model()


class StatusEnum(models.TextChoices):
    """Choices of status of API"""

    UP = "up", _("Up")
    DOWN = "down", _("Down")


class Status(models.Model):
    """This model to store the some general status"""

    key = models.CharField(_("key"), max_length=50, unique=True)
    status = models.CharField(_("status"), max_length=10, choices=StatusEnum.choices)

    class Meta:
        verbose_name = _("status")
        verbose_name_plural = _("status")

    @classmethod
    def is_up(cls, key: str) -> bool:
        """Wether the staus with given `key` is
        `StatusEnum.UP`."""

        try:
            return cls.objects.get(key=key).status == StatusEnum.UP

        except:
            return False

    def __str__(self):
        return str(self.key)


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

    def data_default():
        return []

    updated_on = models.DateTimeField(_("updated on"), auto_now_add=True)
    stale = models.BooleanField(_("stale"), default=False)

    data = models.JSONField(_("data"), default=data_default)
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
            if Status.objects.get(key="API").status == StatusEnum.UP:
                # call async to update from API
                self.stale = True
                self.save()
                async_task(
                    "notifier.utils.request_data",
                    self.term,
                    self.department,
                    task_name=f"request-data-{self.term}-{self.department}",
                    group="request_data",
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

    crn = models.CharField(_("CRN"), max_length=5)
    term = models.CharField(_("term"), max_length=6)
    created_on = models.DateTimeField(_("created on"), auto_now_add=True)
    last_updated = models.DateTimeField(_("last updated"), auto_now=True)
    available_seats = models.IntegerField(_("available seats"), default=0)
    raw = models.JSONField(_("raw info"), default=None, null=True)
    waiting_list_count = models.IntegerField(_("waiting list count"), default=0)
    department = TextChoicesField(
        verbose_name=_("department"), choices_enum=SubjectEnum
    )

    class Meta:
        ordering = ["term", "department"]
        constraints = [
            models.UniqueConstraint("crn", "term", name="unique_crn_term"),
        ]

    def __str__(self) -> str:
        return f"{self.crn} - {self.department}"


class ChannelEnum(models.TextChoices):
    """Choices of `channel` as Enum"""

    SMS = "sms", _("sms")
    PUSH = "push", _("push")
    EMAIL = "email", _("email")
    WHATSAPP = "whatsapp", _("whatsapp")
    TELEGRAM = "telegram", _("telegram")


class Banner(models.Model):
    """A model to stores user's Banner session cookies
    and last check to the session health, with djangoQ scheduler."""

    class Meta:
        verbose_name = _("banner")
        verbose_name_plural = _("banners")

    created_on = models.DateTimeField(_("created on"), auto_now_add=True)
    updated_on = models.DateTimeField(_("updated on"), auto_now=True)

    cookies = models.JSONField(("cookies"), null=True, default=None)
    user = models.OneToOneField(User, verbose_name=_("user"), on_delete=models.CASCADE)
    active = models.BooleanField(_("active"), default=False)
    scheduler = models.OneToOneField(
        Schedule, null=True, blank=True, on_delete=models.SET_NULL
    )

    def __str__(self) -> str:
        return str(self.user)


class BannerEvent(models.Model):
    """A model to records any event for register thru Banner."""

    class Meta:
        verbose_name = _("banner event")
        verbose_name_plural = _("banner events")

    created_on = models.DateTimeField(_("created on"), auto_now_add=True)

    result = models.TextField(_("result"), max_length=1000, null=True, blank=True)
    crns = models.TextField(_("crns"), max_length=100)
    term = models.IntegerField(_("term"))
    banner = models.ForeignKey(
        Banner, verbose_name=_("banner"), on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return str(self.banner)


class TrackingList(models.Model):
    """
    It assigns each users to what `Course` they are willing to track.
    pk: OneToOneField `user`.
    """

    updated_on = models.DateTimeField(_("updated on"), auto_now=True)
    user = models.OneToOneField(
        User,
        verbose_name=_("user"),
        on_delete=models.CASCADE,
        related_name="tracking_list",
    )
    channels = MultiSelectField(
        choices=ChannelEnum.choices,
        default=ChannelEnum.EMAIL,
        max_length=100,
    )

    def __str__(self):
        return f"{self.pk} - {self.user}"


class RegisterCourse(models.Model):
    """
    A model to link each course in user's `TrackingList.register_courses`
    with user's preferred strategy in how to register when the section is open.

    This will server also as holder for user's tracked courses.

    man, im still blaming my self for mislabeling `Course` model,
    it should've been named `Section`.
    """

    class Meta:
        verbose_name = _("register course")
        verbose_name_plural = _("register courses")
        constraints = [
            models.UniqueConstraint(
                "tracking_list", "course", name="unique_trackinglist_course"
            ),
        ]

    class RegisterStrategyEnum(models.IntegerChoices):
        OFF = 0, _("off")
        DEFAULT = 1, _("default")
        LINKED_LAB = 2, _("linked lab")
        REPLACE_WITH = 3, _("replace with ")

        # __empty__ = _("off")

    tracking_list = models.ForeignKey(
        TrackingList,
        verbose_name=_("tracking list"),
        on_delete=models.CASCADE,
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name=_("course"),
    )
    strategy = IntegerChoicesField(
        verbose_name=_("strategy"),
        choices_enum=RegisterStrategyEnum,
        default=RegisterStrategyEnum.OFF,
    )
    with_add = models.ForeignKey(
        Course,
        null=True,
        blank=True,
        default=None,
        related_name="+",
        on_delete=models.CASCADE,
        verbose_name=_("with add course"),
    )
    with_drop = models.ForeignKey(
        Course,
        null=True,
        blank=True,
        default=None,
        related_name="+",
        on_delete=models.CASCADE,
        verbose_name=_("with drop course"),
    )
    updated_on = models.DateTimeField(_("updated on"), auto_now=True)

    def make_strategy_off(self) -> None:
        self.strategy = self.RegisterStrategyEnum.OFF
        self.save()

    def __str__(self) -> str:
        return f'{self.id} - {self.course}'


class NotificationEvent(models.Model):
    """
    It tracks the number, channels, and date of the sent notifications.
    """

    success = models.BooleanField(_("success"), default=True, blank=True)
    sent_on = models.DateTimeField(_("sent on"), auto_now=False, auto_now_add=True)
    course = models.ForeignKey(
        Course, verbose_name=_("course"), on_delete=models.CASCADE
    )
    to = models.ForeignKey(User, verbose_name=_("user"), on_delete=models.CASCADE)
    channel = models.CharField(_("channel"), max_length=50, choices=ChannelEnum.choices)
