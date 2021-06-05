import graphene
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field
from . import models
from cloudinary.models import CloudinaryField

# To accept Cloudinary field
@convert_django_field.register(CloudinaryField)
def convert_profile_pic(field, registry=None):

    return "TEST"

# Make a type of the model Instructor
class InstructorType(DjangoObjectType):

    profile_pic = graphene.String()

    class Meta:
        model = models.Instructor
        fields = ['name', 'department', 'profile_pic']

# A type for Evaluation model with thier fields
class EvaluationType(DjangoObjectType):

    class Meta:
        model = models.Evaluation
        fileds = [
            'comment', 'date', 'grading', 'grading',
            'teaching', 'personality', 'user', 'instructor',
        ]

# Main entry for all the query types
# Now only provides all Instructor & Evaluation objects
class Query(graphene.ObjectType):

    all_instructors = graphene.List(InstructorType, name=graphene.String(), pk=graphene.Int())
    all_evaluations = graphene.List(EvaluationType)

    # return to the query Instructor objects, with filtering by `name` or `pk`
    def resolve_all_instructors(root, info, name=None, pk=None):
        if pk != None:
            return models.Instructor.objects.filter(pk=pk)          
        return models.Instructor.objects.filter(name__icontains=name)

    # return to the query all Evaluation objects 
    def resolve_all_evaluations(root, info):
        return models.Evaluation.objects.all()


# Main entry for mutaion of Instructor model; for editing its data 
# Now to create an instructor
class InstructorMutation(graphene.Mutation):

    instructor = graphene.Field(InstructorType)

    # Define the argumment to use them in editing an Instructor object
    class Arguments:
        name = graphene.String(required=True)
        department = graphene.String()

    @classmethod
    def mutate(cls, root, info, name, department):
        instructor = models.Instructor(name=name, department=department)
        instructor.save()
        return InstructorMutation(instructor=instructor)


# Main entry for all Mutation types
class Mutation(graphene.ObjectType):

    update_instructor = InstructorMutation.Field()



# Create the schema to be used in urls
schema = graphene.Schema(Query, Mutation)