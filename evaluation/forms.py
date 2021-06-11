from django.forms import ModelForm
from .models import Instructor


class insForm(ModelForm):
 	class Meta:
 		model = instructor
 		fields = '__all__'