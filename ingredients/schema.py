from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from ingredients.models import Category, Ingredient


# Graphene will automatically map the Category model's fields onto the CategoryNode.
# This is configured in the CategoryNode's Meta class (as you can see below)
class CategoryNode(DjangoObjectType):
    class Meta:
        model = Category
        filter_fields = ['name', 'ingredients']
        interfaces = (relay.Node, )


class IngredientNode(DjangoObjectType):
    class Meta:
        model = Ingredient
        # Allow for some more advanced filtering here
        #filter_fields = {
        #    'name': ['exact', 'icontains', 'istartswith'],
       #     'department': ['exact', 'icontains', 'istartswith'],
        #}
        #interfaces = (relay.Node, )


class Query(ObjectType):
    category = relay.Node.Field(CategoryNode)
    all_categories = DjangoFilterConnectionField(CategoryNode)

   # ingredient = relay.Node.Field(IngredientNode)
   # all_ingredients = DjangoFilterConnectionField(IngredientNode)