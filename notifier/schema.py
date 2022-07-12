"""
This module is to define the GraphQL queries and mutations
of the `notifier` app.
"""
from typing import List

from strawberry.scalars import JSON
from strawberry.types import Info
from strawberry_django_plus import gql

from .types import CourseType
from .utils import fetch_data

@gql.type
class Query:
    """Main entry of all Query types of `notifier` app."""

    @gql.field
    def raw_data(self, term: int, department: str) -> JSON:
        return fetch_data(term, department)

    @gql.field
    def tracked_courses(self, info: Info) -> List[CourseType]:
        user = info.context.request.user
        return user.tracking_list.courses


@gql.type
class Mutation:
    """Main entry of all Mutation types of `notifier` app."""
