import dataclasses
from typing import Callable, ClassVar, Optional, List, Any

import strawberry
from strawberry import ID, auto, UNSET, Private
from strawberry.types import Info
from strawberry.file_uploads import Upload
from strawberry_django_plus import gql
from strawberry_django_plus.permissions import ConditionDirective
from graphql.type.definition import GraphQLResolveInfo

from django.db.models import Count
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _

from . import models
from account.types import UserType


@gql.django.filter(models.Instructor, lookups=True)
class InstructorFilter:
    name: auto
    department: auto


@gql.django.type(models.Instructor, filters=InstructorFilter)
class InstructorType:
    pk: ID

    name: auto
    department: auto
    profile_pic: str

    evaluation_set: List["EvaluationType"]

    # custom fields

    @gql.django.field
    def grading_avg(self, info) -> float:
        return self.avg()["grading__avg"]

    @gql.django.field
    def teaching_avg(self, info) -> float:
        return self.avg()["teaching__avg"]

    @gql.django.field
    def personality_avg(self, info) -> float:
        return self.avg()["personality__avg"]

    @gql.django.field
    def overall(self, info) -> int:
        return self.avg()["overall"]

    @gql.django.field
    def overall_float(self, info) -> float:
        return self.avg()["overall_float"]


# TODO add the custom fields: avg()
@gql.django.type(models.Evaluation)
class EvaluationType:
    pk: ID

    date: auto
    comment: auto
    course: auto
    term: auto

    grading: auto
    teaching: auto
    personality: auto

    grading_comment: auto
    teaching_comment: auto
    personality_comment: auto

    instructor: InstructorType


@gql.django.input(models.Evaluation, partial=True)
class EvaluationPartialInput:
    pk: ID

    comment: auto
    course: auto
    term: auto

    grading: auto
    teaching: auto
    personality: auto

    grading_comment: auto
    teaching_comment: auto
    personality_comment: auto

    instructor: ID


@gql.django.input(models.Evaluation)
class EvaluationInput:
    pk: ID


@dataclasses.dataclass
class OwnsObjPerm(ConditionDirective):

    message: Private[str] = "You don't have such evaluation."

    def check_condition(
        self, root: Any, info: GraphQLResolveInfo, user: UserType, **kwargs
    ):
        pk = info.variable_values["pk"]  # get evaluation's `pk`
        if models.Evaluation.objects.filter(pk=pk, user=user).exists():
            return True

        return False
