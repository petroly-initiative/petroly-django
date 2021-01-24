from django import forms
from django.contrib.auth.models import User
<<<<<<< HEAD
from .models import Profile

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password',
                               widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password',
                                widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']
=======
from .models import UserProfile


class UserForm(forms.ModelForm):
    '''A form for needed fields from admin `User` class'''

    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("username", 'first_name', 'last_name', 'email', 'password')
>>>>>>> 0589f45200456000b660104ddbd72274b5c20252


class UserProfileForm(forms.ModelForm):
    '''A form for the additional `UserProfile` fields'''
    
    class Meta:
<<<<<<< HEAD
        model = Profile
        fields = ("profile_pic",)
=======
        model = UserProfile
        fields = ("profile_pic",)


class LogInForm(forms.ModelForm):
    '''A Form only for loging in'''
    
    # Fields
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
>>>>>>> 0589f45200456000b660104ddbd72274b5c20252
