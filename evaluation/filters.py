import django_filters
from .models import instructor
from django_filters import DateFilter, CharFilter
from django import forms


class insFilter(django_filters.FilterSet):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.filters['Name'].field.widget.attrs.update({'class': '', 'placeholder':'Email'})
    #     self.filters['Name'].

    departments = (
        ('ICS', 'ICS'),
        ('PHYSICS', 'Physics'),
        ('COE', 'COE'),
        ('SWE', 'SWE'),
    )
    # Name = django_filters.CharFilter(label='Name', widget=forms.TextInput(attrs={'class': 'searchbar', 
    #                                                                                 'placeholder':'Search Here !',
                                                                                    # 'style':"padding: 16px;margin: 0px;color: var(--dark);margin-left: 2px;text-align: center;font-size: 1.0rem;border-radius: 0px;height: 41px;"}))
    department = django_filters.ChoiceFilter(label='department', choices=departments)
    class Meta:
        model = instructor
        fields = {
            'Name': ['icontains'],
            
        }
