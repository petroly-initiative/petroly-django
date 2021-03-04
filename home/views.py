from django.shortcuts import render
from django.views.generic import ListView, TemplateView
from django.http import HttpResponse, HttpResponseRedirect

class IndexView(TemplateView):

    template_name = "home/index.html"
