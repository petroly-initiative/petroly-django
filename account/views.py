from django import forms
from .forms import UserRegistrationForm, ProfileForm, UserForm
from .models import Profile, User
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import CreateView, UpdateView, TemplateView, DetailView
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


def upload_image_(img, user):
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

    def get(self, request, token, *args, **kwargs):
        return render(request, 'email_confirm.html')

    def post(self, request, token, *args, **kwargs):
        url =  'http://' + get_current_site(request).domain + '/account/graphql/'
        payload = '''
            mutation{
                verifyAccount(token:"%s"){
                    success
                    errors
                }
            }
        ''' % token
        r = requests.post(url, json={'query': payload})
        success = r.json()['data']['verifyAccount']['success']
        if r.status_code == 200:
            return render(request, 'email_done.html', context={'success':success})
        else:
            raise Exception(f"Query failed to run with a {r.status_code}.")
            return HttpResponse(r)

class ConfirmView(TemplateView):

    template_name = "email_confirm.html"

    def get(self, request, *args, **kwargs):
        token = request.GET.get('token', '')
        
        return render(request, ConfirmView.template_name, context={'token':token})

    def post(self, request, *args, **kwargs):
        token = request.POST.get('token', '')
        try:
            response = verify(request, token)
        except Exception:
            return HttpResponse("""There are more than one account with the same Email. 
                Contact support@petroly.co to remove the extra ones""")
        return response


class IndexView(TemplateView):

    template_name = "index.html"


class RegisterView(LoginView, forms.Form):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        profile_form = ProfileForm()
        user_form = UserRegistrationForm()
        context.update({"profile_form": profile_form, "user_form": user_form})
        return context

    def get(self, request, *args, **kwargs) -> HttpResponse:
        # Redirect user to the index page if there is a user is alreday logged in
        if request.user.is_active:
            return HttpResponseRedirect(reverse("index"))
        else:
            return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user_form = UserRegistrationForm(data=request.POST)
        profile_form = ProfileForm(data=request.POST)

        # For Login
        if "login" in request.POST:
            # get the auth form
            form = self.get_form()
            if form.is_valid():
                # To check is user verified
                user = User.objects.get(username=request.POST.get('username'))
                try:
                    verified = user.status.verified
                except:
                    # For old accounts
                    verified = True
                
                if not verified:
                    return render(request, 'registration/login.html', context={'not_verified':True})
                return self.form_valid(form)
            else:
                return self.form_invalid(form)

        # For Registering
        elif "register" in request.POST:
            if user_form.is_valid() and profile_form.is_valid():
                new_user = user_form.save()
                new_user.is_active = True
                new_user.save()

                new_profile = profile_form.save(commit=False)
                new_profile.user = new_user

                if "profile_pic" in request.FILES:
                    new_profile.profile_pic = upload_image_(request.FILES["profile_pic"], new_user)

                new_profile.save()

                send_email(new_user)
                
                return render(
                    request, "account/register_done.html", {"new_user": new_user}
                )

            else:
                return super().form_invalid(user_form)

        else:
            return super().form_invalid(user_form)


class ProfileDetailView(LoginRequiredMixin, DetailView):

    model = User
    template_name = "account/profile_detail.html"


class ProfileUpdateView(LoginRequiredMixin, UpdateView):

    model = User
    login_url = "login"
    form_class = UserForm
    form_class2 = ProfileForm
    template_name = "account/profile_form.html"

    def get_object(self, queryset=None):
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if "form" not in context:
            context["form"] = self.form_class(instance=self.request.user)

        if "form2" not in context:
            context["form2"] = self.form_class2(instance=self.request.user.profile)

        return context

    def post(self, request, *args, **kwargs) -> HttpResponse:
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
            if img := request.FILES.get('profile_pic'):
                new_profile.profile_pic = upload_image_(img, new_user)
            elif 'profile_pic-clear' in request.POST:
                new_profile.profile_pic = None
            else:
                # insert the old profile_pic
                new_profile.profile_pic = Profile.objects.get(user=request.user).profile_pic
            new_profile.save()

            return redirect(reverse("profile_form", kwargs={}))
        else:
            return self.form_invalid(form=form)
