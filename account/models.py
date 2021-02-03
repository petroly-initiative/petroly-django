from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image

# Create your models here.


class Profile(models.Model):
    '''A general user profile info model that extends `User` fields. '''

    years = [('OR', 'Orea'), 
            ('FR', 'Jabal Orea'),
            ('SP', 'Major Orea'),
            ('SN', 'Training Orea'),
            ('JN', 'Dieing Orea')]
    # Connect to the admin User object by on-to-one relation
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Additional fields
    profile_pic = models.ImageField(upload_to='profile_pics', blank=True, default='')
    year = models.CharField(blank=True, max_length=25, choices=years)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) # saving image first

        if self.profile_pic:
            img = Image.open(self.profile_pic.path) # Open image using self
            new_img = (300, 300)
            img.thumbnail(new_img)
            img.save(self.profile_pic.path)  # saving image at the same path

    def get_absolute_url(self):
        return reverse("profile_detail", kwargs={'pk':self.pk})

    # For a nice representation for an object
    def __str__(self) -> str:
        return '@{}'.format(self.user.username)