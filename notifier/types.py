"""
This module defines the types pf this `notifier` app
to be used from `schema` module.
"""

from strawberry import auto
from strawberry_django_plus import gql

from .models import Course, TrackingList

@gql.django.type(Course)
class CourseType:
    """A type for `Course` model."""

    crn: auto

@gql.django.type(TrackingList)
class TrackingListType:
    """A type for `TrackingList` model."""

    user: auto
    courses: auto
