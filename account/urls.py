from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    
    path('', views.IndexView.as_view(), name='index'),
    path('login/', views.RegisterView.as_view(), name='login'),
    path('', include('django.contrib.auth.urls')),
    path('profile/<int:pk>/', views.ProfileDetailView.as_view(), name='profile_detail'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='profile_form'),
    path('email_confirm/', views.ConfirmView.as_view(), name='email_confirm'),
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True))),
    path('activate/<token>', views.ActivateView.as_view(), name='activate')
]