import graphene

import bookmarks.schema


class Query(bookmarks.schema.Query, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)