"""
This module defines the types pf this `notifier` app
to be used from `schema` module.
"""

from typing import List, Optional

import strawberry
import strawberry.django
from strawberry import auto, ID
from strawberry.types import Info

from .models import Course, TrackingList, Term


@strawberry.django.type(Term)
class TermType:
    """A type for `Term` model."""

    long: auto
    short: auto

    def get_queryset(self, info: Info):
        return Term.objects.filter(allowed=True)


@strawberry.input
class ChannelsInput:
    EMAIL: bool
    TELEGRAM: bool


@strawberry.type
class ChannelsType:
    SMS: bool
    PUSH: bool
    EMAIL: bool
    WHATSAPP: bool
    TELEGRAM: bool


@strawberry.input
class PreferencesInput:
    """An input type for `TrackingList`"""

    channels: ChannelsInput
    telegram_id: Optional[str]
    ## added the hash and data check strings as optional params
    hash: Optional[str]
    dataCheckString: Optional[str]

@strawberry.type
class PreferencesType:
    """A type for `TrackingList` preferences"""

    channels: ChannelsType


@strawberry.django.type(Course)
class CourseType:
    """A type for `Course` model."""

    crn: auto
    # term: auto
    # department: auto


@strawberry.django.input(Course)
class CourseInput:
    """A type for `Course` model."""

    crn: auto
    term: auto
    department: auto


@strawberry.django.input(TrackingList, partial=True)
class TrackingListInput:
    """An input type for `TrackingList` model."""

    pk: ID
    courses: List[CourseInput]
