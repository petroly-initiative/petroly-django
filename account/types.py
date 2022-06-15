import strawberry
import strawberry_django

from strawberry import auto, ID
from strawberry.file_uploads import Upload

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
    user: "UserType"
    profile_pic: str
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
