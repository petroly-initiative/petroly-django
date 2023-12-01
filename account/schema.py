"""
This defines the `Query` and `Muatation` for all GraphQL operations
for `account` app.
"""
from typing import Optional
from graphql.error import GraphQLError

import strawberry
import strawberry.django
from gqlauth.user import arg_mutations
from strawberry.file_uploads import Upload
from strawberry.types.info import Info
from strawberry_django.permissions import IsAuthenticated

from django.contrib.auth.models import User
from cloudinary.uploader import upload_image
from django.contrib.sites.shortcuts import get_current_site

from account.models import Profile

from .types import (
    UserType_,
    ProfileType,
    ProfilePicUpdateType,
    ProfileInput,
    OwnsObjPerm,
)


@strawberry.type
class UserMutations:
    token_auth = arg_mutations.ObtainJSONWebToken.field  # login mutation
    verify_token = arg_mutations.VerifyToken.field
    refresh_token = arg_mutations.RefreshToken.field
    revoke_token = arg_mutations.RevokeToken.field
    register = arg_mutations.Register.field
    verify_account = arg_mutations.VerifyAccount.field
    send_password_reset_email = arg_mutations.SendPasswordResetEmail.field
    password_reset = arg_mutations.PasswordReset.field


@strawberry.type
class Query:
    """
    Main entry for all query type for `account` app.
    """

    @strawberry.field
    def me(self, info) -> Optional[UserType_]:
        user = info.context.request.user
        if user.is_anonymous:
            return None
        return user


@strawberry.type
class Mutation(UserMutations):
    """
    Main entry for all `Mutation` types for `account` app.
    It inherits from `AuthMutation`.
    """

    profile_update: ProfileType = strawberry.django.mutations.update(
        ProfileInput,
        extensions=[
            OwnsObjPerm(),
            IsAuthenticated(),
        ],
    )


    @strawberry.mutation(extensions=[IsAuthenticated()])
    def become_premium(self, info: Info) -> bool:
        profile = info.context.request.user.profile

        if profile.premium:
            return True

        if Profile.objects.filter(premium=True).count() <= 10:
            profile.premium = True
            profile.save()
            return True

        raise GraphQLError(
            "Sorry we reached 10 premium users. But still be happy we won the Expo."
        )


    @strawberry.django.mutation(extensions=[IsAuthenticated()])
    def profile_pic_update(self, info, file: Upload) -> Optional[ProfilePicUpdateType]:
        """
        Mutation to help upload only a profile pic to Cloudinary
        then save it to Profile model.
        The pic will be save in the current logged in user's profile.
        """

        user: User = info.context.request.user
        try:
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
        except Exception:
            return ProfilePicUpdateType(success=False, profile_pic="")

        return ProfilePicUpdateType(
            success=True, profile_pic=str(user.profile.profile_pic)
        )
