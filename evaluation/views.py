# imports for typing
from typing import Any, Dict, Optional
from cloudinary import CloudinaryImage

# neened imports
from django.shortcuts import redirect, render, get_object_or_404
from django.http import *
from django.urls import reverse_lazy, reverse
from .models import Instructor, Evaluation
from .filters import InstructorFilter
from django.urls import reverse
from django.views.generic import *
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.mixins import *
from data import departments
from cloudinary.uploader import upload_image

# for uploading image with resizing
def upload_image_(img: str, name: str) -> CloudinaryImage:
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
    '''
    To display all :model:`evaluation.Instructor` that pass applied search, with paginator.
    It filters the :model:`evaluation.Instructor` using two inputs: name and department.
    '''

    model = Instructor
    paginate_by = 40

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        # get the search inputs from GET/url
        name = self.request.GET.get("name__icontains", default="")
        department = self.request.GET.get("department", default="")

        # filter the Instructor queryset
        filter_qs = InstructorFilter(self.request.GET, Instructor.objects.all().order_by('name'))
        context = super().get_context_data(**kwargs, object_list = filter_qs.qs)
        # departments list for the selector inout
        context['departments'] = departments 
        # these are to keep track of which page the paginator should be applied
        context['selected_department'] = department
        context['selected_name'] = name
        context['selected_search'] = f"name__icontains={name}&department={department}"

        return context


class Evaluate(LoginRequiredMixin, UpdateView):
    '''
    This view to handle POST request for evaluation
    '''

    model = Instructor

    # for GET request redirect to detail page for that instructor
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        pk = self.kwargs.get('pk')
        return redirect('evaluation:instructor_detail', kwargs={'pk':pk})

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()

        # Check first if this user has already evaluated this instructor
        # and return a message. This case is handled in the template
        if Evaluation.objects.filter(user=request.user, instructor=self.object):
            messages.success(request, """You have RATED this instructor before, 
                click `My Evaluations` from your profile to edit it""")
            return redirect(reverse("evaluation:instructor_detail", kwargs={"pk": self.object.pk}))
        
        # Get all data from POST request and create Evaluation object
        data = {
            'grading': int(request.POST.get("rating", 0)) * 20,
            'teaching': int(request.POST.get("ratingtwo", 0)) * 20,
            'personality': int(request.POST.get("ratingthree", 0)) * 20,
            'course': request.POST["course"],
            'comment': request.POST["comment"],
            'user':request.user,
            'instructor':self.object,
        }
        Evaluation.objects.create(**data)

        messages.success(request, "Evaluation Was Submitted.")
        return redirect(reverse("evaluation:instructor_detail", kwargs={"pk": self.object.pk}))


class InstructorCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    '''
    To create a new :model:`evaluation.Instructor`
    It requires a permission of `evaluation.add_instructor`
    '''

    permission_required = ["evaluation.add_instructor"]
    model = Instructor
    success_url = reverse_lazy("evaluation:instructors")
    success_message = "The instructor was added"
    fields = ["name", "department", "profile_pic"]

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        
        name = request.POST['name']
        department = request.POST['department']
        file = request.FILES.get('profile_pic')
        profile_pic = None
        
        # If there is no file in FILES keep profile_pic as None
        # to let db to use the default
        if file:
            profile_pic = upload_image_(file, name)
        
        instructor = Instructor.objects.get_or_create(
            name=name, 
            department=department, 
            profile_pic=profile_pic
            )
        
        return HttpResponseRedirect(reverse('evaluation:instructor_detail', kwargs={'pk':instructor[0].pk}))



class InstructorUpdateView(PermissionRequiredMixin, UpdateView):
    '''
    To update an existing :model:`evaluation.Instructor` object.
    '''

    permission_required = ["evaluation.update_instructor"]
    model = Instructor
    fields = ["name", "department", "profile_pic"]

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        name = request.POST['name']
        department = request.POST['department']
        instructor = Instructor.objects.filter(pk=self.kwargs['pk'])

        # three cases: (1)a file is given, (2)ask to clear existing pic,
        # or(3) update the profile_pic with new one
        if file := request.FILES.get('profile_pic'):
            profile_pic = upload_image_(file, name)
            instructor.update(name=name, department=department, profile_pic=profile_pic)
        elif 'profile_pic-clear' in request.POST:
            instructor.update(name=name, department=department, profile_pic=None)
        else:
            instructor.update(name=name, department=department)

        return HttpResponseRedirect(reverse('evaluation:instructor_detail', kwargs={'pk':instructor[0].pk}))


class InstructorDeleteView(PermissionRequiredMixin, DeleteView):
    '''
    To delete a :model:`evaluation.Instructor` object.
    It requires permission of `evaluation.delete_instructor`.
    '''

    permission_required = ["evaluation.delete_instructor"]
    permission_denied_message = "403; You do not have the permission :("
    raise_exception = True
    model = Instructor
    success_url = reverse_lazy("evaluation:index")


class InstructorDetailView(DetailView):
    '''
    To show all info about a :model:`evaluation.Instructor` object.
    If the user is logged in and has evaluated this instructor, return `evaluated` varible
    to the template to handle this case there.
    '''

    model = Instructor

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        if Evaluation.objects.filter(instructor__pk=self.kwargs['pk'], user__pk=self.request.user.pk):
            context['evaluated'] = True
        else:
            context['evaluated'] = False
        
        return context


class EvaluationListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    '''
    If a user is logged in return all its :model:`evaluation.Evalusiton` objects, 
    with paginator in which 10 objects for each page.
    '''

    model = Evaluation
    paginate_by = 10
    ordering = 'date'

    def test_func(self) -> Optional[bool]:
        '''Prevent accessing other users' evaluations'''
        return int(self.kwargs.get('pk')) == self.request.user.pk

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        pk = self.kwargs.get('pk')
        return super().get_context_data(object_list=Evaluation.objects.filter(user__pk=pk), **kwargs)


class EvaluationUpdateView(UpdateView):
    '''
    Enable users to update their :model:`evaluation.Evaluation` objects.
    '''

    model = Evaluation
    fields = ["grading", "teaching", "personality", "comment"]

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        evaluation = Evaluation.objects.filter(pk=self.object.pk)

        # get the criterion values, if no star is slected use the old one
        # Note the 5 stars are sotored as 100, calculations is needed
        data = {
            'grading': int(request.POST.get("rating", evaluation[0].grading//20)) * 20,
            'teaching': int(request.POST.get("ratingtwo", evaluation[0].teaching//20)) * 20,
            'personality': int(request.POST.get("ratingthree", evaluation[0].personality//20)) * 20,
            'course': request.POST["course"],
            'comment': request.POST["comment"],
        }        
        evaluation.update(**data)

        messages.success(request, "Evaluation Was Updated.")
        return redirect(reverse("evaluation:evaluation_list", kwargs={"pk": request.user.pk}))

class EvaluationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    '''
    To delete a :modle:`evaluation.Evaluation` object.
    '''

    model = Evaluation
    success_url = reverse_lazy("evaluation:instructors")

    # Before delete an evaluation check wether this user own it or not
    def test_func(self) -> Optional[bool]:
        user_pk = self.request.user.pk
        evaluation_pk = int(self.kwargs.get('pk'))
        return Evaluation.objects.get(pk=evaluation_pk).user.pk == user_pk

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        super().post(request, *args, **kwargs)

        messages.success(request, "Evaluation Was Deleted.")
        return redirect(reverse("evaluation:evaluation_list", kwargs={"pk": request.user.pk}))