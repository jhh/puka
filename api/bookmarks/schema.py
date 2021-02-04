from graphene import Int, List, ObjectType
from graphene_django import DjangoObjectType
from graphql import GraphQLError

from .models import Bookmark


class BookmarkType(DjangoObjectType):
    class Meta:
        model = Bookmark


class Query(ObjectType):
    bookmarks = List(
        BookmarkType, offset=Int(default_value=0), limit=Int(default_value=10)
    )

    def resolve_bookmarks(self, info, offset, limit):
        return Bookmark.objects.exclude(description__exact="")[offset : offset + limit]
