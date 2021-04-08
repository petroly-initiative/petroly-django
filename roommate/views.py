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
from django import forms


class BidCreateView(LoginRequiredMixin, CreateView):
    model = Bid
    fields = [
        'name', 'email', 'phone', 'smoking', 'sociable', 
        'staying_up', 'temperature', 'hometown', 'comment'
    ]

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

class BidDeleteView(DeleteView):
    model = Bid
    success_url = reverse_lazy('roommate:bid_list')


class BidUpdateView(UpdateView):
    model = Bid
    fields = [
        'name', 'email', 'phone', 'smoking', 'sociable', 
        'staying_up', 'temperature', 'hometown', 'comment'
    ]


class BidDetailView(DetailView):
    model = Bid


class BidListView(ListView):
    model = Bid
