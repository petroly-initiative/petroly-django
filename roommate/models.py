from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _


class Bid(models.Model):

    # Basic
    name = models.CharField(_("Name"), max_length=100)
    phone = models.CharField(_("Phone Number"), max_length=100, blank=True, null=True)
    user = models.OneToOneField("auth.User", verbose_name=_("User"), on_delete=models.CASCADE)

    # Additional
    smoking  = models.BooleanField(_("Do You Smoke"))
    staying_up = models.BooleanField(_("Do Stay Up Late"))
    temperature = models.IntegerField(_("Room Temperature You Like"), blank=True, null=True)
    region = models.CharField(_("Your Hometown"), max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = _("bid")
        verbose_name_plural = _("bids")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("roommate:bid_update", kwargs={"pk": self.pk})