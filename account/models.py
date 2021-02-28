from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image
from cloudinary.models import CloudinaryField

# Create your models here.


class Profile(models.Model):
    """A general user profile info model that extends `User` fields. """

    years = [
        ("OR", "Orea"),
        ("FR", "Jabal Orea"),
        ("SP", "Major Orea"),
        ("SN", "Training Orea"),
        ("JN", "Dieing Orea"),
    ]
    # Connect to the admin User object by on-to-one relation
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Additional fields
    profile_pic = CloudinaryField(
        'image', 
        default='https://res.cloudinary.com/ammar-faifi/image/upload/v1614377885/icon.jpg',
        blank=True,
        max_length=350,
    )
    major = models.CharField(default="", max_length=25)
    year = models.CharField(blank=True, max_length=25, choices=years)


    def get_absolute_url(self):
        return reverse("index", kwargs={})

    # For a nice representation for an object
    def __str__(self) -> str:
        return "@{}".format(self.user.username)

