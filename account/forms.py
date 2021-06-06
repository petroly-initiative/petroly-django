from cloudinary import CloudinaryImage
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import models, widgets
from .models import Profile
from cloudinary.forms import CloudinaryFileField, CloudinaryInput
import re



class UserRegistrationForm(UserCreationForm):
    '''
    This form inherits from `UserCreationForm`, to provide the fields, with thier html attrs,
    for register a new user.
    It's useful for creating an `auth.User` object.
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update(
            {"class": "form-control", "placeholder": "example@gamil.com, etc.", "required": "true"}
        )
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Enter your username"}
        )
        self.fields["first_name"].widget.attrs.update(
            {"class": "form-control", "placeholder": "First Name"}
        )
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Enter your password"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Enter your password again"}
        )

    # It was used for requiring a KFUPM eamail address
    def clean_email(self) -> str:
        REGEX = r'^\w+@kfupm.edu.sa$'
        email = self.cleaned_data['email']

        if User.objects.filter(email=email):
            raise forms.ValidationError(
                'The email address is already exist'
                )

        if email and not re.match(REGEX, email):
            # all email addresses are allowed
            # raise forms.ValidationError('You must use a KFUPM email')
            pass

        return email

    class Meta:
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name')



class UserForm(forms.ModelForm):
    '''
    Similar to the class `UserRegistrationForm`, except it has no passowrd fields.
    It's useful for updating an existing `auth.User` object.
    '''

    class Meta:
        model = User
        fields = ("username", "first_name", "email")


class ProfileForm(forms.ModelForm):
    '''
    A form for the additional `UserProfile` fields.
    It's used for updating an existing `Profile` object.
    '''

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["year"].widget.attrs.update({"class": "form-control"})
        self.fields["major"].widget.attrs.update({"class": "form-control", "placeholder": "PHYS, ICS, etc."})
    


    class Meta:
        model = Profile
        fields = ("major", "year", 'profile_pic')

        profile_pic = CloudinaryFileField(
            widget =forms.FileInput(attrs = {"class": "form-control"}), 
            required = False,
            options={
                'tags': "profile_pic",
                'crop': 'limit', 'width': 300, 'height': 300,
                'folder': 'profile_pics',
            }
        )
