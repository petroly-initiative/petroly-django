from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

class Question(models.Model):
    body = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    
    
    class Meta:
        ordering = ['-created']
    def __str__(self):
        return f'{self.body}'

 
class Answer(models.Model):
    question = models.ForeignKey(Question,
                             on_delete=models.CASCADE,
                             related_name='answers')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, blank=True, null=True)
    active = models.BooleanField(default=True)
    answers = models.ForeignKey('self', on_delete=models.CASCADE,
                             related_name='answersfor2m', blank=True,null=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f'{self.body}'


class Tag(models.Model):
    question = models.ManyToManyField(Question,
                             related_name='tags')
    
    body = models.TextField()




    def __str__(self):
        return f'{body} tag'


