from cloudinary import CloudinaryImage
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import models, widgets
from .models import Profile
from cloudinary.forms import CloudinaryFileField, CloudinaryInput
import re



class UserRegistrationForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update(
            {"class": "form-control", "placeholder": "s20xxxxxxx@kfupm.edu.sa", "required": "true"}
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

    def clean_email(self):
        REGEX = r'^\w+@kfupm.edu.sa$'
        email = self.cleaned_data['email']

        if User.objects.filter(email=email):
            raise forms.ValidationError(
                'The email address is already exist'
                )

        if email and not re.match(REGEX, email):
            raise forms.ValidationError('You must use a KFUPM email')

        return email



    class Meta:
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name')



class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "first_name", "email")


class ProfileForm(forms.ModelForm):
    """A form for the additional `UserProfile` fields"""

    def __init__(self, *args, **kwargs):
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
