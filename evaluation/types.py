from typing import Callable, ClassVar, Optional, List, Any

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

@gql.django.type(models.Instructor)
class InstructorType:
    pk: ID
    
    name: auto
    department: auto
    profile_pic: str
    
    evaluation_set: List["EvaluationType"]


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