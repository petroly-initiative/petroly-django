import graphene
import graphql
from graphql import GraphQLError
from graphene import ObjectType
from graphene_django import DjangoObjectType
from graphene_django_crud import DjangoGrapheneCRUD
from graphql_jwt.decorators import *

from .models import Offer
from .utils import is_owner

class OfferType(DjangoGrapheneCRUD):

    class Meta:
        model = Offer
        exclude_fields = ('user', )
        input_exclude_fields = ('user', )

    @classmethod
    def get_queryset(cls, parent, info, **kwargs):
        print(info.context.META)
        print(info.context.POST)
        print(info.context.GET)
        return super().get_queryset(parent, info, **kwargs)

    @classmethod
    @login_required
    def before_create(cls, parent, info, instance, data):
        if info.context.user.offer:
            raise GraphQLError('You already have created an offer')

    @classmethod
    @is_owner
    def before_update(cls, parent, info, instance, data):
        return
    
    @classmethod
    @is_owner
    def before_delete(cls, parent, info, instance, data):
        return

class Query(ObjectType):

    offers = OfferType.BatchReadField()



class Mutation(ObjectType):
    
    offer_create = OfferType.CreateField()
    offer_update = OfferType.UpdateField()
    offer_delete = OfferType.DeleteField()


schema = graphene.Schema(query=Query, mutation=Mutation)