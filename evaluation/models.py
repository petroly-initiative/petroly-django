from django.db import models

# Create your models here.
class instructor(models.Model):

    Name = models.CharField(max_length=250)
        # Additional fields
    profile_pic = models.ImageField(upload_to='profile_pics', blank=True)

class evaluation(models.Model):

    comments = models.CharField(max_length=250)
    Edate= models.DateTimeField(auto_now_add=True, )

    SID = models.CharField(max_length=250)
    # IID = models.ForeignKey(max_length=250)