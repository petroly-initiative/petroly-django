from typing import overload
from django.db import models
from django.db.models import Avg
from django.contrib.auth.models import User
from .data import departments


class Instructor(models.Model):

    name = models.CharField(max_length=250, unique=True)
    department = models.CharField(
        max_length=200, choices=departments
    )  
    # Additional fields
    profile_pic = models.ImageField(upload_to="profile_pics", blank=True)

    def avg(self):
        result = self.evaluation_set.aggregate(
            Avg("grading"),
            Avg("teaching"),
            Avg("personality"),
        )
        try:
            result['overall'] = round((result['grading__avg'] + result['teaching__avg'] + result['personality__avg'])/60)
        except:
            result["overall"] = 0
        print(result)
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

