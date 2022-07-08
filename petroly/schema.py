import strawberry

import strawberry
from strawberry.tools import merge_types
from strawberry_django_jwt.middleware import JSONWebTokenMiddleware
from strawberry_django_plus.optimizer import DjangoOptimizerExtension
from strawberry_django_plus.directives import SchemaDirectiveExtension

import account.schema
import communities.schema
import evaluation.schema

Query = merge_types(
    "RootQuery",
    (account.schema.Query, communities.schema.Query, evaluation.schema.Query),
)

Mutation = merge_types(
    "RootMutation",
    (account.schema.Mutation, communities.schema.Mutation, evaluation.schema.Mutation),
)

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        DjangoOptimizerExtension,
        SchemaDirectiveExtension,
        JSONWebTokenMiddleware,
    ],
)
