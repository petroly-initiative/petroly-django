from typing import Any
from django.http import *
from django.shortcuts import redirect, render
from .models import Offer
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


class OfferCreateView(LoginRequiredMixin, CreateView):
    model = Offer
    fields = [
        'name', 'email', 'phone', 'smoking', 'sociable', 
        'staying_up', 'temperature', 'hometown', 'comment'
    ]

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        offer = Offer.objects.filter(user=request.user)
        if offer:
            return redirect('roommate:offer_update', pk=offer[0].pk)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        if 'use-default-email' in self.request.POST:
            self.object.email = self.request.user.email
        self.object.save()
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

class OfferDeleteView(DeleteView):
    model = Offer
    success_url = reverse_lazy('roommate:offer_list')


class OfferUpdateView(UpdateView):
    model = Offer
    fields = [
        'name', 'email', 'phone', 'smoking', 'sociable', 
        'staying_up', 'temperature', 'hometown', 'comment'
    ]


class OfferDetailView(DetailView):
    model = Offer


class OfferListView(ListView):
    model = Offer
