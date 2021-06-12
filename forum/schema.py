import graphene
from graphql import GraphQLError
from django.contrib.auth.models import User, Group
from graphene_django_crud.types import DjangoGrapheneCRUD, resolver_hints
from .models import Tag,Question,Answer

class Question(DjangoGrapheneCRUD):
    class Meta:
        model = Question
        exclude_fields = None
        input_exclude_fields = ("created")



    @resolver_hints(
      only=["body", "user", "created"]
    )
  

    @classmethod
    def get_queryset(cls, parent, info, **kwargs):
            return Question.objects.all()


    @classmethod
    def before_mutate(cls, parent, info, instance, data):
        if not info.context.user.is_staff:
            raise GraphQLError('not permited, only staff user')

        if "password" in data.keys():
            instance.set_password(data.pop("password"))


class Query(graphene.ObjectType):

    me = graphene.Field(UserType)
    user = UserType.ReadField()
    users = UserType.BatchReadField()

    group = GroupType.ReadField()
    groups = GroupType.BatchReadField()

    def resolve_me(parent, info, **kwargs):
        if not info.context.user.is_authenticated:
            return None
        else:
            return info.context.user

class Mutation(graphene.ObjectType):

    user_create = UserType.CreateField()
    user_update = UserType.UpdateField()
    user_delete = UserType.DeleteField()

    group_create = GroupType.CreateField()
    group_update = GroupType.UpdateField()
    group_delete = GroupType.DeleteField()

