from django.contrib import admin
from .models import Instructor, Evaluation


@admin.register(Evaluation)
class EvaluationAdmmin(admin.ModelAdmin):
    search_fields = ["instructor__name"]
    list_display = ["user", "instructor", "comment", "date"]


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "department"]
    list_filter = ["department"]
