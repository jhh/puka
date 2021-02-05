from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import F
from graphene import Int, List, ObjectType, String
from graphene_django import DjangoObjectType
from graphql import GraphQLError

from .models import Bookmark


class BookmarkType(DjangoObjectType):
    class Meta:
        model = Bookmark
        fields = ("id", "title", "description", "url", "tags", "created_at")


class Query(ObjectType):
    bookmarks = List(
        BookmarkType,
        search=String(),
        offset=Int(default_value=0),
        limit=Int(default_value=10),
    )

    def resolve_bookmarks(self, info, offset, limit, search=None):
        if search:
            query = SearchQuery(search, search_type="websearch", config="english")
            return (
                Bookmark.objects.annotate(
                    rank=SearchRank(F("title_description_search"), query)
                )
                .filter(rank__gte=0.1)
                .order_by("-rank")[offset : offset + limit]
            )

        return Bookmark.objects.all()[offset : offset + limit]
