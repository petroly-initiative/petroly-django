from typing import List, Optional
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

from graphql import GraphQLError
from django.contrib.auth.models import User

from cloudinary.uploader import upload_image
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Count

from strawberry import ID
from strawberry.types import Info
from strawberry_django_plus import gql
from strawberry_django_plus.permissions import IsAuthenticated

from .models import Community, Report
from .types import CommunityFilter, CommunityType, CommunityInteractionsType


# class CommunityType(DjangoGrapheneCRUD):
#     class Meta:
#         model = Community
#         input_exclude_fields = ("verified", "owner")

#     @classmethod
#     def get_queryset(cls, parent, info, **kwargs):
#         # descending order for number of likes
#         return (
#             Community.objects.filter(archived=False)
#             .annotate(num_likes=Count("likes"))
#             .order_by("-num_likes")
#         )

#     @classmethod
#     @login_required
#     def after_mutate(cls, parent, info, instance: Community, data):
#         if "icon" in data.keys() and data["icon"].upload:
#             try:
#                 # to prvent colliding with dev & prod
#                 ext = get_current_site(info.context).domain
#                 instance.icon = upload_image(
#                     data["icon"].upload,
#                     folder=f"communities/{ext}/icons",
#                     public_id=instance.pk,
#                     overwrite=True,
#                     invalidate=True,
#                     transformation=[{"width": 200, "height": 200, "crop": "fill"}],
#                     format="jpg",
#                 )
#                 instance.save()
#             except Exception as e:
#                 raise GraphQLError(_("Error while uploading the icon"))

#     @classmethod
#     def before_create(cls, parent, info, instance, data):
#         instance.owner = info.context.user  # owener is the logged user

#     @classmethod
#     def before_update(cls, parent, info, instance, data):
#         if "icon" in data.keys() and data["icon"].upload is None:
#             # remove the None value of icon to keep the old one
#             del data["icon"]


# class ReportType(DjangoGrapheneCRUD):
#     class Meta:
#         model = Report
#         input_exclude_fields = ("reporter", "created_on")

#     @classmethod
#     @login_required
#     def before_create(cls, parent, info, instance, data):
#         instance.reporter = info.context.user  # reporter is the logged user
#         community = Community.objects.get(
#             pk=data["community"]["connect"]["id"]["exact"]
#         )
#         if Report.objects.filter(
#             reporter=instance.reporter, community=community
#         ).exists():
#             raise GraphQLError("You have reported this community Already")


# class InteractedCommunityMutation(graphene.Mutation):
#     class Arguments:
#         ID = graphene.ID(required=True)

#     liked = Field(Boolean)
#     reported = Field(Boolean)

#     @staticmethod
#     @login_required
#     def mutate(root, info, ID):
#         user = info.context.user
#         interactions = {}
#         interactions["liked"] = Community.objects.filter(pk=ID, likes=user).exists()
#         interactions["reported"] = Community.objects.filter(
#             pk=ID, reports__reporter=user
#         ).exists()
#         return InteractedCommunityMutation(**interactions)


# class ToggleLikeCommunity(graphene.Mutation):
#     class Arguments:
#         ID = graphene.ID()

#     ok = graphene.Boolean()

#     @staticmethod
#     @login_required
#     def mutate(root, info, ID):
#         try:
#             likes = Community.objects.get(pk=ID).likes
#         except ObjectDoesNotExist:
#             return ToggleLikeCommunity(ok=False)
#         user = info.context.user
#         has_liked = Community.objects.filter(pk=ID, likes__pk=user.pk).exists()

#         if has_liked:
#             likes.remove(user)  # Unlike
#         else:
#             likes.add(user)  # Like

#         return ToggleLikeCommunity(ok=True)


def resolve_community_interactions(
    self, info: Info, pk: ID
) -> CommunityInteractionsType:

    user: User = info.context.request.user

    return CommunityInteractionsType(
        liked=Community.objects.filter(pk=pk, likes=user).exists(),
        reported=Community.objects.filter(pk=pk, reports__reporter=user).exists(),
    )


@gql.type
class Query:

    community_interactions: CommunityInteractionsType = gql.field(
        resolve_community_interactions, directives=[IsAuthenticated()]
    )
    community: CommunityType = gql.django.field()
    communities: List[CommunityType] = gql.django.field()


@gql.type
class Mutation:
    ...
    # community_create = CommunityType.CreateField()
    # community_update = CommunityType.UpdateField()
    # community_delete = CommunityType.DeleteField()

    # report_create = ReportType.CreateField()

    # has_interacted_community = InteractedCommunityMutation.Field()
    # toggle_like_community = ToggleLikeCommunity.Field(
    #     description="This will toggle the community like for the logged user"
    # )
