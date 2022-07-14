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


from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from django_choices_field import TextChoicesField

from data import DepartmentEnum


class NotificationChannel(models.Model):
    """
    This model to help choosing multiple channels for a tracking list.

    pk: django default `id`.
    """

    class ChannelEnum(models.TextChoices):
        """Choices of `channel` as Enum"""

        SMS = "sms", _("sms")
        PUSH = "push", _("push")
        EMAIL = "email", _("email")
        WHATSAPP = "whatsapp", _("whatsapp")
        TELEGRAM = "telegram", _("telegram")

    channel = TextChoicesField(
        verbose_name=_("channel"), max_length=15, choices_enum=ChannelEnum
    )

    class Meta:
        verbose_name = _("notification channel")
        verbose_name_plural = _("notification channels")

    def __str__(self):
        return str(self.channel)


class Course(models.Model):
    """
    It abstracts and store related info of each corse from KFUPM API identify by its `crn`.
    pk: `crn`
    """

    crn = models.CharField(_("CRN"), max_length=5, unique=True)
    term = models.CharField(_("term"), max_length=6)
    department = TextChoicesField(
        verbose_name=_("department"), choices_enum=DepartmentEnum
    )

    class Meta:
        ordering = ["term", "department"]

    def __str__(self) -> str:
        return f"CRN: {self.crn}"


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
    channels = models.ManyToManyField(
        NotificationChannel, verbose_name=_("channels")
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
    channel = models.ForeignKey(
        NotificationChannel,
        verbose_name=_("channel"),
        on_delete=models.CASCADE,
    )
