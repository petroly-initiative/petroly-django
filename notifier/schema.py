"""
This module is to define the GraphQL queries and mutations
of the `notifier` app.
"""

from strawberry.scalars import JSON
from strawberry_django_plus import gql

from .utils import fetch_data

@gql.type
class Query:
    """Main entry of all Query types of `notifier` app."""

    @gql.field
    def raw_data(self, term: int, department: str) -> JSON:
        return fetch_data(term, department)


@gql.type
class Mutation:
    """Main entry of all Mutation types of `notifier` app."""
