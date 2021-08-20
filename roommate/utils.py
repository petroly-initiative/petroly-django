from graphql import GraphQLError
from graphql_jwt.decorators import *
from graphql_auth.decorators import login_required as login_required_
from graphql_jwt.exceptions import JSONWebTokenError

from django.utils.translation import ugettext_lazy as _

'''Permissions'''
def is_owner(func):
    """A decorator to check if the logged user owns the instance"""

    @user_passes_test(lambda user: user.is_authenticated, LoginRequired)
    def wrapper(cls, parent, info, instance, data):
        if not info.context.user == instance.user:
            raise OwnershipDenied
        return func(cls, parent, info, instance, data)
    return wrapper



'''Exceptions'''
class LoginRequired(JSONWebTokenError):
    default_message = _('You need to log in')

class OwnershipDenied(JSONWebTokenError):
    default_message = _('You don\'t own this Offer')
