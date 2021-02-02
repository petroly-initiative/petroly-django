from django.shortcuts import render
from django.http import HttpResponse
from .forms import  UserRegistrationForm, UserProfileForm
from .models import Profile

# Create your views here.


def index(request):
    return HttpResponse("this is the main page.")
    
def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(
                user_form.cleaned_data['password'])
            # Save the User object
            new_user.save()
            # Create the user profile
            new_profile = Profile.objects.create(user=new_user)

            if 'profile_pic' in request.FILES:
                new_profile.profile_pic = request.FILES['profile_pic']

            new_profile.save()

            return render(request,
                          'account/register_done.html',
                          {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
        profile_form = UserProfileForm()
    return render(request,
                  'account/register.html',
                  {'user_form': user_form,
                  'profile_form': profile_form})