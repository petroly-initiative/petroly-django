import graphene
from graphql import GraphQLError
from django.contrib.auth.models import User, Group
from graphene_django_crud.types import DjangoGrapheneCRUD, resolver_hints
from .models import Tag,Question,Answer
from .permissions import has_object_permission

class QuestionCRUD(DjangoGrapheneCRUD):
    
    @resolver_hints(
      only=["body", "user", "created",'active']
    )

    @classmethod
    def before_mutate(cls, parent, info, instance, data):
        if not info.context.user.is_authenticated:
            return GraphQLError("You need to login")
        else:
            return None
    
    @classmethod
    def before_update(cls, parent, info, instance, data):
        if not has_object_permission(info.context, instance):
            raise GraphQLError('not authorized, you must update your questions only')
        else:
            return None

    @classmethod
    def before_delete(cls, parent, info, instance, data):
        if not has_object_permission(info.context, instance):
            raise GraphQLError('not authorized, you must delete your questions only')
        else:
            return None


    class Meta:
        model = Question
        fields = "__all__"
        input_exclude_fields = ("created", 'active')

class AnswerCRUD(DjangoGrapheneCRUD):
    
    @resolver_hints(
      only=["question", "user", "body",'created','updated','active','answers']
    )

    class Meta:
        model = Answer
        fields = "__all__"
        input_exclude_fields = ("created", 'active','updated','answers')


class TagCRUD(DjangoGrapheneCRUD):
    
    @resolver_hints(
      only=["question", "body"]
    )

    class Meta:
        model = Question
        fields = "__all__"
        input_exclude_fields = ("created", 'active')

    



class Query(graphene.ObjectType):
    question = QuestionCRUD.ReadField()
    questions = QuestionCRUD.BatchReadField()
    answer = AnswerCRUD.ReadField()
    answers = AnswerCRUD.BatchReadField()
    tag = TagCRUD.ReadField()
    tags = TagCRUD.BatchReadField()



class Mutation(graphene.ObjectType):
    question_create = QuestionCRUD.CreateField()
    question_update = QuestionCRUD.UpdateField()
    question_delete = QuestionCRUD.DeleteField()
    answer_create = AnswerCRUD.CreateField()
    answer_update = AnswerCRUD.UpdateField()
    answer_delete = AnswerCRUD.DeleteField()
    tag_create = TagCRUD.CreateField()
    tag_update = TagCRUD.UpdateField()
    tag_delete = TagCRUD.DeleteField()


