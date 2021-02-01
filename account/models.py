from django.db import models
from django.contrib.auth.models import User

# Create your models here.
from django.contrib.auth.models import User


class Profile(models.Model):
    '''A general user profile info model that extends `User` fields. '''

    # Connect to the admin User object by on-to-one relation
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Additional fields
    profile_pic = models.ImageField(upload_to='profile_pics', blank=True)

    # For a nice representation for an object
    def __str__(self) -> str:
        return self.user.username