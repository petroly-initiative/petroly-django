from django.contrib import admin
from .models import Instructor, Evaluation

@admin.register(Evaluation)
class EvaluationAdmmin(admin.ModelAdmin):

    list_display = ['user', 'instructor', 'comment']

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'department']
    list_filter = ['department']