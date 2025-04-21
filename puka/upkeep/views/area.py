from django.db.models import OuterRef, Prefetch, Subquery
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View
from django_htmx.http import HttpResponseLocation

from puka.core.views import get_template
from puka.upkeep.forms import AreaForm
from puka.upkeep.models import Area, Schedule, Task
from puka.upkeep.services import get_areas_tasks_schedules


class AreaListView(ListView):
    context_object_name = "areas"
    model = Area
    paginate_by = 10
    paginate_orphans = 2

    def get_template_names(self):
        return get_template(self.request, "upkeep/area_list.html", "#list-partial")

    def get_queryset(self):
        query = self.request.GET.get("query", "").strip()
        return get_areas_tasks_schedules(query) if query else get_areas_tasks_schedules()


class AreaDetailView(DetailView):
    model = Area
    context_object_name = "area"

    def get_template_names(self):
        return get_template(self.request, "upkeep/area_detail.html", "#detail-partial")

    def get_queryset(self):
        earliest_due_date_subquery = (
            Schedule.objects.filter(task=OuterRef("pk"), completion_date__isnull=True)
            .order_by("due_date")
            .values("due_date")[:1]
        )
        tasks = Task.objects.annotate(earliest_due_date=Subquery(earliest_due_date_subquery))

        return Area.objects.prefetch_related(Prefetch("tasks", queryset=tasks))


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
        return HttpResponseLocation(reverse("upkeep:area-list"), target="#id_content")
