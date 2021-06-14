from typing import Dict, Any

import graphene
from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.forms.mutation import DjangoModelFormMutation
from cloudinary.models import CloudinaryField
from graphene_file_upload.scalars import Upload

# CRUD
from graphql import GraphQLError
from graphene_django_crud.types import DjangoGrapheneCRUD, resolver_hints

from django.contrib.auth.models import User, Group
from graphql_auth.decorators import login_required
from . import models
from .models import Evaluation, Instructor



# To accept Cloudinary field
@convert_django_field.register(CloudinaryField)
def convert_profile_pic(field: CloudinaryField, registry=None) -> str:
    return str(field)

# Make a type of the model Instructor
class InstructorNode(DjangoObjectType):

    # the CloudinaryField
    profile_pic = graphene.String()

    class Meta:
        model = models.Instructor
        fields = ['name', 'department', 'profile_pic']
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'department': ['exact', 'icontains', 'istartswith'],
        }
        interfaces = (relay.Node, )

# A type for Evaluation model with thier fields
class EvaluationNode(DjangoObjectType):

    class Meta:
        model = models.Evaluation
        fileds = [
            'comment', 'date', 'grading', 'grading',
            'teaching', 'personality', 'user', 'instructor',
        ]
        filter_fields = [
            'comment', 'date', 'grading', 'grading',
            'teaching', 'personality', 'user', 'instructor',
        ]
        interfaces = (relay.Node, )

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
        if not user.has_perm("evaluation.add_instructor"):
            raise GraphQLError("You don't have permission")
        return
    @classmethod

    def before_delete(cls, parent, info, instance, data):
        user: User = info.context.user
        if user.has_perm("evaluation.add_instructor"):
            raise GraphQLError("You don't have permission")
        return

    class Meta:
        model = Instructor
        # exclude it to handle manually
        exclude_fields = ['profile_pic']
        input_exclude_fields = ['profile_pic']

class EvaluationType(DjangoGrapheneCRUD):

    @classmethod
    def before_create(cls, parent, info, instance: Evaluation, data: Dict[str, Any]) -> None:
        pk = data['instructor']['connect']['id']['equals']
        
        if Evaluation.objects.filter(user=info.context.user, instructor__pk=pk):
            raise GraphQLError("You have evaluated this instructor before, you can edit it in My Evaluations")
        return

    class Meta:
        model = Evaluation



# Main entry for mutaion of Evaluation model; for editing its data 
# Now to create an Evaluation
class EvaluationCreateMutation(graphene.Mutation):

    evaluation = graphene.Field(EvaluationNode)

    class Arguments:
        comment = graphene.String()
        course = graphene.String(required=True)
        grading = graphene.Int(required=True)
        teaching = graphene.Int(required=True)
        personality = graphene.Int(required=True)
        instructorID = graphene.ID(required=True)

    @classmethod
    def mutate(cls, root, info, comment, course, grading, teaching, personality, instructerID):
        instructor = Instructor.objects.get(id=instructerID)
        if Evaluation.objects.filter(user=info.context.request.user, instructor=instructor):
            return "you rated this instructer before"
        
        data = {
            'grading': grading * 20,
            'teaching': teaching * 20,
            'personality': personality * 20,
            'course': course,
            'comment': comment,
            'user':info.context.request.user,
            'instructor':instructor,
        }
        evaluation = Evaluation.objects.create(**data)
        
        return EvaluationCreateMutation(evaluation=evaluation)


# Main entry for all the query types
# Now only provides all Instructor & Evaluation objects
class Query(ObjectType):

    evaluation_crud = EvaluationType.ReadField()
    evaluations_crud = EvaluationType.BatchReadField()

    instructor_crud = InstructorType.ReadField()
    instructors_crud = InstructorType.BatchReadField()

# Main entry for all Mutation types
class Mutation(ObjectType):

    evaluation_create = EvaluationType.CreateField()
    evaluation_update = EvaluationType.UpdateField()
    evaluation_delete = EvaluationType.DeleteField()

    instructor_create = InstructorType.CreateField()
    instructor_update = InstructorType.UpdateField()
    instructor_delete = InstructorType.DeleteField()