from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from django_email_verification import urls as email_urls

urlpatterns = [
    
    path('', views.IndexView.as_view(), name='index'),
    path('', include('django.contrib.auth.urls')),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/<int:pk>/', views.ProfileDetailView.as_view(), name='profile_detail'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='profile_form'),
    path('email_confirm/', views.VerifyView.as_view(), name='email_confirm'),
    path('email_verify/', include(email_urls)),

]