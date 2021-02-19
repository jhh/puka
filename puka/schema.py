import graphene
import graphql_jwt

import bookmarks.schema
import users.schema


class Query(bookmarks.schema.Query, users.schema.Query, graphene.ObjectType):
    pass


class Mutation(bookmarks.schema.Mutation, users.schema.Mutation, graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)