from django.db.models import Sum
from django.views.generic import DetailView, ListView

from puka.core.views import get_template
from puka.stuff.models import Item
from puka.upkeep.models import Task, TaskItem


class TaskListView(ListView):
    context_object_name = "items"
    paginate_by = 10

    def get_template_names(self):
        return get_template(self.request, "stuff/item_list.html", "#list-partial")

    def get_queryset(self):
        if "query" in self.request.GET:
            query = self.request.GET["query"]
            query_set = Item.objects.search(query)
            self.extra_context = {"query": query}
        else:
            query_set = Item.objects.all().order_by("name")

        return (
            query_set.annotate(quantity=Sum("inventories__quantity"))
            .prefetch_related("locations")
            .prefetch_related("tags")
        )


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
