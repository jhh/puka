from typing import cast

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import F, OuterRef, Prefetch, Q, Subquery
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View
from django_htmx.http import HttpResponseLocation

from puka.core.pagination import PageSizeMixin
from puka.core.views import get_template
from puka.upkeep.forms import TaskForm
from puka.upkeep.models import Schedule, Task, TaskItem
from puka.upkeep.services import get_tasks_with_earliest_due_date


class TaskListView(PageSizeMixin, ListView):
    context_object_name = "tasks"
    paginate_orphans = 2

    def get_template_names(self):
        return get_template(self.request, "upkeep/task_list.html", "#list-partial")

    def get_queryset(self):
        # TODO(jhh): make query an optional arg to get_tasks_with_earliest_due_date
        query_text = self.request.GET.get("query", "").strip()
        if query_text:
            search_query = SearchQuery(query_text)
            query_set = (
                get_tasks_with_earliest_due_date()
                .select_related("area")
                .annotate(
                    search_vector=SearchVector("name", weight="A")
                    + SearchVector("notes", weight="B")
                    + SearchVector("area__name", weight="B"),
                    rank=SearchRank("search_vector", search_query),
                )
                .filter(search_vector=search_query)
                .order_by("-rank")
            )
        else:
            query_set = (
                get_tasks_with_earliest_due_date()
                .select_related("area")
                .order_by(F("earliest_due_date").asc(nulls_last=True), "pk")
            )

        return query_set


class TaskDetailView(DetailView):
    model = Task
    context_object_name = "task"

    def get_template_names(self):
        return get_template(self.request, "upkeep/task_detail.html", "#detail-partial")

    def get_object(self, queryset=None) -> Task:
        pk = self.kwargs.get("pk")
        if queryset is None:
            latest_complete = (
                Schedule.objects.filter(task=OuterRef("task_id"), completion_date__isnull=False)
                .order_by("-completion_date", "-pk")
                .values("pk")[:1]
            )
            queryset = Task.objects.select_related("area").prefetch_related(
                Prefetch(
                    "schedules",
                    queryset=Schedule.objects.filter(
                        Q(completion_date__isnull=True) | Q(pk=Subquery(latest_complete)),
                    ),
                ),
            )

        task = queryset.order_by("schedules__due_date").get(pk=pk)
        self.extra_context = {
            "task_consumables": list(TaskItem.objects.with_stock_quantities().filter(task=task)),
        }
        return task


class TaskCreateView(CreateView):
    model = Task
    form_class = TaskForm

    def get_template_names(self):
        return get_template(self.request, "upkeep/form.html", "#form-partial")

    def get_initial(self):
        return {"area": self.request.GET.get("area")}

    def get_form(self, form_class=None):
        form = cast("TaskForm", super().get_form(form_class))
        area = self.request.GET.get("area")
        form.cancel_url = (
            reverse("upkeep:area-detail", args=[area]) if area else reverse("upkeep:task-list")
        )
        return form


class TaskUpdateView(UpdateView):
    model = Task
    form_class = TaskForm

    def get_template_names(self):
        return get_template(self.request, "upkeep/form.html", "#form-partial")

    def get_form(self, form_class=None):
        form = cast("TaskForm", super().get_form(form_class))
        form.cancel_url = reverse("upkeep:task-detail", args=[self.object.pk])
        return form


class TaskDeleteView(View):
    def post(self, _request, pk):
        task = get_object_or_404(Task, pk=pk)
        task.delete()
        return HttpResponseLocation(reverse("upkeep:task-list"), target="#content")
