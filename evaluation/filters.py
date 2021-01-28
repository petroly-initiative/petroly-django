import django_filters
from .models import instructor
from django_filters import DateFilter, CharFilter


class insFilter(django_filters.FilterSet):

    class Meta:
        model = instructor
        fields = {
            'Name': ['icontains'],
            'department': ['icontains']
        }
