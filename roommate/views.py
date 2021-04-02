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


class BidCreateView(CreateView):
    model = Bid


class BidDeleteView(DeleteView):
    model = Bid


class BidUpdateView(UpdateView):
    model = Bid


class BidDetailView(DetailView):
    model = Bid


class BidListView(ListView):
    model = Bid
