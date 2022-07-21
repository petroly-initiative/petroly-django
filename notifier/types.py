"""
This module defines the types pf this `notifier` app
to be used from `schema` module.
"""

import dataclasses
from typing import List, Any

from strawberry import auto, ID, Private
from strawberry.types import Info
from strawberry_django_plus import gql
from strawberry_django_plus.permissions import ConditionDirective
from strawberry_django_plus.utils.typing import UserType
from graphql.type.definition import GraphQLResolveInfo


from .models import Course, TrackingList, NotificationChannel, Term


@gql.django.type(Term)
class TermType:
    """A type for `Term` model."""

    long: auto
    short: auto

    def get_queryset(self, queryset, info: Info):
        return queryset.filter(
            allowed=True
        )

@gql.django.type(NotificationChannel)
class NotificationChannelType:
    """A type for `NotificationChannel` model."""

    channel: auto


@gql.django.input(NotificationChannel)
class NotificationChannelInput:
    """Am input type for `NotificationChannel` model."""

    channel: auto


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


@gql.django.type(TrackingList)
class TrackingListType:
    """A type for `TrackingList` model."""

    courses: List[CourseType]
    channels: List[NotificationChannelType]


@gql.django.input(TrackingList, partial=True)
class TrackingListInput:
    """An input type for `TrackingList` model."""

    pk: ID
    courses: List[CourseInput]
    # channels: List[NotificationChannelInput]


@dataclasses.dataclass
class MatchIdentity(ConditionDirective):
    """
    This checks wether the provided `pk` field
    which is also user's pk match the logged in user.
    """

    message: Private[str] = "Your identity aren't matching the provided `pk` field."

    def check_condition(
        self, root: Any, info: GraphQLResolveInfo, user: UserType, **kwargs
    ):
        pk = kwargs["input"]["pk"]
        if pk:
            try:
                if int(pk) == user.pk:
                    return True
                return False
            except Exception as exc:
                raise ValueError("The field `pk` is not valid.") from  exc
        raise ValueError("The field `pk` must be provided.")
