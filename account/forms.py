from cloudinary import CloudinaryImage
import cloudinary
from django import forms
from django.contrib.auth.models import User
from django.forms import models, widgets
from .models import Profile
from cloudinary.forms import CloudinaryFileField, CloudinaryInput


class UserRegistrationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update(
            {"class": "form-control", "placeholder": "201XXXXXX@kfupm.edu.sa", "required": "true"}
        )
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Username"}
        )
        self.fields["first_name"].widget.attrs.update(
            {"class": "form-control", "placeholder": "First Name"}
        )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        ),
    )
    password2 = forms.CharField(
        label="Repeat password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password Again"}
        ),
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "email")

    def clean_password2(self):
        cd = self.cleaned_data
        if cd["password"] != cd["password2"]:
            raise forms.ValidationError("Passwords don't match.")
        return cd["password2"]


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
    

    profile_pic = CloudinaryFileField(
        widget =forms.FileInput(attrs = {"class": "form-control"}), 
        required = False,
        options={
            'tags': "profile_pic",
            'crop': 'limit', 'width': 300, 'height': 300,
        }
    )

    class Meta:
        model = Profile
        fields = ("major", "year")
