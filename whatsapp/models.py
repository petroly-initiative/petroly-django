from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Group(models.Model):    
    link = models.TextField()
    major = models.TextField()
    course = models.TextField()
    report = models.IntegerField(default=0)
    verified = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.course}'

@receiver(post_save, sender=Group)
def create_profile(sender, instance, created, **kwargs):
    if instance.report==6:
        instance.delete()
