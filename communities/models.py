from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Community(models.Model):
    community_categories = (
        ('edu', 'Educational'),
        ('section', 'Section'), # If this choice is chosen, then the field section should be filled. 
        ('entertaining', 'Entertaining'), # could not find a better word :(
    )
    platforms = (
        ('whatsapp', 'Whatsapp'),
        ('discord', 'Discord'),
        ('telegram', 'Telegram'),
    )
    name = models.CharField(_('Name'), max_length = 20)
    description = models.TextField(_('Description'), max_length = 500)
    link = models.URLField(_('Link'))
    platform =  models.CharField(_('Platform'), max_length = 12, choices = platforms)
    category = models.CharField(_('Category'), max_length = 12, choices = community_categories)
    likes = models.IntegerField(_('Likes'), default=0)  
    section = models.CharField(_('Section'), max_length=10, default="") 
    report = models.IntegerField(_('Report'), default=0)
    verified = models.BooleanField(_('Verified'), default=True)
    archived = models.BooleanField(_('Archived'), default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                            verbose_name=_("user"), default=None)

    def __str__(self):
        return f'{self.name} - {self.report}'

@receiver(post_save, sender=Community)
def create_profile(sender, instance, created, **kwargs):
    if instance.report==6:
        instance.delete()
