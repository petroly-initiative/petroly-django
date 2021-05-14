import graphene
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field
from . import models
from cloudinary.models import CloudinaryField


@convert_django_field.register(CloudinaryField)
def convert_profile_pic(field, registry=None):

    return "TEST"

class InstructorType(DjangoObjectType):

    profile_pic = graphene.String()

    class Meta:
        model = models.Instructor
        fields = ['name', 'department', 'profile_pic']

class EvaluationType(DjangoObjectType):

    class Meta:
        model = models.Evaluation
        fileds = [
            'comment', 'date', 'grading', 'grading',
            'teaching', 'personality', 'user', 'instructor',
        ]

class Query(graphene.ObjectType):

    all_instructors = graphene.List(InstructorType, name=graphene.String(), pk=graphene.Int())
    all_evaluations = graphene.List(EvaluationType)

    def resolve_all_instructors(root, info, name=None, pk=None):
        if pk != None:
            return models.Instructor.objects.filter(pk=pk)          
        return models.Instructor.objects.filter(name__icontains=name)

    def resolve_all_evaluations(root, info):
        return models.Evaluation.objects.all()


class InstructorMutation(graphene.Mutation):

    instructor = graphene.Field(InstructorType)

    class Arguments:
        name = graphene.String(required=True)
        department = graphene.String()

    @classmethod
    def mutate(cls, root, info, name, department):
        instructor = models.Instructor(name=name, department=department)
        instructor.save()
        return InstructorMutation(instructor=instructor)


class Mutation(graphene.ObjectType):

    update_instructor = InstructorMutation.Field()




schema = graphene.Schema(Query, Mutation)