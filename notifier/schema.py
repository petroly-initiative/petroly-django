"""
This module is to define the GraphQL queries and mutations
of the `notifier` app.
"""

from strawberry_django_plus import gql

from .types import TrackingListType

@gql.type
class Query:
    """Main entry of all Query types of `notifier` app."""
