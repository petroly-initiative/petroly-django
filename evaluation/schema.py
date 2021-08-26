from inspect import indentsize
from typing import Dict, Any
from django.db.models.base import Model
import json

import graphene
from graphene import *
from graphene.types.scalars import String
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError
from graphene_django_crud.types import DjangoGrapheneCRUD, resolver_hints
from graphene_django_crud.utils import is_required

from graphql_jwt.decorators import login_required
from django.contrib.auth.models import User, Group
from graphql_auth.constants import Messages
from . import models
from .utils import is_owner
from data import departments




class InstructorType(DjangoGrapheneCRUD):
    '''
    A type for the `evaluation.Instructor` model. 
    '''

    class Meta:
        model = models.Instructor

    grading_avg = graphene.Int()
    teaching_avg = graphene.Int()
    personality_avg = graphene.Int()
    overall_float = graphene.Float()
    overall = graphene.Int()

    @staticmethod
    def resolve_grading_avg(parent, info):
        return parent.avg()['grading__avg']
    
    @staticmethod
    def resolve_teaching_avg(parent, info):
        return parent.avg()['teaching__avg']
    
    @staticmethod
    def resolve_personality_avg(parent, info):
        return parent.avg()['personality__avg']
    
    @staticmethod
    def resolve_overall(parent, info):
        return parent.avg()['overall']
    
    @staticmethod
    def resolve_overall_float(parent, info):
        return parent.avg()['overall_float']

    @classmethod
    def before_create(cls, parent, info, instance, data):
        user: User = info.context.user
        if user.has_perm("evaluation.add_instructor"):
            raise GraphQLError("You don't have permission")
        return
    
    @classmethod
    def before_update(cls, parent, info, instance, data):
        user: User = info.context.user
        if not user.has_perm("evaluation.update_instructor"):
            raise GraphQLError("You don't have permission")
        return
    
    @classmethod
    def before_delete(cls, parent, info, instance, data):
        user: User = info.context.user
        if user.has_perm("evaluation.delete_instructor"):
            raise GraphQLError("You don't have permission")
        return


class EvaluationType(DjangoGrapheneCRUD):
    """
    A type for the `evaluation.Evaluation` model. 
    """

    class Meta:
        model = models.Evaluation
        exclude_fields = ('user', )

    @classmethod
    @login_required
    def before_create(cls, parent, info, instance, data) -> None:
        instructor_pk = data['instructor']['connect']['id']['equals']
        user_pk = data['user']['connect']['id']['equals']

        if info.context.user.pk != user_pk:
            raise GraphQLError("The logged user and the provided user must match.")
        
        if models.Evaluation.objects.filter(user=info.context.user, instructor__pk=instructor_pk):
            raise GraphQLError("You have evaluated this instructor before, you can edit it in My Evaluations.")
        return

    # Forbid user to change other users' evaluation
    @classmethod
    @is_owner
    def before_update(cls, parent, info, instance, data) -> None:
        return
            
    @classmethod
    @is_owner
    def before_delete(cls, parent, info, instance, data) -> None:
        return


class Data(ObjectType):
    '''
    This class is to provide general pourpose data.
    '''

    department_list = graphene.List(String, short=Boolean())

    @staticmethod
    def resolve_department_list(parent, info, short=True):
        dep_short = []
        dep_long = []
        for short_, long_ in departments:
            dep_short.append(short_)
            dep_long.append(long_)
            
        if short:
            return dep_short
        return dep_long


# Main entry for all the query types
# Now only provides all Instructor & Evaluation objects
class Query(Data, ObjectType):

    evaluation = EvaluationType.ReadField()
    evaluations = EvaluationType.BatchReadField()

    instructor = InstructorType.ReadField()
    instructors = InstructorType.BatchReadField()


# Main entry for all Mutation types
class Mutation(ObjectType):

    evaluation_create = EvaluationType.CreateField()
    evaluation_update = EvaluationType.UpdateField()
    evaluation_delete = EvaluationType.DeleteField()

    instructor_create = InstructorType.CreateField()
    instructor_update = InstructorType.UpdateField()
    instructor_delete = InstructorType.DeleteField()