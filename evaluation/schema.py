from typing import List, Optional, Iterable, Type, cast
from base64 import b64encode

import strawberry
import strawberry.django
from strawberry import ID, relay
from strawberry.types.info import Info
from django.db.models import Avg, Count
from strawberry_django.permissions import IsAuthenticated

from data import DepartmentEnum
from .models import Evaluation, Instructor
from .types import (
    EvaluationType,
    OwnsObjPerm,
    EvaluationInput,
    EvaluationPartialInput,
    PkInput,
    MatchIdentity,
    InstructorNode,
    InstructorFilter,
)


def resolve_department_list(root, info: Info, short: bool = True) -> List[str]:
    dep_short: List[str] = []
    dep_long: List[str] = []
    for short_, long_ in DepartmentEnum.choices:
        dep_short.append(short_)
        dep_long.append(long_)

    if short:
        return dep_short

    return dep_long


def resolve_has_evaluated(root, info: Info, pk: ID) -> bool:
    return Evaluation.objects.filter(
        user=info.context.request.user, instructor__pk=pk
    ).exists()


def crete_global_id(cls: Type[strawberry.relay.Node], id: int | str) -> str:
    return b64encode(bytes(f"{cls.__name__}:{id}", "utf-8")).decode()


def resolve_evaluated_instructors(root, info: Info) -> List[str]:
    ids: List[str] = []
    for i in Instructor.objects.all():
        if i.evaluation_set.exists():
            ids.append(crete_global_id(InstructorNode, i.pk))
    return ids


@strawberry.type
class Query:
    """
    Main entry for all the query types
    """

    evaluation: EvaluationType = strawberry.django.field()
    evaluations: List[EvaluationType] = strawberry.django.field()

    instructor: Optional[InstructorNode] = relay.node()
    # instructors_connection: relay.ListConnection[
    #     InstructorNode
    # ] = relay.connection()


    @relay.connection(relay.ListConnection[InstructorNode])
    def instructors(self, input: InstructorFilter) -> Iterable[Instructor]:
        filters = {
            "name__icontains": input.name.i_contains,
        } | ({"department": input.department} if input.department else {})

        sorted_by_overall = (
            Instructor.objects.filter(**filters)
            .alias(
                count=Count("evaluation"),
                overall=(
                    Avg("evaluation__grading", default=0)
                    + Avg("evaluation__teaching", default=0)
                    + Avg("evaluation__personality", default=0)
                )
                / 3,
            )
            .order_by("-overall", "-count")
        )

        return sorted_by_overall

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

    evaluation_create: EvaluationType = strawberry.django.mutations.create(
        EvaluationInput, directives=[IsAuthenticated(), MatchIdentity()]
    )
    evaluation_update: EvaluationType = strawberry.django.mutations.update(
        EvaluationPartialInput, directives=[IsAuthenticated(), OwnsObjPerm()]
    )
    evaluation_delete: EvaluationType = strawberry.django.mutations.delete(
        PkInput, directives=[IsAuthenticated(), OwnsObjPerm()]
    )
