from typing import List

import strawberry
from strawberry import ID
from strawberry.types.info import Info
from strawberry_django_plus import gql
from strawberry_django_plus.permissions import IsAuthenticated

from .types import (
    InstructorType,
    EvaluationType,
    OwnsObjPerm,
    EvaluationInput,
    EvaluationPartialInput,
    PkInput,
    MatchIdentity,
)

from django.contrib.auth.models import User, Group
from .models import Evaluation, Instructor
from data import departments

'''
class EvaluationType(DjangoGrapheneCRUD):
    """
    A type for the `evaluation.Evaluation` model.
    """

    class Meta:
        model = Evaluation
        exclude_fields = ("user",)

    @classmethod
    @login_required
    def before_create(cls, parent, info, instance, data) -> None:
        instructor_pk = data["instructor"]["connect"]["id"]["exact"]

        # the logged use is the evaluator
        instance.user = info.context.user

        if Evaluation.objects.filter(
            user=info.context.user, instructor__pk=instructor_pk
        ):
            raise GraphQLError(
                "You have evaluated this instructor before, you can edit it in My Evaluations."
            )
        return

    # Forbid user to change other users' evaluation
    @classmethod
    @is_owner
    def before_update(cls, parent, info, instance, data) -> None:
        return
'''


def resolve_department_list(root, info: Info, short: bool = True) -> List[str]:
    dep_short: List[str] = []
    dep_long: List[str] = []
    for short_, long_ in departments:
        dep_short.append(short_)
        dep_long.append(long_)

    if short:
        return dep_short

    return dep_long


def resolve_has_evaluated(root, info: Info, pk: ID) -> bool:
    return Evaluation.objects.filter(
        user=info.context.request.user, instructor__pk=pk
    ).exists()


def resolve_evaluated_instructors(root, info: Info) -> List[str]:
    ids: List[str] = []
    for i in Instructor.objects.all():
        if i.evaluation_set.exists():
            ids.append(str(i.pk))
    return ids


@strawberry.type
class Query:
    """
    Main entry for all the query types
    """

    evaluation: EvaluationType = gql.django.field()
    evaluations: List[EvaluationType] = gql.django.field()

    instructor: InstructorType = gql.django.field()
    instructors: List[InstructorType] = gql.django.field()

    department_list = strawberry.field(resolve_department_list)
    evaluated_instructors = strawberry.field(resolve_evaluated_instructors)
    has_evaluated = strawberry.field(
        resolve_has_evaluated, directives=[IsAuthenticated()]
    )


@strawberry.type
class Mutation:
    """
    Main entry for all Mutation types
    """

    evaluation_create: EvaluationType = gql.django.create_mutation(
        EvaluationInput, directives=[IsAuthenticated(), MatchIdentity()]
    )
    evaluation_update: EvaluationType = gql.django.update_mutation(
        EvaluationPartialInput, directives=[IsAuthenticated(), OwnsObjPerm()]
    )
    evaluation_delete: EvaluationType = gql.django.delete_mutation(
        PkInput, directives=[IsAuthenticated(), OwnsObjPerm()]
    )
