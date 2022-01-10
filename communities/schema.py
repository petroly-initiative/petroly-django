from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
import graphene
from graphql import GraphQLError
from django.contrib.auth.models import User 
from graphene_django_crud.types import DjangoGrapheneCRUD, resolver_hints
from .models import Community
from forum.permissions import has_object_permission
from graphql_jwt.decorators import login_required

class CommunityType(DjangoGrapheneCRUD):
    class Meta:
        model = Community
        input_exclude_fields = ('verified', 'owner')

    # like_community = graphene.Field(graphene.ID, id_=None)

    def resolver_like_community(id, **kwargs):
        pass

    @classmethod
    @login_required
    def before_mutate(cls, parent, info, instance, data):
        pass
    
    @classmethod
    def before_create(cls, parent, info, instance, data):
       instance.owner = info.context.user   # owener is the logged user

    @classmethod
    def before_update(cls, parent, info, instance, data):
        if not has_object_permission(info.context, instance):  # user report without being owner
          if len(data) == 1 and data.get('report'):
            if data.get('report') != 1:
              raise GraphQLError(_('you can add one report only'))
            else: # user report while being owner 
              data['report'] += instance.report  
          else:       
            raise GraphQLError(_('not authorized, you must update your questions only'))
        else:
          if data.get('report'):
            if data.get('report') != 1:
              raise GraphQLError(_('you can add one report only'))
            else: # user report while being owner 
              data['report'] += instance.report




            


    @classmethod
    def before_delete(cls, parent, info, instance, data):
      if not has_object_permission(info.context, instance.question):
        raise GraphQLError(_('not authorized, you must delete your questions only'))
      else:
        return None





class Query(graphene.ObjectType):
    community = CommunityType.ReadField()
    communities = CommunityType.BatchReadField()
  

class ToggleLikeCommunity(graphene.Mutation):
    class Arguments:
        ID = graphene.ID()
    
    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(root, info, ID):
        try:
            likes = Community.objects.get(pk=ID).likes
        except ObjectDoesNotExist:
            return ToggleLikeCommunity(ok=False)
        user = info.context.user
        has_liked = Community.objects.filter(pk=ID, likes__pk=user.pk).exists()

        if has_liked:
           likes.remove(user)   # Unlike
        else:
           likes.add(user)      # Like

        return ToggleLikeCommunity(ok = True)


class Mutation(graphene.ObjectType):
    community_create = CommunityType.CreateField()
    community_update = CommunityType.UpdateField()
    community_delete = CommunityType.DeleteField()

    toggle_like_community = ToggleLikeCommunity.Field(
        description='This will toggle the community like for the logged user')