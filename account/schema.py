import graphene
from graphene import relay, ObjectType, String, Scalar
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
# from graphene_django.converter import convert_django_field
from graphql_auth.schema import UserQuery, MeQuery
from graphql_auth import mutations
from graphql_jwt.decorators import login_required
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from graphene_file_upload.scalars import Upload
# CRUD
from graphql import GraphQLError
from django.contrib.auth.models import User, Group
from graphene_django_crud.types import DjangoGrapheneCRUD, resolver_hints
from graphene_django_crud.converter import convert_django_field
from graphene_django_crud.utils import is_required

from .models import Profile
from graphql_auth.models import UserStatus



@convert_django_field.register(CloudinaryField)
def convert_profile_pic(field: CloudinaryField, registry=None, input_flag=None) -> String:
    """graphene doesn't know how to handle a CloudinaryField
    so we need to register it"""
    return String(
        description="CloudinaryField for profile_pic",
        required=is_required(field) and input_flag == "create",
    )

class StatusType(DjangoGrapheneCRUD):
    """
    A type for `UserStatus` from graphql_auth lib.
    It is defined to enable accessing to verified value for a user.
    """

    class Meta:
        model = UserStatus

class UserType(DjangoGrapheneCRUD):
    """
    A type for `auth.User`. It is used to be found in other types.
    """

    class Meta:
        model = User
        exclude_fields = ("password",)
        input_exclude_fields = ("last_login", "date_joined")

    @classmethod
    def get_queryset(cls, parent, info, **kwargs):
        if not info.context.user.has_perm("auth.view_user"):
            raise GraphQLError("forbidden")
        return super().get_queryset(parent, info, **kwargs)


class ProfileType(DjangoGrapheneCRUD):
    """
    A type for `account.Profile` model.
    """
    
    file = Upload()

    class Meta:
        model = Profile


class AuthMutation(graphene.ObjectType):
    '''
    All authintication mutations.
    It inherits from `django_graphql_auth` and `django_graphql_jwt`.
    '''

    register = mutations.Register.Field()
    verify_account = mutations.VerifyAccount.Field()
    resend_activation_email = mutations.ResendActivationEmail.Field()
    send_password_reset_email = mutations.SendPasswordResetEmail.Field()
    password_reset = mutations.PasswordReset.Field()
    password_set = mutations.PasswordSet.Field() # For passwordless registration
    password_change = mutations.PasswordChange.Field()
    update_account = mutations.UpdateAccount.Field()
    delete_account = mutations.DeleteAccount.Field()
    archive_account = mutations.ArchiveAccount.Field()

    # django-graphql-jwt inheritances
    token_auth = mutations.ObtainJSONWebToken.Field()
    verify_token = mutations.VerifyToken.Field()
    refresh_token = mutations.RefreshToken.Field()
    revoke_token = mutations.RevokeToken.Field()


class Query(MeQuery, graphene.ObjectType):
    '''
    Main entry for all query type for `account` app.
    It inherits `UserQuery` and `MeQuery`.
    '''
    profile = ProfileType.ReadField()
    profiles = ProfileType.BatchReadField()

    # user = UserType.ReadField()
    users = UserType.BatchReadField()


class Mutation(AuthMutation, graphene.ObjectType):
    '''
    Main entry for all `Mutation` types for `account` app.
    It inherits from `AuthMutation`.
    '''
    
    profile_create = ProfileType.CreateField()
    profile_update = ProfileType.UpdateField()
    profile_delete = ProfileType.DeleteField
