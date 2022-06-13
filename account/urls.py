from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    
    path('', views.IndexView.as_view(), name='index'),
    path('', include('django.contrib.auth.urls')),
    path('profile/<int:pk>/', views.ProfileDetailView.as_view(), name='profile_detail'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='profile_form'),
    path('email_confirm/', views.ConfirmView.as_view(), name='email_confirm'),
    path('activate/<token>', views.ActivateView.as_view(), name='activate')
]