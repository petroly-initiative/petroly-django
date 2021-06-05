from django.shortcuts import redirect, render, get_object_or_404
from django.http import *
from django.urls.base import reverse_lazy, reverse
from django.views.generic.base import TemplateView
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
from data import departments
from cloudinary.uploader import upload_image


def upload_image_(img, name):
    return upload_image(
                    file=img,
                    folder='instructors/profile_pics',
                    public_id=name,
                    overwrite=True,
                    invalidate=True,
                    transformation=[
                        {'width': 300, 'crop': "limit"}
                    ],
                    format='jpg'
                )

class InstructorListView(ListView):

    model = Instructor
    paginate_by = 40

    def get_context_data(self, **kwargs):
        name = self.request.GET.get("name__icontains", default="")
        department = self.request.GET.get("department", default="")

        filter_qs = InstructorFilter(self.request.GET, Instructor.objects.all().order_by('name'))
        context = super().get_context_data(**kwargs, object_list = filter_qs.qs)
        context['departments'] = departments
        context['selected_department'] = department
        context['selected_name'] = name
        context['selected_search'] = f"name__icontains={name}&department={department}"

        return context


class Evaluate(LoginRequiredMixin, UpdateView):

    model = Instructor

    def get(self, request, *args, **kwargs) -> HttpResponse:
        pk = self.kwargs.get('pk')
        return HttpResponseRedirect(reverse('evaluation:instructor_detail', kwargs={'pk':pk}))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if Evaluation.objects.filter(user=request.user, instructor=self.object):
            messages.success(request, """You have RATED this instructor before, 
                click `My Evaluations` from your profile to edit it""")
            return redirect(reverse("evaluation:instructor_detail", kwargs={"pk": self.object.pk}))
        
        data = {
            'grading': int(request.POST.get("rating", 0)) * 20,
            'teaching': int(request.POST.get("ratingtwo", 0)) * 20,
            'personality': int(request.POST.get("ratingthree", 0)) * 20,
            'comment': request.POST["comment"],
            'user':request.user,
            'instructor':self.object,
        }
        Evaluation.objects.create(**data)

        messages.success(request, "Evaluation Was Submitted.")
        return redirect(reverse("evaluation:instructor_detail", kwargs={"pk": self.object.pk}))


class InstructorCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):

    permission_required = ["evaluation.add_instructor"]
    model = Instructor
    fields = ["name", "department", "profile_pic"]
    success_url = reverse_lazy("evaluation:instructors")
    success_message = "The instructor was added"

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        
        name = request.POST['name']
        department = request.POST['department']
        profile_pic = upload_image_(request.FILES['profile_pic'], name)
        instructor = Instructor.objects.get_or_create(
            name=name, 
            department=department, 
            profile_pic=profile_pic
            )
        
        return HttpResponseRedirect(reverse('evaluation:instructor_detail', kwargs={'pk':instructor[0].pk}))


class InstructorDeleteView(PermissionRequiredMixin, DeleteView):

    permission_required = ["evaluation.delete_instructor"]
    permission_denied_message = "403; You do not have the permission :("
    raise_exception = True
    model = Instructor
    success_url = reverse_lazy("evaluation:index")


class InstructorDetailView(DetailView):

    model = Instructor

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if Evaluation.objects.filter(instructor__pk=self.kwargs['pk'], user__pk=self.request.user.pk):
            context['evaluated'] = True
        else:
            context['evaluated'] = False
        
        return context


class EvaluationListView(LoginRequiredMixin, ListView):

    model = Evaluation
    paginate_by = 10
    ordering = 'date'

    def get(self, request, *args, **kwargs) -> HttpResponse:
        # Prevent accessing other users' evaluations
        if int(self.kwargs.get('pk')) != self.request.user.pk:
            return HttpResponseForbidden('You have no permission')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        pk = self.kwargs.get('pk')
        return super().get_context_data(object_list=Evaluation.objects.filter(user__pk=pk), **kwargs)


class EvaluationUpdateView(UpdateView):

    model = Evaluation
    fields = ["grading", "teaching", "personality", "comment"]

    def post(self, request, *args, **kwargs):
        # super().post(request, *args, **kwargs)
        print('POST: ', request.POST)
        self.object = self.get_object()
        evaluation = Evaluation.objects.filter(pk=self.object.pk)
        data = {
            'grading': int(request.POST.get("rating", evaluation[0].grading//20)) * 20,
            'teaching': int(request.POST.get("ratingtwo", evaluation[0].teaching//20)) * 20,
            'personality': int(request.POST.get("ratingthree", evaluation[0].personality//20)) * 20,
            'comment': request.POST["comment"],
        }        
        evaluation.update(**data)

        messages.success(request, "Evaluation Was Updated.")
        return redirect(reverse("evaluation:evaluation_list", kwargs={"pk": request.user.pk}))

class EvaluationDeleteView(DeleteView):
    model = Evaluation
    success_url = reverse_lazy("evaluation:instructors")

    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)

        messages.success(request, "Evaluation Was Deleted.")
        return redirect(reverse("evaluation:evaluation_list", kwargs={"pk": request.user.pk}))