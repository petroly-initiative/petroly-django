from io import FileIO
from cloudinary.models import CloudinaryField

# import graphene
# import graphene_django
# from graphql import GraphQLError
# from graphene import relay, ObjectType, String, Scalar
# from graphene_django import DjangoObjectType
# from graphene_django.filter import DjangoFilterConnectionField
# from graphql_auth import mutations
# from graphql_jwt.decorators import *
# from graphene_file_upload.scalars import Upload
# from graphene_django_crud.types import DjangoGrapheneCRUD, resolver_hints
# from graphql_auth.models import UserStatus

from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from .models import Profile
# from .utils import is_owner
from cloudinary.uploader import upload_image


# class StatusType(DjangoGrapheneCRUD):
#     """
#     A type for `UserStatus` from graphql_auth lib.
#     It is defined to enable accessing to verified value for a user.
#     """

#     class Meta:
#         model = UserStatus


# class UserType(DjangoGrapheneCRUD):
#     """
#     A type for `auth.User`. It is used to be found in other types.
#     """

#     class Meta:
#         model = User
#         exclude_fields = ("password",)
#         input_exclude_fields = ("last_login", "date_joined")

#     @classmethod
#     def get_queryset(cls, parent, info, **kwargs):
#         return super().get_queryset(parent, info, **kwargs)


# class ProfileType(DjangoGrapheneCRUD):
#     """
#     A type for `account.Profile` model.
#     """

#     file = Upload()

#     class Meta:
#         model = Profile
#         input_exclude_fields = ("user",)
#         exclude_fields = ("user",)

#     @classmethod
#     @login_required
#     def get_queryset(cls, parent, info, **kwargs):
#         return super().get_queryset(parent, info, **kwargs)

#     @classmethod
#     @is_owner
#     def before_mutate(cls, parent, info, instance, data):
#         return


# class ProfileNode(DjangoObjectType):
#     """
#     A type for `account.Profile` model.
#     This class is for graphql_auth methods.
#     """

#     class Meta:
#         model = Profile
#         exclude = ("user",)


# class AuthMutation(graphene.ObjectType):
#     """
#     All authintication mutations.
#     It inherits from `django_graphql_auth` and `django_graphql_jwt`.
#     """

#     register = mutations.Register.Field()
#     verify_account = mutations.VerifyAccount.Field()
#     resend_activation_email = mutations.ResendActivationEmail.Field()
#     send_password_reset_email = mutations.SendPasswordResetEmail.Field()
#     password_reset = mutations.PasswordReset.Field()
#     password_set = mutations.PasswordSet.Field()  # For passwordless registration
#     password_change = mutations.PasswordChange.Field()
#     update_account = mutations.UpdateAccount.Field()
#     delete_account = mutations.DeleteAccount.Field()
#     archive_account = mutations.ArchiveAccount.Field()

#     # django-graphql-jwt inheritances
#     token_auth = mutations.ObtainJSONWebToken.Field()
#     verify_token = mutations.VerifyToken.Field()
#     refresh_token = mutations.RefreshToken.Field()
#     revoke_token = mutations.RevokeToken.Field()


# class Query(graphene.ObjectType):
#     """
#     Main entry for all query type for `account` app.
#     """

#     # profile = ProfileType.ReadField()
#     # profiles = ProfileType.BatchReadField()

#     # user = UserType.ReadField()
#     # users = UserType.BatchReadField()

#     me = graphene.Field(UserType)

#     @login_required
#     def resolve_me(parent, info):
#         return info.context.user


# from graphene_file_upload.scalars import Upload


# class UploadMutation(graphene.Mutation):
#     class Arguments:
#         file = Upload(required=True)

#     success = graphene.Boolean()

#     @staticmethod
#     @login_required
#     def mutate(self, info, file, **kwargs):
#         user: User = info.context.user

#         try:
#             # to prvent colliding with dev & prod
#             ext =  get_current_site(info.context).domain
#             res = upload_image(
#                 file,
#                 folder=f"profile_pics/{ext}",
#                 public_id=user.username,
#                 overwrite=True,
#                 invalidate=True,
#                 transformation=[{"width": 200, "height": 200, "crop": "fill"}],
#                 format="jpg",
#             )
#             user.profile.profile_pic = res
#             user.profile.save()
#         except:
#             return UploadMutation(success=False)

#         return UploadMutation(success=True)


# class Mutation(AuthMutation, graphene.ObjectType):
#     """
#     Main entry for all `Mutation` types for `account` app.
#     It inherits from `AuthMutation`.
#     """

#     profile_pic_update = UploadMutation.Field()
#     profile_update = ProfileType.UpdateField()



import strawberry
from gqlauth.user.queries import UserQueries
from gqlauth.user import arg_mutations

@strawberry.type
class UserMutations:
    token_auth = arg_mutations.ObtainJSONWebToken.Field # login mutation
    verify_token = arg_mutations.VerifyToken.Field
    refresh_token = arg_mutations.RefreshToken.Field
    revoke_token = arg_mutations.RevokeToken.Field
    register = arg_mutations.Register.Field
    verify_account = arg_mutations.VerifyAccount.Field
    update_account = arg_mutations.UpdateAccount.Field
    resend_activation_email = arg_mutations.ResendActivationEmail.Field
    archive_account = arg_mutations.ArchiveAccount.Field
    delete_account = arg_mutations.DeleteAccount.Field
    password_change = arg_mutations.PasswordChange.Field
    send_password_reset_email = arg_mutations.SendPasswordResetEmail.Field
    password_reset = arg_mutations.PasswordReset.Field
    password_set = arg_mutations.PasswordSet.Field
    verify_secondary_email = arg_mutations.VerifySecondaryEmail.Field
    swap_emails = arg_mutations.SwapEmails.Field
    remove_secondary_email = arg_mutations.RemoveSecondaryEmail.Field
    send_secondary_email_activation = arg_mutations.SendSecondaryEmailActivation.Field
