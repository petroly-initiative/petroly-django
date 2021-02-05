from django.http.response import Http404
from .forms import  UserRegistrationForm, ProfileForm, UserForm
from .models import Profile, User
from django.http import HttpResponse, request
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import CreateView, UpdateView, TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
import logging 
logging.basicConfig(filename='request.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Create your views here.


class IndexView(TemplateView):

    template_name = "account/index.html"
    

class RegisterView(CreateView):
    def get(self, request, *args, **kwargs):
        user_form = UserRegistrationForm()
        profile_form = ProfileForm()
        return render(request,
                  'account/register.html',
                  {'user_form': user_form,
                  'profile_form': profile_form})

    def post(self, request, *args, **kwargs):
        user_form = UserRegistrationForm(data=request.POST)
        profile_form = ProfileForm(data=request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()

            new_profile = profile_form.save(commit=False)
            new_profile.user = new_user

            if 'profile_pic' in request.FILES:
                new_profile.profile_pic = request.FILES['profile_pic']

            new_profile.save()
            logging.info('profile: '+str(new_profile.pk))
            logging.info('user: '+str(new_user.pk))

            return render(request,
                            'account/register_done.html',
                            {'new_user': new_user})

        else: return HttpResponse('Erorr while POSTing data')


class ProfileDetailView(LoginRequiredMixin, DetailView):
    
    model = User
    template_name = 'account/profile_detail.html'


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    
    model = User
    login_url = 'login'
    form_class = UserForm
    form_class2 = ProfileForm
    template_name = 'account/profile_form.html'
    
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
            raise Http404(_("No %(verbose_name)s found matching the query") %
                        {'verbose_name': queryset.model._meta.verbose_name})
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'form' not in context:
            context["form"] = self.form_class(instance=self.request.user)
        
        if 'form2' not in context:
            context['form2'] = self.form_class2(instance=self.request.user.profile)
        
        return context

    def post(self, request, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()

        form = self.get_form(self.form_class)
        form2 = self.get_form(self.form_class2)
        form2.instance = request.user.profile
    
        if 'form1' in request.POST:
            logging.info('i got form1')
            logging.info(request.POST)
            print('test')

        if form.is_valid() and form2.is_valid():
            cd = form.cleaned_data
            new_user = form.save(commit=False)
            new_user.save()

            new_profile = form2.save(commit=False)
            new_profile.user = new_user
            new_profile.save()

            print(request.user.pk)
            print(new_user.pk)
            print(new_profile.pk)

            return redirect(reverse('profile_form', kwargs={}))
        else:
            return self.form_invalid(form=form)
