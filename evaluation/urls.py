from django.urls import path

from . import views

app_name = 'evaluation'

urlpatterns = [
    # path('', views.index, name='index'),
      path('instructor/', views.SearchInstructor.as_view(), name='index'),
      path('instructor/<pk>', views.Evaluate.as_view(), name='index'),
      
]