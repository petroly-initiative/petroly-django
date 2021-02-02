from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Profile(models.Model):
    '''A general user profile info model that extends `User` fields. '''

    years = [('OR', 'Orea'), ('FR', 'Freshman')]
    # Connect to the admin User object by on-to-one relation
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Additional fields
    profile_pic = models.ImageField(upload_to='profile_pics', blank=True)
    year = models.CharField(blank=True, max_length=25, choices=years)
    # For a nice representation for an object
    def __str__(self) -> str:
        return self.user.username