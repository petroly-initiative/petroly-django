from tabnanny import verbose
from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from cloudinary.models import CloudinaryField

class CloudinaryFieldCostom(CloudinaryField):
    '''
    This is needed to modify to_python, to deal with the FileInput from `graphene`.
    '''
    def to_python(self, value):
        if isinstance(value, dict):
            # ignore it
            pass
        else:
            return super().to_python(value)

class Community(models.Model):
    class Meta:
        verbose_name = _('community')
        verbose_name_plural = _('Communities')
    community_categories = (
        ('edu', _('Educational')),
        ('section', _('Section')), # If this choice is chosen, then the field section should be filled). 
        ('entertaining', _('Entertaining')), # could not find a better word ):(
    )
    platforms = (
        ('whatsapp', _('Whatsapp')),
        ('discord', _('Discord')),
        ('telegram', _('Telegram')),
    )
    name = models.CharField(_('Name'), max_length = 100)
    description = models.TextField(_('Description'), max_length = 500, default='', blank=True)
    link = models.URLField(_('Link')) 
    date = models.DateField(_('Date'), auto_now_add=True)
    platform =  models.CharField(_('Platform'), max_length = 12, choices = platforms)
    category = models.CharField(_('Category'), max_length = 12, choices = community_categories)
    section = models.CharField(_('Section'), max_length=10, default="", blank=True) 
    verified = models.BooleanField(_('Verified'), default=True)
    archived = models.BooleanField(_('Archived'), default=False)
    icon = CloudinaryFieldCostom(_('icon'), default=None, null=True,  blank=True, max_length=350)
    reports = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_("reports"), 
        related_name='reported_communities', blank=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_("likes"), 
        related_name='liked_communities', blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        related_name='owned_communities', verbose_name=_("owner"), null=True)

    def __str__(self):
        return f'{self.name}'

@receiver(m2m_changed, sender=Community.reports.through)
def archive_community(sender, instance, action, **kwargs):
    if action == 'post_add':
        num = instance.reports.count()  # count of reports

        if num >= 2:
            instance.archived = True
            instance.save()
            
