"""
This module provides types of `evaluation` app for usage
in `schema.py`.
"""

import dataclasses
from typing import List, Any

import strawberry
import strawberry.django
from strawberry import ID, auto, Private
from strawberry.types import Info
from strawberry.django import relay
from strawberry_django.utils.typing import UserType
from graphql.type.definition import GraphQLResolveInfo
from strawberry_django.permissions import ConditionDirective
from strawberry_django.permissions import DjangoPermissionExtension

from .models import Instructor, Evaluation


@strawberry.django.filter(Instructor, lookups=True)
class InstructorFilter:
    name: auto
    department: auto


@strawberry.django.type(Instructor, filters=InstructorFilter)
class InstructorNode(relay.Node):
    pk: ID

    name: str
    department: str

    evaluation_set: List["EvaluationNode"]

    # custom fields

    @strawberry.django.field
    def instructor_count(self: Instructor, info: Info) -> str:
        return Instructor.objects.count()

    @strawberry.django.field
    def profile_pic(self: Instructor, info: Info) -> str:
        return self.profile_pic.url

    @strawberry.django.field
    def evaluation_set_count(self: Instructor, info: Info) -> int:
        return self.evaluation_set.count()

    @strawberry.django.field
    def grading_avg(self: Instructor, info) -> float:
        return self.avg()["grading__avg"] or 0

    @strawberry.django.field
    def teaching_avg(self: Instructor, info) -> float:
        return self.avg()["teaching__avg"] or 0

    @strawberry.django.field
    def personality_avg(self: Instructor, info) -> float:
        return self.avg()["personality__avg"] or 0

    @strawberry.django.field
    def overall(self: Instructor, info) -> int:
        return self.avg()["overall"]

    @strawberry.django.field
    def overall_float(self: Instructor, info) -> float:
        return self.avg()["overall_float"]


@strawberry.django.type(Evaluation)
class EvaluationNode(relay.Node):
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

    instructor: InstructorNode


@strawberry.django.type(Evaluation)
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

    instructor: InstructorNode


@strawberry.django.input(Evaluation, partial=True)
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

    # instructor: ID


@strawberry.django.input(Evaluation)
class EvaluationInput:
    comment: auto
    course: auto
    term: auto

    grading: auto
    teaching: auto
    personality: auto

    grading_comment: auto
    teaching_comment: auto
    personality_comment: auto

    user: ID
    instructor: ID


@strawberry.input
class PkInput:
    """General purpose pk input type"""

    pk: ID


@dataclasses.dataclass
class OwnsObjPerm(ConditionDirective):
    """
    This is to check users can only modify theirs.
    """

    message: Private[str] = "You don't have such evaluation."

    def check_condition(
        self, root: Any, info: GraphQLResolveInfo, user: UserType, **kwargs
    ) -> bool:
        pk = kwargs["input"]["pk"]  # get evaluation's `pk`
        if Evaluation.objects.filter(pk=pk, user=user).exists():
            return True

        return False


# This is not used,
# we created a constraint on `Evaluation` model
# to do the same thing
class NotEvaluated(ConditionDirective):

    message: Private[str] = "You can only evalute an instructor once."

    def check_condition(
        self, root: Any, info: GraphQLResolveInfo, user: UserType, **kwargs
    ) -> bool:

        kwargs["input"]["user"] = user.pk  # set the user field to the logged user
        pk = kwargs["input"]["instructor"]  # get instructor `pk`

        return Evaluation.objects.filter(
            user=info.context.request.user, instructor__pk=pk
        ).exists()


@dataclasses.dataclass
class MatchIdentity(ConditionDirective):
    """
    This to check wether the provided `user` match ther logged-in user.
    """

    message: Private[str] = "Your identity isn't matching the provided `user`."

    def check_condition(
        self, root: Any, info: GraphQLResolveInfo, user: UserType, **kwargs
    ):
        pk = kwargs["input"]["user"]
        if pk:
            try:
                if int(pk) == user.pk:
                    return True
                return False
            except:
                raise ValueError("The field `user` is not valid.")
        raise ValueError("The field `user` must be provided.")
