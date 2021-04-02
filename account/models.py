from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image
from cloudinary.models import CloudinaryField
from data import departments, years
from django.dispatch import receiver
from django.db.models.signals import pre_save

# Create your models here.


class Profile(models.Model):
    """A general user profile info model that extends `User` fields. """

    # Connect to the admin User object by on-to-one relation
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Additional fields
    profile_pic = CloudinaryField(
        'image', 
        default='https://res.cloudinary.com/ammar-faifi/image/upload/v1614377885/icon.jpg',
        blank=True,
        max_length=350,
    )
    major = models.CharField(default="", max_length=25, choices=departments)
    year = models.CharField(blank=True, max_length=25, choices=years)


    def get_absolute_url(self):
        return reverse("index", kwargs={})

    # For a nice representation for an object
    def __str__(self) -> str:
        return "@{}".format(self.user.username)

# @receiver(pre_save, sender=User)
# def user_to_inactive(sender, instance, created, update_fields, **kwargs):
#     if created:
#         instance.is_active = False