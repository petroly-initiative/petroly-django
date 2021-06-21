from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils.translation import gettext as _


class Group(models.Model):    
    link = models.URLField(_('Link'))
    major = models.CharField(_('Major'), max_length=10)
    course = models.CharField(_('Course'), max_length=10)
    report = models.IntegerField(_('Report'), default=0)
    verified = models.BooleanField(_('Verified'), default=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                            verbose_name=_("User"), default=None)

    def __str__(self):
        return f'{self.course}'

@receiver(post_save, sender=Group)
def create_profile(sender, instance, created, **kwargs):
    if instance.report==6:
        instance.delete()