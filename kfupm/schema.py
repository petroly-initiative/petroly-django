import graphene

import evaluation.schema
import account.schema


class Query(evaluation.schema.Query, account.schema.Query, graphene.ObjectType):
    # This class will inherit from multiple Queries
    # as we begin to add more apps to our project
    pass

class Mutation(evaluation.schema.Mutation, account.schema.Mutation, graphene.ObjectType):

    pass


schema = graphene.Schema(query=Query, mutation=Mutation)