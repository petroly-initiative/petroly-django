from django.shortcuts import render
from django.http import HttpResponse
from .models import instructor
from django.core.paginator import Paginator
from django.contrib import messages
from .filters import insFilter
from django.views.generic import ListView, DetailView
# Create your views here.





class searchInstructor(ListView):
    model = instructor
    template_name = 'evaluation/instructors.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = insFilter(self.request.GET, queryset=self.get_queryset())
        return context



def search(request):
    
    instructor=instructor.objects.all()
    
       # Pagintion
    myFilter = insFilter(request.GET['q'], queryset=instructor)
    instructor = myFilter.qs 
    context = {'instructors':instructor,	'myFilter':myFilter}
    return render(request,'evaluation/instructors.html',context)

# Create your views here.

def instructors(request):
    context = {
       
    }
  
    return render(request, 'evaluation/instructors.html',context)
