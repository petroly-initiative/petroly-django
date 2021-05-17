from django.urls import path
from . import views
from .schema import schema
from graphene_django.views import GraphQLView

app_name = 'roommate'

urlpatterns = [
    path('list/', views.BidListView.as_view(), name='bid_list'),
    path('detail/<int:pk>/', views.BidDetailView.as_view(), name='bid_detail'),
    path('create/', views.BidCreateView.as_view(), name='bid_create'),
    path('update/<int:pk>', views.BidUpdateView.as_view(), name='bid_update'),
    path('delete/<int:pk>', views.BidDeleteView.as_view(), name='bid_delete'),
    path('graphql/', GraphQLView.as_view(graphiql=True, schema=schema)),
]
