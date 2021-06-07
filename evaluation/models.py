from os import name
from django.db import models
from django.db.models import Avg
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from data import departments
from cloudinary.models import CloudinaryField
from cloudinary.uploader import upload, upload_image


class Instructor(models.Model):
    '''
    It constructs the instructor info: name, department, and profile_pic
    It calculates the average values for using in template rendering.
    '''

    name = models.CharField(max_length=250, unique=True)
    department = models.CharField(
        max_length=200, choices=departments
    )  
    # Additional fields
    profile_pic = CloudinaryField(
    default='https://res.cloudinary.com/petroly-initiative/image/upload/v1622359053/profile_pics/blank_profile.png',
    blank=True,
    max_length=350,
    )

    def avg(self):
        '''Uses the Aggregation function `Avg` to find the avg values for each criterion.'''
        
        result = self.evaluation_set.aggregate(
            Avg("grading"),
            Avg("teaching"),
            Avg("personality"),
        )
        try:
            result['grading__avg'] = round(result['grading__avg'])
            result['teaching__avg'] = round(result['teaching__avg'])
            result['personality__avg'] = round(result['personality__avg'])
            # Overall avg in `integer`
            result['overall'] = round((result['grading__avg'] + result['teaching__avg'] + result['personality__avg'])/60)
            # Overall avg in `float`
            result['overall_float'] = round((result['grading__avg'] + result['teaching__avg'] + result['personality__avg'])/60, 1)
        
        # If cannot find the avg, assign 0
        except:
            result['overall'] = result['overall_float'] = 0

        return result

    def __str__(self):
        return self.name


class Evaluation(models.Model):
    '''
    It constructs the evaluation info and criteria. It has a ForeignKey relation to the :model:`evluation.Instructor` to which this 
    evaluation belongs to.
    Also, this model has field for :model:`auth.User` for who is done this evaluation.
    '''

    starts = [(0, "NO star"), (20, "1 star"), (40, "2 stars"), 
    (60, "3 stars"), (80, "4 stars"), (100, "5 stars")]
    comment = models.TextField(_("Comment"), blank=True, default='')
    date = models.DateTimeField(auto_now_add=True)
    # term = models.IntegerField(_("Term"), default="", choices=[(192, 192)])
    
    # course = models.CharField(_("Course"), max_length=50, default="", )
    grading = models.IntegerField(choices=starts, blank=False)
    teaching = models.IntegerField(choices=starts, blank=False)
    personality = models.IntegerField(choices=starts, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)

    def __str__(self):
        return (
            "user: " + str(self.user.username) + " instructor: " + self.instructor.name
        )

