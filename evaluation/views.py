from django.shortcuts import redirect, render, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls.base import reverse_lazy, reverse
from .models import Instructor, Evaluation
from .filters import InstructorFilter
from django.urls import reverse
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    View,
    DeleteView,
)
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


class SearchInstructor(ListView):
    model = Instructor
    template_name = "evaluation/index.html"
    fields = [
        "name",
        "department",
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = InstructorFilter(self.request.GET, queryset=self.get_queryset())

        return context


class Evaluate(UpdateView):

    model = Instructor

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        rating_1 = int(request.POST["rating"]) * 20
        rating_2 = int(request.POST["ratingtwo"]) * 20
        rating_3 = int(request.POST["ratingthree"]) * 20
        comment = request.POST["comment"]

        rating = Evaluation.objects.create(
            comments=comment,
            grading=rating_1,
            teaching=rating_2,
            personality=rating_3,
            user=request.user,
            instructor=self.object,
        )

        messages.success(request, "Evaluation Was Submitted.")
        return redirect(reverse("evaluation:detail", kwargs={"pk": self.object.pk}))


class InstructorCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):

    permission_required = ["evaluation.add_instructor"]
    model = Instructor
    fields = ["name", "department", "profile_pic"]
    success_url = reverse_lazy("evaluation:index")
    success_message = "The instructor was added"


class InstructorDeleteView(PermissionRequiredMixin, DeleteView):

    permission_required = ["evaluation.delete_instructor"]
    permission_denied_message = "403; You do not have the permission :("
    raise_exception = True
    model = Instructor
    success_url = reverse_lazy("evaluation:index")


class InstructorDetailView(DetailView):
    
    model = Instructor
