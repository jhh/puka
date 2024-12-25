import django_filters
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Layout
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F
from taggit.forms import TagField

from puka.bookmarks.forms import CancelButton, PrimaryButton
from puka.bookmarks.models import Bookmark

YEAR_CHOICES = [(year, str(year)) for year in range(2004, 2025) if year not in (2012, 2013, 2015)]


class TagFilter(django_filters.CharFilter):
    field_class = TagField

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("lookup_expr", "in")
        kwargs.setdefault("distinct", True)
        super().__init__(*args, **kwargs)


def filter_full_text_search(queryset, name, value):
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
    )
    created = django_filters.ChoiceFilter(
        field_name="created",
        lookup_expr="year",
        label="Year created",
        empty_label="Any",
        choices=YEAR_CHOICES,
    )
    url = django_filters.CharFilter(lookup_expr="icontains")
    tags = TagFilter(field_name="tags__name")

    class Meta:
        model = Bookmark
        fields = ["text", "created", "url", "tags", "active"]

    @property
    def form(self):
        form = super().form
        form.helper = FormHelper()
        form.helper.form_method = "GET"
        form.helper.attrs = {"hx-get": "", "hx-target": "#id_content"}
        form.helper.layout = Layout(
            Div(
                Field("text", wrapper_class="sm:col-span-3"),
                Field("tags", wrapper_class="sm:col-span-3"),
                Field("created", wrapper_class="sm:col-span-1"),
                Field("active", wrapper_class="sm:col-span-1"),
                Field("url", wrapper_class="sm:col-span-4"),
                css_class="grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-6",
            ),
            Div(
                CancelButton("clear", "Clear Search", onclick="clearSearch();", hx_get=""),
                PrimaryButton("submit", "Search"),
                css_class="mt-0 mb-4 flex items-center justify-end gap-x-6",
            ),
        )
        return form
