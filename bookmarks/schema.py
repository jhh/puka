import django_filters
import graphene
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F
from django_filters.filters import BaseCSVFilter, CharFilter
from graphene import ObjectType, relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_relay import from_global_id

from .models import Bookmark


class CharArrayFilter(BaseCSVFilter, CharFilter):
    pass


class BookmarkFilter(django_filters.FilterSet):
    tags = CharArrayFilter(lookup_expr="overlap")
    search = django_filters.CharFilter(method="filter_search")
    year = django_filters.NumberFilter(field_name="created_at", lookup_expr="year")
    order_by = django_filters.OrderingFilter(fields=("created_at", "title"))

    def filter_search(self, queryset, name, value):
        query = SearchQuery(value, search_type="websearch", config="english")
        return (
            queryset.annotate(rank=SearchRank(F("title_description_search"), query))
            .filter(rank__gte=0.1)
            .order_by("-rank")
        )


class BookmarkNode(DjangoObjectType):
    class Meta:
        model = Bookmark
        exclude = ("title_description_search",)
        filterset_class = BookmarkFilter
        interfaces = (relay.Node,)


class Query(ObjectType):
    bookmark = relay.Node.Field(BookmarkNode)
    all_bookmarks = DjangoFilterConnectionField(BookmarkNode)

    def resolve_all_bookmarks(self, info, **kwargs):
        if info.context.user.is_anonymous:
            raise GraphQLError("Log in to query bookmarks.")
        return Bookmark.objects


class CreateBookmark(relay.ClientIDMutation):
    bookmark = graphene.Field(BookmarkNode)

    class Input:
        title = graphene.String(required=True)
        description = graphene.String()
        url = graphene.String(required=True)
        tags = graphene.List(graphene.String)

    @classmethod
    def mutate_and_get_payload(
        cls, root, info, title, url, description="", tags=[], **kwargs
    ):
        if info.context.user.is_anonymous:
            raise GraphQLError("Log in to create bookmark.")

        bookmark = Bookmark(title=title, description=description, url=url, tags=tags)
        bookmark.save()
        return CreateBookmark(bookmark=bookmark)


class UpdateBookmark(relay.ClientIDMutation):
    bookmark = graphene.Field(BookmarkNode)

    class Input:
        id = graphene.ID(required=True)
        title = graphene.String()
        description = graphene.String()
        url = graphene.String()
        tags = graphene.List(graphene.String)

    @classmethod
    def mutate_and_get_payload(
        cls, root, info, id, title, description, url, tags, **kwargs
    ):
        if info.context.user.is_anonymous:
            raise GraphQLError("Log in to update bookmark.")

        bookmark = Bookmark.objects.get(pk=from_global_id(id)[1])
        bookmark.title = title
        bookmark.description = description
        bookmark.url = url
        bookmark.tags = tags
        bookmark.save()
        return UpdateBookmark(bookmark=bookmark)


class DeleteBookmark(relay.ClientIDMutation):
    id = graphene.ID()

    class Input:
        id = graphene.ID(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, id, **kwargs):
        if info.context.user.is_anonymous:
            raise GraphQLError("Log in to delete bookmark.")

        bookmark = Bookmark.objects.get(pk=from_global_id(id)[1])
        bookmark.delete()
        return DeleteBookmark(id=id)


class Mutation(graphene.ObjectType):
    create_bookmark = CreateBookmark.Field()
    update_bookmark = UpdateBookmark.Field()
    delete_bookmark = DeleteBookmark.Field()
