from django.urls import path

from . import views

app_name = "evaluation"

urlpatterns = [
    # path('', views.index, name='index'),
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
    path("evaluate/<int:pk>/", views.Evaluate.as_view(), name="evaluate"),
    path("instructor/<int:pk>/", views.InstructorDetailView.as_view(), name="detail"),
]
