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


@strawberry.django.type(model=get_user_model())
# @inject_field({user_pk_field: auto})
class UserType:
    username: auto
    email: auto
    first_name: auto
    last_name: auto
    logentry_set: auto
    is_superuser: auto
    last_login: auto
    is_staff: auto
    is_active: auto
    date_joined: auto
    profile: "ProfileType"


@strawberry_django.type(models.Profile)
class ProfileType:
    id: ID
    user: UserType
    profile_pic: str
    major: str
    year: str
    language: str
    theme: str

    def get_queryset(self, queryset, info: Info):
        user = info.context.request.user
        print(queryset)
        if user.is_authenticated:
            return queryset.filter(user=user)
        return None


@strawberry_django.input(models.Profile)
class ProfileInput:
    id: auto
    major: str
    year: str
    language: str
    theme: str


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

    def check_condition(self, root: Any, info: GraphQLResolveInfo, user: UserType, **kwargs):
        pk = kwargs["input"]["id"]
        if pk:
            try:
                pk = int(pk)
            except:
                raise ValueError("The field `id` is not valid.")
            return  user.profile.pk == pk
        raise ValueError('The field `id` must be provided.')
