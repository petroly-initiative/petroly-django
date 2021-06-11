import graphene
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field
from graphql_auth.schema import UserQuery, MeQuery
from graphql_auth import mutations
from graphql_jwt.decorators import login_required
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from .models import Profile


# graphene doesn't know how to handle a CloudinaryField
# so we need to register it
@convert_django_field.register(CloudinaryField)
def convert_profile_pic(field: CloudinaryField, registry=None) -> str:
    return str(field)


class UserType(DjangoObjectType):
    '''
    A type for the django model `account.User`.
    '''

    class Meta:
        model = User
        fields = ["username", 'email', 'is_active']


class ProfileType(DjangoObjectType):
    '''
    A type for the django model `account.Profile`.
    '''

    # define the GraphQL field type
    profile_pic = graphene.String()

    class Meta:
        model = Profile
        fields = ['year', 'major']

class AuthMutation(graphene.ObjectType):
    '''
    All authintication mutations.
    It inherits from `django-graphql-auth` and `django-graphql-jwt`.
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


class Query(UserQuery, MeQuery, graphene.ObjectType):
    '''
    Main entry for all query type for `account` app.
    It inherits `UserQuery` and `MeQuery`.
    '''
    profiles = graphene.Field(ProfileType, token=graphene.String(required=True))
    user2 = graphene.Field(UserType)

    @login_required
    def resolve_profiles(root, info, **kwargs):
        return Profile.objects.filter(user__pk=info.context.user.pk)

    @login_required
    def resolve_user2(root, info, **kwargs):
        return info.context.user



class Mutation(AuthMutation, graphene.ObjectType):
    '''
    Main entry for all `Mutation` types for `account` app.
    It inherits from `AuthMutation`.
    '''
    
    pass