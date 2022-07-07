import dataclasses
import strawberry
import strawberry_django
from strawberry import auto, ID, BasePermission, Private
from strawberry.types import Info
from strawberry.file_uploads import Upload
from strawberry_django_plus import gql
from strawberry_django_plus.permissions import ConditionDirective
from graphql.type.definition import GraphQLResolveInfo
from typing import Any

from django.contrib.auth import get_user_model

from . import models
from communities.types import CommunityType
from evaluation.types import EvaluationType


@strawberry.django.type(model=get_user_model())
# @inject_field({user_pk_field: auto})
class UserType:
    pk: ID
    username: auto
    email: auto
    is_superuser: auto
    is_staff: auto
    is_active: auto
    date_joined: auto
    profile: "ProfileType"

    owned_communities: list[CommunityType]
    evaluation_set: list[EvaluationType]

    @gql.field
    def owned_communities_count(self) -> int:
        return self.owned_communities.count()

    @gql.field
    def evaluation_set_count(self) -> int:
        return self.evaluation_set.count()


@gql.django.type(models.Profile)
class ProfileType:
    pk: ID
    user: UserType
    major: str
    year: str
    language: str
    theme: str

    @gql.field
    def profile_pic(self: models.Profile) -> str:
        return self.profile_pic.url

    def get_queryset(self, queryset, info: Info):
        user = info.context.request.user
        if user.is_authenticated:
            return queryset.filter(user=user)
        return None


@gql.django.input(models.Profile, partial=True)
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


class IsAuthenticated(BasePermission):
    message = "User is not authenticated"

    # This method can also be async!
    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        print("info.field_name", info.field_name)

        print(info.context.request.user.is_authenticated)
        return True


@dataclasses.dataclass
class OwnsObjPerm(ConditionDirective):

    message: Private[str] = "You don't own this object."

    def check_condition(
        self, root: Any, info: GraphQLResolveInfo, user: UserType, **kwargs
    ):
        pk = kwargs["input"]["pk"]
        if pk:
            try:
                pk = int(pk)
            except:
                raise ValueError("The field `pk` is not valid.")
            return user.profile.pk == pk
        raise ValueError("The field `p` must be provided.")
