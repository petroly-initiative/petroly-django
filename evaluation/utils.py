from functools import wraps
from cloudinary.models import CloudinaryField
from django.contrib.auth.models import User
from django.db.models.base import Model
from graphql.error.base import GraphQLError
from graphql_jwt.decorators import *
from graphene_django_crud.converter import convert_django_field as convert_django_field_crud
from graphene_django.converter import convert_django_field
from graphene_django_crud.utils import is_required
from graphene.types import String, Scalar


'''Converters and Types'''
from account.utils import ProfilePic



'''Permissions'''

def is_owner_(user: User, obj: Model) -> bool:
    """Check if this user owns the object"""
    
    if user.pk == obj.user.pk:
        return True
    raise GraphQLError("You don't own this Evaluation")

def is_owner(func):
    """A decorator to check if the logged user owns the instance"""

    @wraps(func)
    @login_required
    def wrapper(cls, parent, info, instance, data):
        if not info.context.user == instance.user:
            raise GraphQLError("You don't own this ")
        return func(cls, parent, info, instance, data)
    return wrapper