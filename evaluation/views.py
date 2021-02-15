from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponse
from .models import instructor, evaluation
from django.core.paginator import Paginator
from django.contrib import messages
from .filters import insFilter
from django.views.generic import ListView, DetailView, CreateView, UpdateView
# Create your views here.


class searchInstructor(ListView):
    model = instructor
    template_name = 'evaluation/index.html'
    fields = [
    'Name', 'department',
    ]
    # search bar
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = insFilter(
            self.request.GET, queryset=self.get_queryset())

        return context

    def get_object(self, queryset=None):
        """
        Returns the object the view is displaying.
        By default this requires `self.queryset` and a `pk` or `slug` argument
        in the URLconf, but subclasses can override this to return any object.
        """
        # Use a custom queryset if provided; this is required for subclasses
        # like DateDetailView
        if queryset is None:
            queryset = self.get_queryset()
        # Next, try looking up by primary key.
        pk = self.request.user

        if pk is not None:
            queryset = queryset.filter(pk=pk)

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(("No %(verbose_name)s found matching the query") %
                        {'verbose_name': queryset.model._meta.verbose_name})
        return obj

    def post(self, request):
        obj = self.get_object()
        rating_1 = int(request.POST['rating'])
        rating_2 = int(request.POST['ratingtwo'])
        rating_3 = int(request.POST['ratingthree'])
        comment = request.POST['comment']
        
        rating =evaluation(comments=comment,grading=rating_1, teaching=rating_2, personality=rating_3, SID=request.user, IID= obj.pk )
        
        
        total = rating_1 + rating_2 + rating_3
        print(ID)
        return HttpResponse()
