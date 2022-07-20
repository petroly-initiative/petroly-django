from django.db import models



from account.models import Profile
# Create your models here.
class TelegramBotUser(models.Model):
    "A class to represent the link between a django user and the telegram account"
    telegram_user_id = models.CharField(default="", max_length=256);
    telegram_username=  models.CharField(primary_key=True, max_length=256);
    user = models.OneToOneField(Profile, on_delete= models.PROTECT)