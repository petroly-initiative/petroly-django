import graphene
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field
from graphql_auth.schema import UserQuery, MeQuery
from graphql_auth import mutations
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from .models import Profile

from graphql_auth.mixins import VerifyAccountMixin

@convert_django_field.register(CloudinaryField)
def convert_profile_pic(field, registry=None):

    return "TEST"

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ["username", 'email', 'is_active']

class ProfileType(DjangoObjectType):
    profile_pic = graphene.String()

    class Meta:
        model = Profile
        fields = ['profile_pic', 'year', 'major']


# class Query(graphene.ObjectType):
#     viewer = graphene.Field(UserType)

#     def resolve_viewer(self, info, **kwargs):
#         user = info.context.user
#         if not user.is_authenticated:
#             raise Exception('Authentication credentials were not provided')
#         return user

# class Mutation(graphene.ObjectType):
#     token_auth = graphql_jwt.ObtainJSONWebToken.Field()
#     verify_token = graphql_jwt.Verify.Field()
#     refresh_token = graphql_jwt.Refresh.Field()

class Query(UserQuery, MeQuery, graphene.ObjectType):
    pass

class AuthMutation(graphene.ObjectType):
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
    # send_secondary_email_activation =  mutations.SendSecondaryEmailActivation.Field()
    # verify_secondary_email = mutations.VerifySecondaryEmail.Field()
    # swap_emails = mutations.SwapEmails.Field()
    # remove_secondary_email = mutations.RemoveSecondaryEmail.Field()

    # django-graphql-jwt inheritances
    token_auth = mutations.ObtainJSONWebToken.Field()
    verify_token = mutations.VerifyToken.Field()
    refresh_token = mutations.RefreshToken.Field()
    revoke_token = mutations.RevokeToken.Field()

class Mutation(AuthMutation, graphene.ObjectType):
    pass



#schema = graphene.Schema(query=Query, mutation=Mutation)