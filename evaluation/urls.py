from django.urls import path

from . import views

urlpatterns = [
    # path('', views.index, name='index'),
      path('instructor/', views.searchInstructor.as_view(), name='a'),
]