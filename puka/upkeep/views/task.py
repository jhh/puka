from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.views.generic import DetailView, ListView

from puka.core.views import get_template
from puka.upkeep.models import Task, TaskItem
from puka.upkeep.services import get_tasks_with_earliest_due_date


class TaskListView(ListView):
    context_object_name = "tasks"
    paginate_by = 10
    paginate_orphans = 2

    def get_template_names(self):
        return get_template(self.request, "upkeep/task_list.html", "#list-partial")

    def get_queryset(self):
        if "query" in self.request.GET:
            query_text = self.request.GET["query"]
            search_query = SearchQuery(query_text)
            query_set = (
                Task.objects.annotate(
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

    def get_object(self):
        pk = self.kwargs.get("pk")
        task = (
            Task.objects.select_related("area")
            .prefetch_related("schedules")
            .order_by("schedules__due_date")
            .get(pk=pk)
        )
        self.extra_context = {"task_consumables": list(TaskItem.objects.filter(task=task))}
        return task
