from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, View
from django_htmx.http import HttpResponseLocation

from puka.core.views import get_template
from puka.upkeep.forms import TaskItemForm
from puka.upkeep.models import TaskItem


class TaskItemCreateView(CreateView):
    model = TaskItem
    form_class = TaskItemForm

    def get_template_names(self):
        return get_template(self.request, "upkeep/form.html", "#form-partial")

    def get_initial(self):
        return {"task": self.kwargs["pk"], "quantity": 1}


class TaskItemUpdateView(UpdateView):
    model = TaskItem
    form_class = TaskItemForm

    def get_template_names(self):
        return get_template(self.request, "upkeep/form.html", "#form-partial")


class TaskItemDeleteView(View):
    def post(self, _request, pk):
        task_item = get_object_or_404(TaskItem, pk=pk)
        task_item.delete()
        return HttpResponseLocation(
            reverse("upkeep:task-detail", args=[task_item.task_id]),
            target="#id_content",
        )
