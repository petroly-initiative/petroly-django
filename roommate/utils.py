from graphql import GraphQLError
from graphql_jwt.decorators import *
from graphql_auth.decorators import login_required as login_required_

def is_owner(func):
    """A decorator to check if the logged user owns the instance"""

    @login_required
    def wrapper(cls, parent, info, instance, data):
        if not info.context.user == instance.user:
            raise GraphQLError("You don't own this Profile")
        return func(cls, parent, info, instance, data)
    return wrapper