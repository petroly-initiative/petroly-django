"""
This module defines the types pf this `notifier` app
to be used from `schema` module.
"""

from typing import List, Optional

from strawberry import auto, ID
from strawberry.scalars import JSON
from strawberry.types import Info
from strawberry_django_plus import gql


from .models import Course, TrackingList, Term


@gql.django.type(Term)
class TermType:
    """A type for `Term` model."""

    long: auto
    short: auto

    def get_queryset(self, info: Info):
        return Term.objects.filter(allowed=True)


@gql.input
class ChannelsInput:
    EMAIL: bool
    TELEGRAM: bool


@gql.type
class ChannelsType:
    SMS: bool
    PUSH: bool
    EMAIL: bool
    WHATSAPP: bool
    TELEGRAM: bool


@gql.input
class PreferencesInput:
    """An input type for `TrackingList`"""

    channels: ChannelsInput
    telegram_id: Optional[str]
    ## added the hash and data check strings as optional params
    hash: Optional[str]
    dataCheckString: Optional[str]

@gql.type
class PreferencesType:
    """A type for `TrackingList` preferences"""

    channels: ChannelsType


@gql.django.type(Course)
class CourseType:
    """A type for `Course` model."""

    crn: auto
    # term: auto
    # department: auto


@gql.django.input(Course)
class CourseInput:
    """A type for `Course` model."""

    crn: auto
    term: auto
    department: auto


@gql.django.input(TrackingList, partial=True)
class TrackingListInput:
    """An input type for `TrackingList` model."""

    pk: ID
    courses: List[CourseInput]
