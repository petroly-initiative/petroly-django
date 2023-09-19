from typing import Any, Callable, ClassVar

import strawberry
import strawberry.django
from strawberry.types import Info
from strawberry.file_uploads import Upload
from strawberry import auto, ID, BasePermission
from graphql.type.definition import GraphQLResolveInfo
from strawberry_django.permissions import DjangoNoPermission, DjangoPermissionExtension
from strawberry_django.utils.typing import UserType
from django.contrib.auth import get_user_model

from . import models
import communities.types
import evaluation.types


@strawberry.django.type(model=get_user_model())
# @inject_field({user_pk_field: auto})
class UserType_:
    # gqlauth has a type `UserType`
    pk: ID
    username: auto
    email: auto
    is_superuser: auto
    is_staff: auto
    is_active: auto
    date_joined: auto
    profile: "ProfileType"

    owned_communities: list[communities.types.CommunityType]
    evaluation_set: list[evaluation.types.EvaluationType]

    @strawberry.field
    def owned_communities_count(self) -> int:
        return self.owned_communities.count()

    @strawberry.field
    def evaluation_set_count(self) -> int:
        return self.evaluation_set.count()


@strawberry.django.type(models.Profile)
class ProfileType:
    pk: ID
    user: UserType_
    major: str
    year: str
    language: str
    theme: str

    @strawberry.field
    def profile_pic(self: models.Profile) -> str:
        return self.profile_pic.url

    def get_queryset(self, queryset, info: Info):
        user = info.context.request.user
        if user.is_authenticated:
            return queryset.filter(user=user)
        return None


@strawberry.django.input(models.Profile, partial=True)
class ProfileInput:
    pk: ID
    major: auto
    year: auto
    language: auto
    theme: auto


@strawberry.input
class FileInput:
    file: Upload


@strawberry.type
class ProfilePicUpdateType:
    success: bool
    profile_pic: str


class OwnsObjPerm(DjangoPermissionExtension):
    DEFAULT_ERROR_MESSAGE = "You don't own this Profile."

    def resolve_for_user(
        self, resolver: Callable, user: UserType, *, info: Info, source: Any
    ):
        # another way to access input data
        # info.selected_fields[0].arguments['data']['pk']

        pk = resolver.keywords["data"].pk
        if not pk:
            raise ValueError("The field `p` must be provided.")

        try:
            pk = int(pk)
        except:
            raise ValueError("The field `pk` is not valid.")

        if user.profile.pk != pk:
            raise DjangoNoPermission

        return resolver()
