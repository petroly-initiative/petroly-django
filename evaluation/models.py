from django.db import models

# Create your models here.
class instructor(models.Model):
    
    Name = models.CharField(max_length=250)
    department = models.CharField(max_length=200)        # Additional fields
    profile_pic = models.ImageField(upload_to='profile_pics', blank=True)

    def __str__(self):
	    return self.Name


class evaluation(models.Model):

    comments = models.CharField(max_length=250)
    Edate= models.DateTimeField(auto_now_add=True, )

    SID = models.CharField(max_length=250)
    IID = models.ForeignKey(instructor, on_delete=models.CASCADE)