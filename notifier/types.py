"""
This module defines the types pf this `notifier` app
to be used from `schema` module.
"""

from typing import Any, Callable, List, Optional

import strawberry
import strawberry.django
from strawberry import ID, auto
from strawberry.types import Info
from strawberry_django.permissions import DjangoNoPermission, DjangoPermissionExtension
from strawberry_django.utils.typing import UserType

from .models import Course, RegisterCourse, Term, TrackingList


@strawberry.input
class IdInput:
    """General purpose i input type"""

    id: ID


class OwnsObjPerm(DjangoPermissionExtension):
    """
    This is to check users can only modify theirs.
    """

    DEFAULT_ERROR_MESSAGE = "You don't own this Profile."

    def resolve_for_user(
        self, resolver: Callable, user: UserType, *, info: Info, source: Any
    ):
        # another way to access input data
        # info.selected_fields[0].arguments['data']['pk']
        breakpoint()

        pk = resolver.keywords["data"].pk
        if not pk:
            raise ValueError("The field `pk` must be provided.")

        try:
            pk = int(pk)
        except:
            raise ValueError("The field `pk` is not valid.")

        if not Evaluation.objects.filter(pk=pk, user=user).exists():
            raise DjangoNoPermission

        return resolver()


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


@strawberry.django.type(TrackingList, fields="__all__")
class TrackingListType:
    """A type for `TrackingList` model."""

    # id: ID
    # courses: List[CourseInput]


@strawberry.django.type(RegisterCourse)
class RegisterCourseType:
    """
    A type for `RegisterCourse` model.
    """

    id: ID
    strategy: auto
    course: CourseType | None
    with_add: CourseType | None
    with_drop: CourseType | None
    # tracking_list: TrackingListType


@strawberry.django.input(RegisterCourse)
class RegisterCourseInput:
    """
    A type for `RegisterCourse` model.
    """

    id: ID
    strategy: auto
    with_add_crn: str | None
    with_drop_crn: str | None
