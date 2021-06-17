from django.contrib.auth.models import User
from django.db.models.base import Model
from graphql.error.base import GraphQLError
from graphql_jwt.decorators import *


def is_owner_(user: User, obj: Model) -> bool:
    """Check if this user owns the object"""
    
    if user.pk == obj.user.pk:
        return True
    raise GraphQLError("You don't own this Profile")

def is_owner(func):
    """A decorator to check if the logged user owns the instance"""

    @login_required
    def wrapper(cls, parent, info, instance, data):
        if not info.context.user == instance.user:
            raise GraphQLError("You don't own this Profile")
        return func(cls, parent, info, instance, data)
    return wrapper