from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _


class Offer(models.Model):

    # Basic
    name = models.CharField(_("Name"), max_length=100)
    phone = models.CharField(_("Phone Number"), max_length=100, blank=True, null=True)
    email = models.EmailField(_("Personal Email"), max_length=254, blank=True, null=True)
    user = models.OneToOneField("auth.User", verbose_name=_("User"), on_delete=models.CASCADE)

    # Additional
    smoking  = models.BooleanField(_("Do You Smoke"))
    staying_up = models.BooleanField(_("Do Stay Up Late"))
    sociable = models.BooleanField(_("Sociable Person"))
    temperature = models.CharField(_("Room Temperature You Like"), max_length=50, blank=True, null=True)
    hometown = models.CharField(_("Your Hometown"), max_length=50, blank=True, null=True)
    comment = models.TextField(_("Comment"), blank=True, default='No Comment')

    class Meta:
        verbose_name = _("offer")
        verbose_name_plural = _("offers")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("roommate:offer_update", kwargs={"pk": self.pk})