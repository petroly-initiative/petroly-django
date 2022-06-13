# import graphene
import strawberry

# import evaluation.schema
# import account.schema
# import forum.schema
# import communities.schema
# import roommate.schema


# class Query(evaluation.schema.Query, account.schema.Query, forum.schema.Query, communities.schema.Query,
#             roommate.schema.Query, graphene.ObjectType):
#     # This class will inherit from multiple Queries
#     # as we begin to add more apps to our project
#     pass

# class Mutation(evaluation.schema.Mutation, account.schema.Mutation, forum.schema.Mutation, 
#                 communities.schema.Mutation, roommate.schema.Mutation, graphene.ObjectType):

#     pass


# schema = graphene.Schema(query=Query, mutation=Mutation) 


# yourapp/schema.py

import strawberry
from strawberry.tools import merge_types
from account.schema import UserMutations, UserQueries

Query = merge_types("RootQuery", (UserQueries,))

Mutation = merge_types("RootMutation", (UserMutations,))

schema = strawberry.Schema(query=Query, mutation=Mutation)
