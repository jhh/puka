from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View
from django_htmx.http import HttpResponseLocation

from puka.core.views import get_template
from puka.upkeep.forms import TaskForm
from puka.upkeep.models import Task, TaskItem
from puka.upkeep.services import get_tasks_with_earliest_due_date


class TaskListView(ListView):
    context_object_name = "tasks"
    paginate_by = 10
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
                .order_by("area__name", "name")
            )

        return query_set


class TaskDetailView(DetailView):
    model = Task
    context_object_name = "task"

    def get_template_names(self):
        return get_template(self.request, "upkeep/task_detail.html", "#detail-partial")

    def get_object(self, _queryset=None):
        pk = self.kwargs.get("pk")
        task = (
            Task.objects.select_related("area")
            .prefetch_related("schedules")
            .order_by("schedules__due_date")
            .get(pk=pk)
        )
        self.extra_context = {"task_consumables": list(TaskItem.objects.filter(task=task))}
        return task


class TaskCreateView(CreateView):
    model = Task
    form_class = TaskForm

    def get_template_names(self):
        return get_template(self.request, "upkeep/form.html", "#form-partial")

    def get_initial(self):
        return {"area": self.request.GET.get("area")}


class TaskUpdateView(UpdateView):
    model = Task
    form_class = TaskForm

    def get_template_names(self):
        return get_template(self.request, "upkeep/form.html", "#form-partial")


class TaskDeleteView(View):
    def post(self, _request, pk):
        task = get_object_or_404(Task, pk=pk)
        task.delete()
        return HttpResponseLocation(reverse("upkeep:task-list"), target="#id_content")
