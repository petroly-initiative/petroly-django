from django.urls import path
from . import views
from graphene_django.views import GraphQLView
from .schema import schema

app_name = "evaluation"

urlpatterns = [
    # path('', views.index, name='index'),
    path("instructors/", views.InstructorListView.as_view(), name="instructors"),
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
    path("my_evaluations/<pk>", views.EvaluationListView.as_view(), name="evaluation_list"),
    path("update/<int:pk>", views.EvaluationUpdateView.as_view(), name="evaluation_form"),
    path('graphql/', GraphQLView.as_view(graphiql=True, schema=schema)),
]
