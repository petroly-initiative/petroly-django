from django.urls import path
from . import views
from graphene_django.views import GraphQLView
#from .schema import schema

app_name = "ingredients"

urlpatterns = [
    #path('graphql/', GraphQLView.as_view(graphiql=True, schema=schema)),
]
