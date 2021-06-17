import graphene
from graphql import GraphQLError
from django.contrib.auth.models import User, Group
from graphene_django_crud.types import DjangoGrapheneCRUD, resolver_hints
from .models import Group
from forum.permissions import has_object_permission

class GroupCRUD(DjangoGrapheneCRUD):
    
    @resolver_hints(
      only=["link", "major", "course",'report', 'verified']
    )

    #@classmethod
    #def before_mutate(cls, parent, info, instance, data):
     #   if not info.context.user.is_authenticated:
      #      return GraphQLError("You need to login")
       # else:
        #    return None
    
    #@classmethod
    #def before_create(cls, parent, info, instance, data):
     #   if not info.context.user.is_authenticated:
      #      return GraphQLError("You need to login")
       # else:
        #    return None
    
    @classmethod
    def before_update(cls, parent, info, instance, data):
        if not has_object_permission(info.context, instance):
            raise GraphQLError('not authorized, you must update your questions only')
        else:
            instance.user = info.context.user
            return None

    @classmethod
    def before_delete(cls, parent, info, instance, data):
        if not has_object_permission(info.context, instance):
            raise GraphQLError('not authorized, you must delete your questions only')
        else:
            instance.user = info.context.user
            return None


    class Meta:
        model = Group
        fields = "__all__"
        input_exclude_fields = ('verified')




class Query(graphene.ObjectType):
    group = GroupCRUD.ReadField()
    groups = GroupCRUD.BatchReadField()




class Mutation(graphene.ObjectType):
    group_create = GroupCRUD.CreateField()
    group_update = GroupCRUD.UpdateField()
    group_delete = GroupCRUD.DeleteField()



