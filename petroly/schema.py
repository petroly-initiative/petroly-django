"""
Here all `pertoly` projects' queries and mutations are merged down 
into a single `RootQuery` and `RootMutation`.
"""

import strawberry
from graphql.validation import NoSchemaIntrospectionCustomRule
from strawberry.extensions import AddValidationRules, QueryDepthLimiter
from strawberry.tools import merge_types
from strawberry_django_jwt.middleware import JSONWebTokenMiddleware
from strawberry_django_plus.optimizer import DjangoOptimizerExtension
from strawberry_django_plus.directives import SchemaDirectiveExtension

import account.schema
import communities.schema
import evaluation.schema
import notifier.schema
import telegram_bot.schema
from strawberry_ratelimit.ratelimit import ExtensionRatelimit


Query = merge_types(
    "Query",
    (
        account.schema.Query,
        communities.schema.Query,
        evaluation.schema.Query,
        notifier.schema.Query,
        telegram_bot.schema.Query,
    ),
)

Mutation = merge_types(
    "Mutation",
    (
        account.schema.Mutation,
        communities.schema.Mutation,
        evaluation.schema.Mutation,
        notifier.schema.Mutation,
        telegram_bot.schema.Mutation,
    ),
)

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        # AddValidationRules([NoSchemaIntrospectionCustomRule]),
        QueryDepthLimiter(max_depth=10),
        ExtensionRatelimit(
            type_name=[
                "me",
                "search",
                "instructor",
                "instructors",
                "evaluations",
                "evaluation",
                "rawData",
                "register",
                "refreshToken",
            ],
            rate_max=120,
            rate_seconds=60,
        ),
        DjangoOptimizerExtension,
        SchemaDirectiveExtension,
        JSONWebTokenMiddleware,
    ],
)
