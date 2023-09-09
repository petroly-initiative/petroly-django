import dataclasses
import functools
from typing import Callable, ClassVar, Optional, Any

import strawberry
import strawberry.django
from strawberry import ID, auto, Private
from strawberry.types import Info
from strawberry.file_uploads import Upload
from strawberry_django.permissions import DjangoPermissionExtension
from strawberry_django.utils.typing import UserType
from graphql.type.definition import GraphQLResolveInfo

from django.db.models import Count
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _
from cloudinary.models import CloudinaryResource

from . import models


@strawberry.django.input(models.Report, partial=True)
class ReportInput:
    pk: ID
    reason: auto
    other_reason: auto


@strawberry.django.filter(models.Community, lookups=True)
class CommunityFilter:
    name: auto
    category: auto
    platform: auto
    section: auto


@strawberry.django.input(models.Community, partial=True)
class CommunityInput:
    owner: ID
    name: auto
    description: auto
    link: auto
    category: auto
    platform: auto
    section: auto
    icon: Optional[Upload]


@strawberry.django.input(models.Community, partial=True)
class CommunityPartialInput:
    pk: Optional[ID]
    name: auto
    description: auto
    link: auto
    category: auto
    platform: auto
    section: auto
    icon: Optional[Upload]


@strawberry.type
class CloudinaryType:
    @strawberry.field
    def url(self: CloudinaryResource) -> str:
        return self.url


@strawberry.django.type(models.Community, filters=CommunityFilter)
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
    icon: Optional[CloudinaryType]
    # likes: Optional[List[UserType]] # replace with likes_count field

    @strawberry.field
    def likes_count(self: models.Community, info: Info) -> int:
        return self.likes.count()

    def get_queryset(self, queryset: QuerySet, filters=None, **kw) -> QuerySet:
        # descending order for number of likes
        return (
            models.Community.objects.filter(archived=False)
            .annotate(num_likes=Count("likes"))
            .order_by("-num_likes")
        )


@strawberry.type
class CommunityInteractionsType:
    """
    This type holds info about user's interactions with a community.
    """

    liked: bool
    reported: bool


class MatchIdentity(DjangoPermissionExtension):
    """
    This to check wether the provided `pk` match ther logged in user.
    """

    message: Private[str] = "Your identity aren't matching the provided `pk`."

    def resolve_for_user(
        self, resolver: Callable, user: UserType, *, info: Info, source: Any
    ):
        return super().resolve_for_user(resolver, user, info=info, source=source)

    def check_condition(
        self, root: Any, info: GraphQLResolveInfo, user: UserType, **kwargs
    ):
        pk = kwargs["input"]["owner"]
        if pk:
            try:
                if int(pk) == user.pk:
                    return True
                return False
            except:
                raise ValueError("The field `id` is not valid.")
        raise ValueError("The field `id` must be provided.")


class OwnsObjPerm(DjangoPermissionExtension):
    message: Private[str] = "You don't own this community."

    def resolve_for_user(
        self, resolver: Callable, user: UserType, *, info: Info, source: Any
    ):
        return super().resolve_for_user(resolver, user, info=info, source=source)

    def check_condition(
        self, root: Any, info: GraphQLResolveInfo, user: UserType, **kwargs
    ):
        pk = kwargs["input"]["pk"]  # get community `pk`
        if models.Community.objects.filter(pk=pk, owner=user).exists():
            return True

        return False
