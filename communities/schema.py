import re
from typing import List

import strawberry
import strawberry.django
from strawberry.types import Info
from django_q.tasks import async_task
from django.contrib.auth import get_user_model
from strawberry_django.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist

from .models import Community, Report
from .types import (
    CommunityType,
    CommunityInteractionsType,
    CommunityInput,
    CommunityPartialInput,
    MatchIdentity,
    OwnsObjPerm,
    ReportInput,
)

User = get_user_model()


def resolve_community_interactions(
    root, info: Info, pk: strawberry.ID
) -> CommunityInteractionsType:
    user: User = info.context.request.user

    return CommunityInteractionsType(
        liked=Community.objects.filter(pk=pk, likes=user).exists(),
        reported=Community.objects.filter(pk=pk, reports__reporter=user).exists(),
    )


def rsolve_toggle_like_community(root, info: Info, pk: strawberry.ID) -> bool:
    try:
        likes = Community.objects.get(pk=pk).likes
    except ObjectDoesNotExist:
        return False

    user: User = info.context.request.user
    has_liked = Community.objects.filter(pk=pk, likes__pk=user.pk).exists()

    if has_liked:
        likes.remove(user)  # Unlike
    else:
        likes.add(user)  # Like

    return True


def resolve_report(root, info: Info, input: ReportInput) -> bool:
    user: User = info.context.request.user
    community = Community.objects.get(pk=input.pk)

    if Report.objects.filter(reporter=user, community=community).exists():
        raise Exception("You have reported this community Already")

    obj = Report.objects.get_or_create(
        reporter=user,  # reporter is the logged user
        reason=input.reason,
        other_reason=input.other_reason,
        community=community,
    )

    return obj[1]  # created ?


def resolve_community_create(
    root: CommunityInput, info: Info, input: CommunityInput
) -> CommunityType:
    ...


@strawberry.type
class Query:
    community_interactions: CommunityInteractionsType = strawberry.field(
        resolve_community_interactions, extensions=[IsAuthenticated()]
    )
    community: CommunityType = strawberry.django.field()
    communities: List[CommunityType] = strawberry.django.field()


@strawberry.type
class Mutation:
    community_create: CommunityType = strawberry.django.mutations.create(
        CommunityInput, extensions=[MatchIdentity(), IsAuthenticated()]
    )
    community_update: CommunityType = strawberry.django.mutations.update(
        CommunityPartialInput, extensions=[OwnsObjPerm(), IsAuthenticated()]
    )
    community_delete: CommunityType = strawberry.django.mutations.delete(
        CommunityPartialInput, extensions=[OwnsObjPerm(), IsAuthenticated()]
    )

    report_create = strawberry.mutation(resolve_report, extensions=[IsAuthenticated()])

    toggle_like_community = strawberry.mutation(
        rsolve_toggle_like_community,
        extensions=[IsAuthenticated()],
        description="This will toggle the community like for the logged user",
    )

    @strawberry.field
    def quick_add(root, info: Info, text: str) -> str:
        """Quickly, using regex, extract WhatsApp links, and add them as
        as a Section, with empty section number"""

        try:
            matches = re.findall(r"https:\/\/chat\.whatsapp\.com\/[A-Za-z0-9]*", text)

            async_task(
                "communities.populate.whatsapp_populate",
                matches,
                task_name="populate_whatsapp",
                group="communities",
                timeout=60 * 60,  # 1 hour
            )
            return (
                f"Adding {len(matches)} group(s),  they should appear within minutes."
            )

        except Exception as exc:
            return f"An issue occured - {exc}"
