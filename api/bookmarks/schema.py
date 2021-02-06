from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import F
from graphene import Int, List, ObjectType, String
import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError

from .models import Bookmark


class BookmarkType(DjangoObjectType):
    class Meta:
        model = Bookmark
        exclude = ("title_description_search",)


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

        return Bookmark.objects.all().order_by("-created_at")[offset : offset + limit]


class CreateBookmark(graphene.Mutation):
    bookmark = graphene.Field(BookmarkType)

    class Arguments:
        title = graphene.String()
        description = graphene.String()
        url = graphene.String()
        tags = graphene.List(graphene.String)

    def mutate(self, info, title, description, url, tags):
        user = info.context.user or None
        if user.is_anonymous:
            raise GraphQLError("Log in to create bookmark.")

        bookmark = Bookmark(title=title, description=description, url=url, tags=tags)
        bookmark.save()
        return CreateBookmark(bookmark=bookmark)


class UpdateBookmark(graphene.Mutation):
    bookmark = graphene.Field(BookmarkType)

    class Arguments:
        bookmark_id = graphene.Int(required=True)
        title = graphene.String()
        description = graphene.String()
        url = graphene.String()
        tags = graphene.List(graphene.String)

    def mutate(self, info, bookmark_id, title, description, url, tags):
        user = info.context.user or None
        if user.is_anonymous:
            raise GraphQLError("Log in to update bookmark.")

        bookmark = Bookmark.objects.get(id=bookmark_id)
        bookmark.title = title
        bookmark.description = description
        bookmark.url = url
        bookmark.tags = tags
        bookmark.save()
        return UpdateBookmark(bookmark=bookmark)


class DeleteBookmark(graphene.Mutation):
    bookmark_id = graphene.Int()

    class Arguments:
        bookmark_id = graphene.Int(required=True)

    def mutate(self, info, bookmark_id):
        user = info.context.user or None
        if user.is_anonymous:
            raise GraphQLError("Log in to update bookmark.")

        bookmark = Bookmark.objects.get(id=bookmark_id)
        bookmark.delete()
        return DeleteBookmark(bookmark_id=bookmark_id)


class Mutation(graphene.ObjectType):
    create_bookmark = CreateBookmark.Field()
    update_bookmark = UpdateBookmark.Field()
    delete_bookmark = DeleteBookmark.Field()