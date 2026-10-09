from types import MappingProxyType

from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View
from django_htmx.http import HttpResponseLocation

from puka.core.pagination import PageSizeMixin
from puka.core.views import get_template
from puka.upkeep.forms import AreaForm
from puka.upkeep.models import Area
from puka.upkeep.services import get_areas_tasks_schedules, get_tasks_with_earliest_due_date


class AreaListView(PageSizeMixin, ListView):
    context_object_name = "areas"
    model = Area
    paginate_orphans = 2

    def get_template_names(self):
        return get_template(self.request, "upkeep/area_list.html", "#list-partial")

    def get_queryset(self):
        query = self.request.GET.get("query", "").strip()
        return get_areas_tasks_schedules(query) if query else get_areas_tasks_schedules()


class AreaDetailView(DetailView):
    model = Area
    context_object_name = "area"
    extra_context = MappingProxyType({"bookmark_delete_url": "upkeep:bookmark-delete"})

    def get_template_names(self):
        return get_template(self.request, "upkeep/area_detail.html", "#detail-partial")

    def get_queryset(self):
        return Area.objects.prefetch_related(
            Prefetch("tasks", queryset=get_tasks_with_earliest_due_date()),
            "bookmarks__tags",
        )


class AreaCreateView(CreateView):
    model = Area
    form_class = AreaForm
    success_url = reverse_lazy("upkeep:area-list")

    def get_template_names(self):
        return get_template(self.request, "upkeep/form.html", "#form-partial")


class AreaUpdateView(UpdateView):
    model = Area
    form_class = AreaForm
    success_url = reverse_lazy("upkeep:area-list")

    def get_template_names(self):
        return get_template(self.request, "upkeep/form.html", "#form-partial")


class AreaDeleteView(View):
    def post(self, _request, pk):
        area = get_object_or_404(Area, pk=pk)
        area.delete()
        return HttpResponseLocation(reverse("upkeep:area-list"), target="#content")
