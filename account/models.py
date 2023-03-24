from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from data import DepartmentEnum, years
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import gettext as _

from cloudinary.models import CloudinaryField
from django_choices_field import TextChoicesField

# Create your models here.


class Profile(models.Model):
    class Meta:
        verbose_name = _("profile")
        verbose_name_plural = _("profiles")

    """
    A general user profile info model that has a field of :model:`auth.User`. 
    """

    # Connect to the admin User object by on-to-one relation
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Additional fields
    profile_pic = CloudinaryField(
        _("profile picture"),
        default="https://res.cloudinary.com/petroly-initiative/image/upload/v1622359053/profile_pics/blank_profile.png",
        blank=True,
        max_length=350,
    )
    major = TextChoicesField(
        blank=True, null=True, max_length=25, choices_enum=DepartmentEnum
    )
    year = models.CharField(blank=True, null=True, max_length=25, choices=years)
    language = models.CharField(_("language"), max_length=10, default="en-US")
    theme = models.CharField(_("theme"), max_length=10, default="light")

    # Some views need this to redirect to a url
    def get_absolute_url(self) -> str:
        return reverse("index", kwargs={})

    # For a nice representation for an object
    def __str__(self) -> str:
        return "Profile: @{}".format(self.user.username)


class UserLog(models.Model):
    """To record user usages helping in
    rate limiting services"""

    class Meta:
        verbose_name = _("user log")
        verbose_name_plural = _("user logs")

    ip = models.GenericIPAddressField(_("IP"))
    function = models.CharField(_("function"), max_length=100)
    created_on = models.DateTimeField(_("created on"), auto_now_add=True)
    updated_on = models.DateTimeField(_("updated on"), auto_now=True)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
