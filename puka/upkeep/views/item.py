from typing import cast

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

    def get_form(self, form_class=None):
        form = cast("TaskItemForm", super().get_form(form_class))
        form.cancel_url = reverse("upkeep:task-detail", args=[self.kwargs["pk"]])
        return form


class TaskItemUpdateView(UpdateView):
    model = TaskItem
    form_class = TaskItemForm

    def get_template_names(self):
        return get_template(self.request, "upkeep/form.html", "#form-partial")

    def get_form(self, form_class=None):
        form = cast("TaskItemForm", super().get_form(form_class))
        form.cancel_url = reverse("upkeep:task-detail", args=[self.object.task_id])
        return form


class TaskItemDeleteView(View):
    def post(self, _request, pk):
        task_item = get_object_or_404(TaskItem, pk=pk)
        task_item.delete()
        return HttpResponseLocation(
            reverse("upkeep:task-detail", args=[task_item.task_id]),
            target="#content",
        )
