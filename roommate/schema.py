import graphene
from graphene_django import DjangoObjectType
from . import models

class OfferType(DjangoObjectType):

    class Meta:
        model = models.Offer
        fields = [
            'name', 'phone', 'email'
        ]


class Query(graphene.ObjectType):

    all_offers = graphene.List(OfferType)

    def resolve_all_offers(root, info):
        return models.Offer.objects.all()


schema = graphene.Schema(query=Query)