import graphene
from graphql import GraphQLError
from django.contrib.auth.models import User, Group
from graphene_django_crud.types import DjangoGrapheneCRUD, resolver_hints
from .models import Tag,Question,Answer

class Question(DjangoGrapheneCRUD):
    class Meta:
        model = Question
        #exclude_fields = None
        fields = "__all__"
        input_exclude_fields = ("created", 'active')

    @resolver_hints(
      only=["body", "user", "created"]
    )

    @classmethod
    def get_queryset(cls, parent, info, **kwargs):
            return Question.objects.all()


    @classmethod
    def before_mutate(cls, parent, info, instance, data):
        data['question'] = data['question'] + "555555555"
        return 
            


class Query(graphene.ObjectType):

    
    question = Question.ReadField()
    questions = Question.BatchReadField()

    def resolve_me(parent, info, **kwargs):
        if not info.context.user.is_authenticated:
            return None
        else:
            return info.context.user

class Mutation(graphene.ObjectType):

    question_create = Question.CreateField()
    question_update = Question.UpdateField()
    question_delete = Question.DeleteField()


