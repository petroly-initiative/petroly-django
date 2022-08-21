"""
This module is to define the GraphQL queries and mutations
of the `telegram_bot` app.
"""

from strawberry.types import Info
from strawberry_django_plus import gql
from strawberry_django_plus.permissions import IsAuthenticated
from django_q.tasks import async_task

from .models import Token


@gql.type
class Query:
    """Main entry of all Query types of `notifier` app."""


@gql.type
class Mutation:
    """Main entry of all Mutation types of `notifier` app."""

    @gql.mutation(directives=[IsAuthenticated()])
    def get_telegram_token(self, info: Info) -> str:
        """
        Create a obj from `Token` model,
        return the generated token.
        """
        user = info.context.request.user

        obj = Token.objects.create(user=user)

        return obj.token
        
def print_obj(task):
    print(task.result)