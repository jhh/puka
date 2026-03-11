import django_filters
from django import forms
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F

from puka.bookmarks.models import Bookmark
from puka.core.filters import TagFilter

YEAR_CHOICES = [(year, str(year)) for year in range(2004, 2027) if year not in (2012, 2013, 2015)]


def filter_full_text_search(queryset, _name, value):
    query = SearchQuery(value, search_type="websearch", config="english")
    return (
        queryset.annotate(rank=SearchRank(F("title_description_search"), query))
        .filter(rank__gte=0.1)
        .order_by("-rank")
    )


class BookmarkFilter(django_filters.FilterSet):
    text = django_filters.CharFilter(
        method=filter_full_text_search,
        label="Title or description contains words",
        widget=forms.TextInput(attrs={"class": "input w-full"}),
    )
    created = django_filters.ChoiceFilter(
        field_name="created",
        lookup_expr="year",
        label="Year created",
        empty_label="Any",
        choices=YEAR_CHOICES,
        widget=forms.Select(attrs={"class": "select leading-4"}),
    )
    url = django_filters.CharFilter(lookup_expr="icontains")
    tags = TagFilter(field_name="tags__name")
    active = django_filters.ChoiceFilter(
        field_name="active",
        label="Active",
        empty_label="Any",
        choices=[(True, "Yes"), (False, "No")],
        widget=forms.Select(attrs={"class": "select leading-4"}),
    )

    class Meta:
        model = Bookmark
        fields = ("text", "created", "url", "tags", "active")
