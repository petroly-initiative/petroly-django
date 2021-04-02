from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _


class RoommateBid(models.Model):
    

    # Basic
    name = models.CharField(_("Name"), max_length=100)
    phone = models.PhoneNumberField(_("Phone Number"))
    user = models.ForeignKey("admin.User", on_delete=models.CASCADE)

    # Additional
    smoking  = models.BooleanField(_("Do You Smoke"))
    staying_up = models.BooleanField(_("Do Stay Up Late"))
    temperature = models.IntegerField(_("Room Temperature You Like"))
    region = models.CharField(_("Your Hometown"), max_length=50)


    class Meta:
        verbose_name = _("roommate_bid")
        verbose_name_plural = _("roommate_bids")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("roommate_bid_detail", kwargs={"pk": self.pk})

