from cloudinary.models import CloudinaryField

import graphene
import graphene_django
from graphql import GraphQLError
from graphene import relay, ObjectType, String, Scalar
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_auth import mutations
from graphql_jwt.decorators import *
from graphene_file_upload.scalars import Upload
from graphene_django_crud.types import DjangoGrapheneCRUD, resolver_hints

from django.contrib.auth.models import User
from .models import Profile
from .utils import is_owner
from graphql_auth.models import UserStatus



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
    @staff_member_required
    def get_queryset(cls, parent, info, **kwargs):
        return super().get_queryset(parent, info, **kwargs)


class ProfileType(DjangoGrapheneCRUD):
    """
    A type for `account.Profile` model.
    """
    
    file = Upload()

    class Meta:
        model = Profile
        input_exclude_fields = ('user', )
        exclude_fields = ('user', )

    @classmethod
    @is_owner
    def before_update(cls, parent, info, instance, data):
        return

class ProfileNode(DjangoObjectType):
    """
    A type for `account.Profile` model.
    This class is for graphql_auth methods.
    """
    
    class Meta:
        model = Profile
        exclude = ('user', )


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


class Query(graphene.ObjectType):
    '''
    Main entry for all query type for `account` app.
    '''
    # profile = ProfileType.ReadField()
    # profiles = ProfileType.BatchReadField()

    # user = UserType.ReadField()
    users = UserType.BatchReadField()

    me = graphene.Field(UserType)

    @login_required
    def resolve_me(parent, info):
        return info.context.user


class Mutation(AuthMutation, graphene.ObjectType):
    '''
    Main entry for all `Mutation` types for `account` app.
    It inherits from `AuthMutation`.
    '''
    
    profile_update = ProfileType.UpdateField()