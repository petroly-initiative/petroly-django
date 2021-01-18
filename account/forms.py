from django import forms
from django.contrib.auth.models import User
from .models import UserProfile


class UserForm(forms.ModelForm):
    '''A form for needed fields from admin `User` class'''

    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("username", 'first_name', 'last_name', 'email', 'password')


class UserProfileForm(forms.ModelForm):
    '''A form for the additional `UserProfile` fields'''
    
    class Meta:
        model = UserProfile
        fields = ("profile_pic",)


class LogInForm(forms.ModelForm):
    '''A Form only for loging in'''
    
    # Fields
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)