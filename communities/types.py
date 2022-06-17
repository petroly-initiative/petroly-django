from typing import Optional, List
from enum import Enum

import strawberry
import strawberry_django

from strawberry import ID, auto
from strawberry.types import Info
from strawberry_django_plus import gql
from strawberry_django.filters import FilterLookup

from django.db.models.query import QuerySet

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

@gql.django.type(models.Community, filters=CommunityFilter)
class CommunityType:
    id: ID
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
    owner: Optional[UserType]

    def get_queryset(self, queryset:QuerySet, info:Info, filters, **kw):
        return queryset.filter(archived=False)
