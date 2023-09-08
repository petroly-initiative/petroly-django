"""
This module is to define the GraphQL queries and mutations
of the `telegram_bot` app.
"""

import strawberry
from strawberry.types import Info
from strawberry_django.permissions import IsAuthenticated

from .models import Token


@strawberry.type
class Query:
    """Main entry of all Query types of `notifier` app."""


@strawberry.type
class Mutation:
    """Main entry of all Mutation types of `notifier` app."""

    @strawberry.mutation(directives=[IsAuthenticated()])
    def get_telegram_token(self, info: Info) -> str:
        """
        Create a obj from `Token` model,
        return the generated token.
        """
        user = info.context.request.user

        obj = Token.objects.create(user=user)

        return obj.token
