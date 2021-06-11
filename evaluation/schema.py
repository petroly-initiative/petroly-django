from typing_extensions import Required
import graphene
from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field
from graphene_django.filter import DjangoFilterConnectionField
from .forms import insForm 
from . import models
from cloudinary.models import CloudinaryField
from graphene_django.forms.mutation import DjangoModelFormMutation
from .models import Evaluation, Instructor
import evaluation


# To accept Cloudinary field
@convert_django_field.register(CloudinaryField)
def convert_profile_pic(field: CloudinaryField, registry=None) -> str:
    return str(field)

# Make a type of the model Instructor
class InstructorType(DjangoObjectType):

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
class EvaluationType(DjangoObjectType):

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


# Main entry for all the query types
# Now only provides all Instructor & Evaluation objects
class Query(ObjectType):
    instructor = relay.Node.Field(InstructorType)
    all_instructors = DjangoFilterConnectionField(InstructorType)

    evaluation = relay.Node.Field(EvaluationType)
    all_evaluations = DjangoFilterConnectionField(EvaluationType)
    






# Main entry for mutaion of Instructor model; for editing its data 
# Now to create an instructor
class InstructorCreateMutation(graphene.Mutation):

    instructor = graphene.Field(InstructorType)

    class Arguments:
        name = graphene.String(required=True)
        department = graphene.String(required=True)
        profile_pic = graphene.Upload()

    @classmethod
    def mutate(cls, root, info, name, department, profile_pic=None):
        if profile_pic:
            instructor = Instructor(name=name, department=department, profile_pic=profile_pic)
        else:
            instructor = Instructor(name=name, department=department, profile_pic=None)
        instructor.save()
        return InstructorCreateMutation(instructor=instructor)

class InstructorUpdateMutation(graphene.Mutation):

    instructor = graphene.Field(InstructorType)

    class Arguments:
        id = graphene.ID(Required=True)
        name = graphene.String()
        department = graphene.String()
        profile_pic = graphene.Upload()

    @classmethod
    def mutate(cls, root, info, id,  name, department, profile_pic):
        instructor = Instructor.objects.get(pk=id)
        if name:
            instructor.name = name
        if instructor:
            instructor.department = department
        if profile_pic:
            instructor.profile_pic = profile_pic
        instructor.save()
        return InstructorUpdateMutation(instructor=instructor)

class InstructorDeleteMutation(graphene.Mutation):

    instructor = graphene.Field(InstructorType)

    class Arguments:
        id = graphene.ID(Required=True)


    @classmethod
    def mutate(cls, root, info, id,  name, department, profile_pic):
        instructor = Instructor.objects.get(pk=id)
  
        instructor.delete()
        return 



# Main entry for mutaion of Evaluation model; for editing its data 
# Now to create an Evaluation
class EvaluationCreateMutation(graphene.Mutation):

    evaluation = graphene.Field(EvaluationType)

    class Arguments:
        comment = graphene.String()
        course = graphene.String(required=True)
        grading = graphene.Int(required=True)
        teaching = graphene.Int(required=True)
        personality = graphene.Int(required=True)
        instructorID = graphene.ID(required=True)

    @classmethod
    def mutate(cls, root, info, comment=None, course, grading, teaching, personality, instructerID):
        instructor = Instructor.objects.get(id=instructerID)
        if Evaluation.objects.filter(user=info.context.request.user, instructor=instructer):
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

class EvaluationUpdateMutation(graphene.Mutation):

    evaluation = graphene.Field(EvaluationType)

    class Arguments:
        id = graphene.ID(required=True)
        comment = graphene.String()
        course = graphene.String(required=True)
        grading = graphene.Int(required=True)
        teaching = graphene.Int(required=True)
        personality = graphene.Int(required=True)
        instructorID = graphene.ID(required=True)

    @classmethod
    def mutate(cls, root, info,id, comment=None, course, grading, teaching, personality, instructerID):
        evaluation = Evaluation.objects.get(id=id)
        instructor = Instructor.objects.get(pk=instructerID)
        if name:
            instructor.name = name
        if instructor:
            instructor.department = department
        if profile_pic:
            instructor.profile_pic = profile_pic
        instructor.save()
        return InstructorUpdateMutation(instructor=instructor)

class InstructorDeleteMutation(graphene.Mutation):

    instructor = graphene.Field(InstructorType)

    class Arguments:
        id = graphene.ID(Required=True)


    @classmethod
    def mutate(cls, root, info, id,  name, department, profile_pic):
        instructor = Instructor.objects.get(pk=id)
  
        instructor.delete()
        return 


# Main entry for all Mutation types
class Mutation(ObjectType):

    create_instructor = InstructorCreateMutation.Field()
    update_instructor = InstructorUpdateMutation.Field()
    delete_instructor = InstructorDeleteMutation.Field()




# Create the schema to be used in urls
#schema = graphene.Schema(Query, Mutation)