from django.forms import forms
from .forms import UserRegistrationForm, ProfileForm, UserForm
from .models import Profile, User
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import CreateView, UpdateView, TemplateView, DetailView
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse, reverse_lazy
from cloudinary.uploader import upload
from django.core.mail import send_mail
from django_email_verification import send_email


class IndexView(TemplateView):

    template_name = "index.html"


class RegisterView(LoginView):

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
                return self.form_valid(form)
            else:
                return self.form_invalid(form)

        # For Registering
        elif "register" in request.POST:
            print('>>>1')
            if user_form.is_valid() and profile_form.is_valid():
                new_user = user_form.save(commit=False)
                new_user.is_active= False
                new_user.save()

                new_profile = profile_form.save(commit=False)
                new_profile.user = new_user

                if "profile_pic" in request.FILES:
                    new_profile.profile_pic = request.FILES["profile_pic"]

                new_profile.save()
                print('>>>2')
                try:
                    # Confirmation email
                    # send_mail(
                    #     'THANK YOU!',
                    #     'We welcome you to our community, where we all help one another :)',
                    #     'no-reply@petroly.co',
                    #     [request.POST['email']],
                    #     fail_silently=False,
                    # )
                    send_email(new_user)
                except Exception as e:
                    print(e)
                    User.objects.filter(email=request.POST['email']).delete()
                    return HttpResponse("Unexpected error while sending you an email, please register again")
                print('>>>3')
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
            if request.FILES.get('profile_pic', '') != '':
                upload(
                    request.FILES.get('profile_pic'),
                    folder='profile_pics',
                    public_id=new_user.username,
                    overwrite=True,
                    invalidate=True,
                    transformation=[
                        {'width': 200, 'height': 200, 'gravity': "face", 'crop': "thumb"}
                    ],
                    format='jpg'
                )
            new_profile.save()

            return redirect(reverse("profile_form", kwargs={}))
        else:
            return self.form_invalid(form=form)
