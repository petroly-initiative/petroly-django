from os import name
from django.db import models
from django.db.models import Avg
from django.contrib.auth.models import User
from .data import departments
from cloudinary.models import CloudinaryField
from cloudinary.uploader import upload, upload_image


class Instructor(models.Model):

    name = models.CharField(max_length=250, unique=True)
    department = models.CharField(
        max_length=200, choices=departments
    )  
    # Additional fields
    profile_pic = CloudinaryField(
    default='https://res.cloudinary.com/ammar-faifi/image/upload/v1614377885/icon.jpg',
    blank=True,
    max_length=350,
    )

    def avg(self):
        result = self.evaluation_set.aggregate(
            Avg("grading"),
            Avg("teaching"),
            Avg("personality"),
        )
        try:
            result['grading__avg'] = round(result['grading__avg'])
            result['teaching__avg'] = round(result['teaching__avg'])
            result['personality__avg'] = round(result['personality__avg'])
            result['overall'] = round((result['grading__avg'] + result['teaching__avg'] + result['personality__avg'])/60)
        except:
            for key, value in zip(result):
                value = 0
        return result

    def __str__(self):
        return self.name


class Evaluation(models.Model):

    comments = models.CharField(max_length=250, blank=True)
    Edate = models.DateTimeField(auto_now_add=True)
    grading = models.IntegerField()
    teaching = models.IntegerField()
    personality = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)

    def __str__(self):
        return (
            "user: " + str(self.user.username) + " instructor: " + self.instructor.name
        )

