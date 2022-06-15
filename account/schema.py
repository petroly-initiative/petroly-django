import strawberry
from typing import Optional
from strawberry.file_uploads import Upload
from gqlauth.user.queries import UserQueries
from gqlauth.user import arg_mutations
from strawberry_django_jwt.decorators import login_required

from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site

from cloudinary.models import CloudinaryField
from cloudinary.uploader import upload_image

# from .utils import is_owner

from .types import UserType, ProfileType, ProfilePicUpdateType
from .models import Profile

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


@strawberry.type
class UserMutations:
    token_auth = arg_mutations.ObtainJSONWebToken.Field  # login mutation
    verify_token = arg_mutations.VerifyToken.Field
    refresh_token = arg_mutations.RefreshToken.Field
    revoke_token = arg_mutations.RevokeToken.Field
    register = arg_mutations.Register.Field
    verify_account = arg_mutations.VerifyAccount.Field
    # update_account = arg_mutations.UpdateAccount.Field
    # resend_activation_email = arg_mutations.ResendActivationEmail.Field
    # archive_account = arg_mutations.ArchiveAccount.Field
    # delete_account = arg_mutations.DeleteAccount.Field
    # password_change = arg_mutations.PasswordChange.Field
    send_password_reset_email = arg_mutations.SendPasswordResetEmail.Field
    password_reset = arg_mutations.PasswordReset.Field
    # password_set = arg_mutations.PasswordSet.Field
    # verify_secondary_email = arg_mutations.VerifySecondaryEmail.Field
    # swap_emails = arg_mutations.SwapEmails.Field
    # remove_secondary_email = arg_mutations.RemoveSecondaryEmail.Field
    # send_secondary_email_activation = arg_mutations.SendSecondaryEmailActivation.Field


@strawberry.type
class Query:
    """
    Main entry for all query type for `account` app.
    """

    @strawberry.django.field
    def profile(self, info) -> Optional[ProfileType]:
        user = info.context.request.user
        if not user.is_anonymous:
            return user.profile

    @strawberry.django.field
    def me(self, info) -> Optional[UserType]:
        user = info.context.request.user
        if not user.is_anonymous:
            return user


@strawberry.type
class Mutation(UserMutations):
    """
    Main entry for all `Mutation` types for `account` app.
    It inherits from `AuthMutation`.
    """

    @strawberry.mutation
    @login_required
    def profile_pic_update(self, info, file: Upload) -> ProfilePicUpdateType:
        """
        Mutation to help upload only a profile pic to Cloudinary
        then save it to Profile model.
        The pic will be save in the current logged in user's profile.
        """

        try:
            user: User = info.context.request.user
            # to prvent colliding with dev & prod
            ext = get_current_site(info.context.request).domain
            res = upload_image(
                file,
                folder=f"profile_pics/{ext}",
                public_id=user.username,
                overwrite=True,
                invalidate=True,
                transformation=[{"width": 200, "height": 200, "crop": "fill"}],
                format="jpg",
            )
            user.profile.profile_pic = res
            user.profile.save()
        except Exception as e:
            print(e)
            return ProfilePicUpdateType(success=False, profile_pic="")

        return ProfilePicUpdateType(
            success=True, profile_pic=str(user.profile.profile_pic)
        )

    # profile_update = ProfileType.UpdateField()
