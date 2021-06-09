import graphene
from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field
from graphene_django.filter import DjangoFilterConnectionField

from . import models
from cloudinary.models import CloudinaryField

# To accept Cloudinary field
@convert_django_field.register(CloudinaryField)
def convert_profile_pic(field, registry=None):

    return "TEST"

# Make a type of the model Instructor
class InstructorType(DjangoObjectType):

   # profile_pic = graphene.String()

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
class Mutation(ObjectType):

    update_instructor = InstructorMutation.Field()



# Create the schema to be used in urls
#schema = graphene.Schema(Query, Mutation)