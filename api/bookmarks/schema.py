from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from graphene import Int, List, ObjectType, String
from graphene_django import DjangoObjectType
from graphql import GraphQLError

from .models import Bookmark


class BookmarkType(DjangoObjectType):
    class Meta:
        model = Bookmark


class Query(ObjectType):
    bookmarks = List(
        BookmarkType,
        search=String(),
        offset=Int(default_value=0),
        limit=Int(default_value=10),
    )

    def resolve_bookmarks(self, info, offset, limit, search=None):
        if search:
            vector = SearchVector("title", weight="A") + SearchVector(
                "description", weight="B"
            )
            query = SearchQuery(search, search_type="websearch", config="english")
            return (
                Bookmark.objects.annotate(rank=SearchRank(vector, query))
                .filter(rank__gte=0.1)
                .order_by("-rank")[offset : offset + limit]
            )

        return Bookmark.objects.exclude(description__exact="")[offset : offset + limit]
