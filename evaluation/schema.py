from typing import List, Optional, Iterable, Type
from base64 import b64encode

import strawberry
from strawberry import ID
from strawberry.types.info import Info
from strawberry_django_plus import gql
from strawberry_django_plus.gql import relay
from strawberry_django_plus.relay import Connection, Node
from strawberry_django_plus.permissions import IsAuthenticated
from django.db.models import QuerySet

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


def crete_global_id(cls: Type[Node], id: int | str) -> str:
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

    evaluation: EvaluationType = gql.django.field()
    evaluations: List[EvaluationType] = gql.django.field()

    instructor: Optional[InstructorNode] = relay.node()
    instructors_connection: Connection[InstructorNode] = relay.connection()

    @relay.connection
    def instructors(self, input: InstructorFilter) -> Iterable[InstructorNode]:
        filters = {
            "name__icontains": input.name.i_contains,
        } | ({"department": input.department} if input.department else {})

        sorted_instructors = sorted(
            Instructor.objects.filter(**filters),
            key=lambda obj: obj.avg()["overall_float"],
            reverse=True,
        )
        return Instructor.objects.filter(
            pk__in=[obj.pk for obj in sorted_instructors]
        )

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
