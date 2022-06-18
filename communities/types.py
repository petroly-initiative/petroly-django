from typing import Optional, List
from enum import Enum

from strawberry import ID, auto, UNSET
from strawberry.types import Info
from strawberry.file_uploads import Upload
from strawberry_django_plus import gql
from strawberry_django.filters import FilterLookup

from django.db.models import Count
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _


from . import models
from account.types import UserType


@gql.enum
class CategoryEnum(Enum):
    EDU = "edu"
    SEC = "section"
    ENT = "entertaining"


@gql.django.filter(models.Community, lookups=True)
class CommunityFilter:
    name: auto
    category: auto
    platform: auto
    section: auto


@gql.django.input(models.Community)
class CommunityInput:
    pk: ID
    name: auto
    description: auto
    link: auto
    date: auto
    category: auto
    platform: auto
    section: auto
    verified: auto
    archived: auto
    icon: Optional[str]
    likes: Optional[List[UserType]]


@gql.django.input(models.Community, partial=True)
class CommunityPartialInput:
    pk: ID


@gql.django.type(models.Community, filters=CommunityFilter)
class CommunityType:
    pk: ID
    name: auto
    description: auto
    link: auto
    date: auto
    category: auto
    platform: auto
    section: auto
    verified: auto
    archived: auto
    icon: Optional[str]
    likes: Optional[List[UserType]]
    # owner: Optional[UserType]

    def get_queryset(self, queryset: QuerySet, info: Info, filters, **kw) -> QuerySet:
        # descending order for number of likes
        return (
            models.Community.objects.filter(archived=False)
            .annotate(num_likes=Count("likes"))
            .order_by("-num_likes")
        )


@gql.type
class CommunityInteractionsType:
    """
    This type holds info about user's interactions with a community.
    """

    liked: bool
    reported: bool
