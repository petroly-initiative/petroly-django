# imports for typing
from typing import Any, Dict
from cloudinary import CloudinaryImage
from django.core.signing import BadSignature, SignatureExpired
from django.http.request import HttpRequest

# needed imports
from django import forms
from graphql_auth.constants import Messages
from graphql_auth.exceptions import TokenScopeError, UserAlreadyVerified
from graphql_auth.models import UserStatus
from .forms import UserRegistrationForm, ProfileForm, UserForm
from .models import Profile, User
from django.http import *
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import *
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse, reverse_lazy
from cloudinary.uploader import upload_image
from django.core.mail import send_mail
from django_email_verification import send_email
from django_email_verification.views import verify
from django.contrib.sites.shortcuts import get_current_site
import requests


def upload_image_(img:str, user:User) -> CloudinaryImage:
    return upload_image(
                    img,
                    folder='profile_pics',
                    public_id=user.username,
                    overwrite=True,
                    invalidate=True,
                    transformation=[
                        {'width': 300, 'crop': "limit"}
                    ],
                    format='jpg'
                )

class ActivateView(TemplateView):
    '''
    To mark a :model:`auth.User` as verified, usin GraphQL API.
    Not really needed right now.
    '''

    def get(self, request: HttpRequest, token: str, *args, **kwargs) -> HttpResponse:
        return render(request, 'email_confirm.html')

    def post(self, request: HttpRequest, token: str, *args, **kwargs) -> HttpResponse:
        try:
            UserStatus.verify(token)
            return render(request, 'email_done.html', context={'success':True})
        except UserAlreadyVerified:
            return render(request, 'email_done.html', context={'success':False, 
                "messages":Messages.ALREADY_VERIFIED})
        except SignatureExpired:
            return render(request, 'email_done.html', context={'success':False, 
                "messages":Messages.EXPIRED_TOKEN})
        except (BadSignature, TokenScopeError):
            return render(request, 'email_done.html', context={'success':False, 
                "messages":Messages.INVALID_TOKEN})


class ConfirmView(TemplateView):
    '''
    A view to verifiy an :model:`auth.User` (account).
    '''

    template_name = "email_confirm.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        token = request.GET.get('token', '')
        
        return render(request, ConfirmView.template_name, context={'token':token})

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        token = request.POST.get('token', '')
        try:
            response = verify(request, token)
        except Exception:
            return HttpResponse("""There might be more than one account with the same Email. 
                Contact support@petroly.co to remove the extra ones""")
        return response


class IndexView(TemplateView):
    '''
    Represents the Home page.
    Currently, it's only return a static html file.
    '''

    template_name = "index.html"


class RegisterView(LoginView, forms.Form):
    '''
    All the Login and Registration is done here.
    It uses two forms `UserRegistrationForm` and `ProfileForm` together.
    * Note that the two forms is for the registering, no form for login.
    '''

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        '''Add the two forms to the `context`'''
        
        context = super().get_context_data(**kwargs)

        profile_form = ProfileForm()
        user_form = UserRegistrationForm()
        context.update({"profile_form": profile_form, "user_form": user_form})
        return context

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        '''Redirect user to the index page if there is a user is alreday logged in'''
        
        if request.user.is_active:
            return redirect("index")
        else:
            return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        user_form = UserRegistrationForm(data=request.POST)
        profile_form = ProfileForm(data=request.POST)

        # Handling login functionality
        if "login" in request.POST:
            # get the auth form
            form = self.get_form()
            if form.is_valid():
                # Check wether the user is verified
                user = User.objects.get(username=request.POST.get('username'))
                try:
                    verified = user.status.verified
                except:
                    # For old accounts that has no `Status` object
                    verified = True
                
                if not verified:
                    return render(request, 'registration/login.html', context={'not_verified':True})
                return self.form_valid(form)
            else:
                return self.form_invalid(form)

        # Handling registration functionality
        elif "register" in request.POST:
            if user_form.is_valid() and profile_form.is_valid():
                # Create the `User` object
                new_user: User = user_form.save()

                # Fill in the `Profile` object, without saving it to the db
                new_user.profile.year = request.POST["year"]
                new_user.profile.major = request.POST["major"]

                if "profile_pic" in request.FILES:
                    new_user.profile.profile_pic = upload_image_(request.FILES["profile_pic"], new_user)
                new_user.profile.save()

                # Send the verification email
                send_email(new_user)
                
                return render(
                    request, "account/register_done.html", {"new_user": new_user}
                )

            else:
                return super().form_invalid(user_form)

        else:
            return super().form_invalid(user_form)


class ProfileDetailView(LoginRequiredMixin, DetailView):
    '''
    To show the :model:`auth.User` instance its info along with :model:`account.Profile` info.
    '''

    model = User
    template_name = "account/profile_detail.html"


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    '''
    Enable users to edit thier info in :model:`auth.User` and :model:`account.Profile`.
    * It has two forms for both objects.
    '''

    model = User
    login_url = "login"
    form_class = UserForm
    form_class2 = ProfileForm
    template_name = "account/profile_form.html"

    def get_object(self, queryset=None) -> User:
        """
        Returns the object the view is displaying.
        By default this requires `self.queryset` and a `pk` or `slug` argument
        in the URLconf, but subclasses can override this to return any object.
        """
        # Use a custom queryset if provided; this is required for subclasses
        # like DateDetailView
        if queryset is None:
            queryset = self.get_queryset()
        # Next, try looking up by primary key.
        pk = self.request.user.pk

        if pk is not None:
            queryset = queryset.filter(pk=pk)

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(
                ("No %(verbose_name)s found matching the query")
                % {"verbose_name": queryset.model._meta.verbose_name}
            )
        return obj

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        '''Add our two forms'''
        context = super().get_context_data(**kwargs)

        # Try to fill the form instances if there're data
        if "form" not in context:
            context["form"] = self.form_class(instance=self.request.user)

        if "form2" not in context:
            context["form2"] = self.form_class2(instance=self.request.user.profile)

        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()

        form = self.get_form(self.form_class)
        form2 = self.get_form(self.form_class2)
        form2.instance = request.user.profile

        if form.is_valid() and form2.is_valid():
            cd = form.cleaned_data
            new_user = form.save(commit=False)
            new_user.save()

            new_profile = form2.save(commit=False)
            new_profile.user = new_user

            # Handling three cases: (1)a pic is given, (2)no pic is given, 
            # or (3)ask to clean the prev pic
            if img := request.FILES.get('profile_pic'):
                new_profile.profile_pic = upload_image_(img, new_user)
            elif 'profile_pic-clear' in request.POST:
                new_profile.profile_pic = None
            else:
                # insert the old profile_pic
                new_profile.profile_pic = Profile.objects.get(user=request.user).profile_pic
            new_profile.save()

            # Back to the same page
            return redirect(reverse("profile_form", kwargs={}))
        else:
            return self.form_invalid(form=form)
