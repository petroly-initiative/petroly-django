import dataclasses
import functools
from typing import Callable, ClassVar, Optional, Any

from strawberry import ID, auto, UNSET, Private
from strawberry.types import Info
from strawberry.file_uploads import Upload
from strawberry_django_plus import gql
from strawberry_django_plus.permissions import ConditionDirective
from strawberry_django_plus.utils.typing import UserType
from graphql.type.definition import GraphQLResolveInfo

from django.db.models import Count
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _
from cloudinary.models import CloudinaryField, CloudinaryResource

from . import models


@gql.django.input(models.Report, partial=True)
class ReportInput:
    pk: ID
    reason: auto
    other_reason: auto


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
    pk: Optional[ID]
    name: auto
    description: auto
    link: auto
    category: auto
    platform: auto
    section: auto
    icon: Optional[Upload]


@gql.type
class CloudinaryType:
    @gql.field
    def url(self: CloudinaryResource) -> str:
        return self.url


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
    icon: Optional[CloudinaryType]
    # likes: Optional[List[UserType]] # replace with likes_count field

    @gql.field
    def likes_count(self: models.Community, info: Info) -> int:
        return self.likes.count()

    def get_queryset(
        self, queryset: QuerySet, filters=None, **kw
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


@dataclasses.dataclass
class OwnsObjPerm(ConditionDirective):

    message: Private[str] = "You don't own this community."

    def check_condition(
        self, root: Any, info: GraphQLResolveInfo, user: UserType, **kwargs
    ):
        pk = kwargs["input"]["pk"]  # get community `pk`
        if models.Community.objects.filter(pk=pk, owner=user).exists():
            return True

        return False


# Example of implementing custom directive; is not courged
from strawberry_django_plus.directives import (
    SchemaDirectiveWithResolver,
    SchemaDirectiveHelper,
)


@dataclasses.dataclass
class CustomDirective(SchemaDirectiveWithResolver):
    """Base auth directive definition."""

    has_resolver: ClassVar = True

    def resolve(
        self,
        helper: SchemaDirectiveHelper,
        _next: Callable,
        root: Any,
        info: GraphQLResolveInfo,
        *args,
        **kwargs,
    ):
        print(kwargs)
        resolver = functools.partial(_next, root, info, *args, **kwargs)

        if callable(resolver):
            resolver = resolver()
        return resolver
