from typing import Dict, Any
from django.db.models.base import Model

import graphene
from graphene import relay, ObjectType, String
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.forms.mutation import DjangoModelFormMutation
from cloudinary.models import CloudinaryField
from graphene_file_upload.scalars import Upload

# CRUD
from graphql import GraphQLError
from graphene_django_crud.types import DjangoGrapheneCRUD, resolver_hints
from graphene_django_crud.utils import is_required

from django.contrib.auth.models import User, Group
from graphql_auth.constants import Messages
from graphql_auth.decorators import login_required
from . import models


# graphene doesn't know how to handle a CloudinaryField
# so we need to register it
@convert_django_field.register(CloudinaryField)
def convert_profile_pic(field: CloudinaryField, registry=None, input_flag=None) -> String:
    return String(
        description="CloudinaryField for profile_pic",
        required=is_required(field) and input_flag == "create",
    )



class InstructorType(DjangoGrapheneCRUD):

    profile_pic = graphene.String()

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

    class Meta:
        model = models.Instructor
        # exclude it to handle manually
        exclude_fields = ['profile_pic']
        input_exclude_fields = ['profile_pic']


def is_owner(user: User, obj: Model) -> bool:
    """Check if this user owns the object"""
    if user.pk == obj.user.pk:
        return True
    raise GraphQLError("You don't own this Evaluation")

class EvaluationType(DjangoGrapheneCRUD):
    """
    A type for the `evaluation.Evaluatio` model. 
    """

    class Meta:
        model = models.Evaluation

    @classmethod
    def before_create(cls, parent, info, instance, data) -> None:
        pk = data['instructor']['connect']['id']['equals']
        
        if models.Evaluation.objects.filter(user=info.context.user, instructor__pk=pk):
            raise GraphQLError("You have evaluated this instructor before, you can edit it in My Evaluations")
        return

    # Forbid user to change other users' evaluation
    @classmethod
    def before_update(cls, parent, info, instance, data) -> None:
        is_owner(info.context.user, instance)
        return
            
    @classmethod
    def before_update(cls, parent, info, instance, data) -> None:
        is_owner(info.context.user, instance)
        return



# Main entry for all the query types
# Now only provides all Instructor & Evaluation objects
class Query(ObjectType):

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