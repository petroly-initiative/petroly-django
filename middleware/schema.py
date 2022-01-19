class HideIntrospectMiddleware:
    """
    This middleware to prevent getting the schema. This class hide the
    introspection. It checks for __schema field_name and __type, if it is there
    return None
    """
    def resolve(self, next, root, info, **args):
        if info.field_name == '__schema':
            return None
        return next(root, info, **args)