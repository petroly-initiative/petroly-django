import dataclasses
from typing import Callable, ClassVar, Optional, List, Any

import strawberry
from strawberry import ID, auto, UNSET, Private
from strawberry.types import Info
from strawberry.file_uploads import Upload
from strawberry_django_plus import gql
from strawberry_django_plus.utils.typing import UserType
from strawberry_django_plus.permissions import ConditionDirective
from graphql.type.definition import GraphQLResolveInfo

from django.db.models import Count
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _

from . import models


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
        if models.Evaluation.objects.filter(pk=pk, user=user).exists():
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

        return models.Evaluation.objects.filter(
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
