from django.urls import path
from . import views
from .schema import schema

app_name = 'roommate'

urlpatterns = [
    path('list/', views.OfferListView.as_view(), name='offer_list'),
    path('detail/<int:pk>/', views.OfferDetailView.as_view(), name='offer_detail'),
    path('create/', views.OfferCreateView.as_view(), name='offer_create'),
    path('update/<int:pk>', views.OfferUpdateView.as_view(), name='offer_update'),
    path('delete/<int:pk>', views.OfferDeleteView.as_view(), name='offer_delete'),
]
