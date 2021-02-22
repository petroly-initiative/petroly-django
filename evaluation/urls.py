from django.urls import path

from . import views

app_name = "evaluation"

urlpatterns = [
    # path('', views.index, name='index'),
<<<<<<< HEAD
      path('instructor/', views.SearchInstructor.as_view(), name='index'),
      path('instructor/<pk>', views.Evaluate.as_view(), name='index'),
      
]
=======
    path("instructor/", views.SearchInstructor.as_view(), name="index"),
    path(
        "instructor/create/",
        views.InstructorCreateView.as_view(),
        name="instructor_form",
    ),
    path(
        "instructor/<int:pk>/delete",
        views.InstructorDeleteView.as_view(),
        name="instructor_delete",
    ),
]
>>>>>>> 3a3d5321e41203080afa46d29e1a090b5de0e9dc
