from graphql import GraphQLError
from django.conf import settings


class HideIntrospectMiddleware:
    """
    This middleware to prevent getting the schema. This class hide the
    introspection. It checks for __schema field_name and __type, if it is there
    return None
    """

    def resolve(self, next, root, info, **args):
        if info.field_name in ["__schema", "__type"] and not settings.DEBUG:
            raise GraphQLError("You are not allowed")
        return next(root, info, **args)
