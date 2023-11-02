from typing import Callable, Optional, Any

import strawberry
import strawberry.django
from strawberry.types import Info
from strawberry import ID, auto, Private
from strawberry.file_uploads import Upload
from strawberry_django.filters import FilterLookup
from strawberry_django.utils.typing import UserType
from graphql.type.definition import GraphQLResolveInfo
from strawberry_django.permissions import DjangoNoPermission, DjangoPermissionExtension

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


@strawberry.django.filter(models.Community)
class CommunityFilter:
    name: FilterLookup[str] | None
    section: FilterLookup[str] | None
    category: auto
    platform: auto


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

    @classmethod
    def get_queryset(cls, queryset: QuerySet, info: Info, **kwargs):
        # descending order for number of likes
        return (
            queryset.filter(archived=False)
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

    DEFAULT_ERROR_MESSAGE = "Your identity aren't matching the provided `pk`."

    def resolve_for_user(
        self, resolver: Callable, user: UserType, *, info: Info, source: Any
    ):
        pk = resolver.keywords["data"].pk
        if pk:
            try:
                if int(pk) == user.pk:
                    return True
                raise DjangoNoPermission
            except:
                raise ValueError("The field `id` is not valid.")
        raise ValueError("The field `id` must be provided.")


class OwnsObjPerm(DjangoPermissionExtension):
    DEFAULT_ERROR_MESSAGE = "You don't own this community."

    def resolve_for_user(
        self, resolver: Callable, user: UserType, *, info: Info, source: Any
    ):
        pk = resolver.keywords["data"].pk  # get community `pk`
        if models.Community.objects.filter(pk=pk, owner=user).exists():
            return resolver()

        raise DjangoNoPermission
