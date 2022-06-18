import dataclasses
from typing import Optional, List, Any

from strawberry import ID, auto, UNSET, Private
from strawberry.types import Info
from strawberry.file_uploads import Upload
from strawberry_django_plus import gql
from strawberry_django_plus.permissions import ConditionDirective
from graphql.type.definition import GraphQLResolveInfo

from django.db.models import Count
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _

from . import models
from account.types import UserType


@gql.django.filter(models.Community, lookups=True)
class CommunityFilter:
    name: auto
    category: auto
    platform: auto
    section: auto


@gql.django.input(models.Community, partial=True)
class CommunityInput:
    owner: ID
    name: auto
    description: auto
    link: auto
    category: auto
    platform: auto
    section: auto
    icon: Optional[Upload]


@gql.django.input(models.Community, partial=True)
class CommunityPartialInput:
    pk: ID
    name: auto
    description: auto
    link: auto
    category: auto
    platform: auto
    section: auto
    icon: Optional[Upload]


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

    def get_queryset(
        self, queryset: QuerySet, info: Info, filters=None, **kw
    ) -> QuerySet:
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


@dataclasses.dataclass
class MatchIdentity(ConditionDirective):
    """
    This to check wether the provided `pk` match ther logged in user.
    """

    message: Private[str] = "Your identity aren't matching the provided `pk`."

    def check_condition(self, root: Any, info: GraphQLResolveInfo, user: UserType):
        pk = info.variable_values["owner"]
        if pk:
            try:
                if int(pk) == user.pk:
                    return True
                return False
            except:
                raise ValueError("The field `id` is not valid.")
        raise ValueError("The field `id` must be provided.")


@dataclasses.dataclass
class OwnsObjPerm(ConditionDirective):

    message: Private[str] = "You don't own this community."

    def check_condition(self, root: Any, info: GraphQLResolveInfo, user: UserType):
        pk = info.variable_values["pk"] # get community `pk`
        if models.Community.objects.filter(pk=pk, owner=user).exists():
            return True

        return False
