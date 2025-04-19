import datetime

from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, View
from django_htmx.http import HttpResponseLocation

from puka.core.views import get_template
from puka.upkeep.forms import ScheduleForm
from puka.upkeep.models import Schedule, Task


class ScheduleCreateView(CreateView):
    model = Schedule
    form_class = ScheduleForm

    def get_template_names(self):
        return get_template(self.request, "upkeep/form.html", "#form-partial")

    def get_initial(self):
        initial = super().get_initial()
        task = Task.objects.get(pk=self.kwargs["pk"])
        initial.update({"task": task.id, "due_date": task.next_date()})
        return initial


class ScheduleUpdateView(UpdateView):
    model = Schedule
    form_class = ScheduleForm

    def get_template_names(self):
        return get_template(self.request, "upkeep/form.html", "#form-partial")


class ScheduleDeleteView(View):
    def post(self, _request, pk):
        schedule = get_object_or_404(Schedule, pk=pk)
        task_id = schedule.task_id
        schedule.delete()
        return HttpResponseLocation(
            reverse("upkeep:task-detail", args=[task_id]),
            target="#id_content",
        )


class ScheduleToggleView(View):
    http_method_names = ("patch",)

    def patch(self, _request, pk):
        schedule = get_object_or_404(Schedule, pk=pk)
        if schedule.completion_date:
            schedule.completion_date = None
        else:
            schedule.completion_date = datetime.datetime.now(datetime.UTC).date()
        schedule.save()
        return HttpResponseLocation(
            reverse("upkeep:task-detail", args=[schedule.task.id]),
            target="#id_content",
        )
