from django.shortcuts import render
from .models import Bid
from django.views.generic import (
    TemplateView,
    ListView,
    DeleteView,
    DetailView,
    CreateView,
    UpdateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse


class BidCreateView(LoginRequiredMixin, CreateView):
    model = Bid
    fields = [
        'name', 'phone', 'smoking', 
        'staying_up', 'temperature', 'region'
    ]


class BidDeleteView(DeleteView):
    model = Bid
    success_url = reverse_lazy('roommate:bid_list')


class BidUpdateView(UpdateView):
    model = Bid
    fields = [
        'name', 'phone', 'smoking', 
        'staying_up', 'temperature', 'region'
    ]


class BidDetailView(DetailView):
    model = Bid


class BidListView(ListView):
    model = Bid
