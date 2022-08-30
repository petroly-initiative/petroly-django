
import re
from typing import List


from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from strawberry import ID
from strawberry.types import Info
from strawberry_django_plus import gql
from strawberry_django_plus.permissions import IsAuthenticated
from django_q.tasks import async_task

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
    root, info: Info, pk: ID
) -> CommunityInteractionsType:

    user: User = info.context.request.user

    return CommunityInteractionsType(
        liked=Community.objects.filter(pk=pk, likes=user).exists(),
        reported=Community.objects.filter(
            pk=pk, reports__reporter=user
        ).exists(),
    )


def rsolve_toggle_like_community(root, info: Info, pk: ID) -> bool:
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


def resolve_quick_add(root, info: Info, text: str) -> bool:

    try:
        matches = re.findall(r'https:\/\/chat.whatsapp.com\/[A-Za-z0-9]*', text)

        async_task(
            'communities.populate.whatsapp_populate',
            matches,
            task_name='populate_whatsapp',
            group='communities',
            timeout=60 * 60     # 1 hour
        )
        return True

    except Exception:
        return False


@gql.type
class Query:

    community_interactions: CommunityInteractionsType = gql.field(
        resolve_community_interactions, directives=[IsAuthenticated()]
    )
    community: CommunityType = gql.django.field()
    communities: List[CommunityType] = gql.django.field()


@gql.type
class Mutation:

    quick_add: bool = gql.field(resolve_quick_add)
    community_create: CommunityType = gql.django.create_mutation(
        CommunityInput, directives=[IsAuthenticated(), MatchIdentity()]
    )
    community_update: CommunityType = gql.django.update_mutation(
        CommunityPartialInput, directives=[IsAuthenticated(), OwnsObjPerm()]
    )
    community_delete: CommunityType = gql.django.delete_mutation(
        CommunityPartialInput, directives=[IsAuthenticated(), OwnsObjPerm()]
    )

    report_create = gql.mutation(
        resolve_report, directives=[IsAuthenticated()]
    )

    toggle_like_community = gql.mutation(
        rsolve_toggle_like_community,
        directives=[IsAuthenticated()],
        description="This will toggle the community like for the logged user",
    )
