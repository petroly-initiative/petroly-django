from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image
from cloudinary.models import CloudinaryField
from cloudinary import CloudinaryImage
from data import departments, years
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import gettext as _

# Create your models here.


class Profile(models.Model):
    """
    A general user profile info model that has a field of :model:`auth.User`. 
    """

    # Connect to the admin User object by on-to-one relation
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Additional fields
    profile_pic = CloudinaryField(
        'image', 
        default='https://res.cloudinary.com/petroly-initiative/image/upload/v1622359053/profile_pics/blank_profile.png',
        blank=True,
        max_length=350,
    )
    major = models.CharField(blank=False, null=True, max_length=25, choices=departments)
    year = models.CharField(blank=False, null=True, max_length=25, choices=years)
    language = models.CharField(_("language"), max_length=10, default='en-US')

    # Some views need this to redirect to a url
    def get_absolute_url(self) -> str:
        return reverse("index", kwargs={})

    # For a nice representation for an object
    def __str__(self) -> str:
        return "Profile: @{}".format(self.user.username)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)