from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Layout
from django import forms
from django.urls import reverse

from puka.core.forms import CancelButton, DeleteButton, PrimaryButton
from puka.stuff.models import Item

from .models import Area, Schedule, Task, TaskItem


class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ("name", "notes")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.id:
            action = reverse("upkeep:area-edit", args=[self.instance.id])
            delete_button = DeleteButton("upkeep:area-delete", self.instance.id, "area")
            autofocus = {}
        else:
            action = reverse("upkeep:area-new")
            delete_button = None
            autofocus = {"autofocus": ""}

        self.helper = FormHelper()
        self.helper.attrs = {"hx-post": action}
        self.helper.layout = Layout(
            Div(
                Field("name", wrapper_class="sm:col-span-6", autocomplete="off", **autofocus),
                Field("notes", wrapper_class="sm:col-span-6"),
                css_class="grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-6",
            ),
            Div(
                PrimaryButton("submit", "Save area"),
                CancelButton("upkeep:area-list"),
                delete_button,
                css_class="mt-4 flex gap-x-4",
            ),
        )


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ("area", "name", "interval", "frequency", "notes")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.id:
            action = reverse("upkeep:task-edit", args=[self.instance.id])
            delete_button = DeleteButton("upkeep:task-delete", self.instance.id, "task")
            autofocus = {}
        else:
            action = reverse("upkeep:task-new")
            delete_button = None
            autofocus = {"autofocus": ""}

        self.helper = FormHelper()
        self.helper.attrs = {"hx-post": action}
        self.helper.layout = Layout(
            Div(
                Field("name", wrapper_class="sm:col-span-6", autocomplete="off", **autofocus),
                Field("area", wrapper_class="sm:col-span-6"),
                Field("interval", wrapper_class="sm:col-span-3"),
                Field("frequency", wrapper_class="sm:col-span-3"),
                Field("notes", wrapper_class="sm:col-span-6"),
                css_class="grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-6",
            ),
            Div(
                PrimaryButton("submit", "Save task"),
                CancelButton("upkeep:task-list"),
                delete_button,
                css_class="mt-4 flex gap-x-4",
            ),
        )


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ("task", "due_date", "completion_date", "notes")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:
            action = reverse("upkeep:schedule-edit", args=[self.instance.id])
            delete_button = DeleteButton("upkeep:schedule-delete", self.instance.id, "schedule")
        else:
            action = reverse("upkeep:schedule-new", args=[self.initial["task"]])
            delete_button = None

        self.helper = FormHelper()
        self.helper.attrs = {"hx-post": action}

        tasks = Task.objects.select_related().values_list("id", "area__name", "name")
        self.fields["task"].choices = [(t[0], f"{t[1]}: {t[2]}") for t in tasks]  # type:ignore[attr-defined]

        self.helper.layout = Layout(
            Div(
                Field("task", wrapper_class="sm:col-span-6"),
                Field("due_date", wrapper_class="sm:col-span-3"),
                Field("completion_date", wrapper_class="sm:col-span-3"),
                Field("notes", wrapper_class="sm:col-span-6"),
                css_class="grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-6",
            ),
            Div(
                PrimaryButton("submit", "Save schedule"),
                CancelButton("upkeep:home"),
                delete_button,
                css_class="mt-4 flex gap-x-4",
            ),
        )


class TaskItemForm(forms.ModelForm):
    class Meta:
        model = TaskItem
        fields = ("task", "item", "quantity")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:
            action = reverse("upkeep:task-item-edit", args=[self.instance.id])
            delete_button = DeleteButton("upkeep:task-item-delete", self.instance.id, "item")
        else:
            action = reverse("upkeep:task-item-new", args=[self.initial["task"]])
            delete_button = None

        self.helper = FormHelper()
        self.helper.attrs = {"hx-post": action}

        tasks = Task.objects.select_related().values_list("id", "area__name", "name")
        self.fields["task"].choices = [(t[0], f"{t[1]}: {t[2]}") for t in tasks]  # type:ignore[attr-defined]
        items = (
            Item.objects.filter(tags__name__in=["upkeep"])
            .order_by("name")
            .values_list("id", "name")
        )
        self.fields["item"].choices = [(None, "---")] + [(i[0], i[1]) for i in items]  # type:ignore[attr-defined]

        self.helper.layout = Layout(
            Div(
                Field("task", wrapper_class="sm:col-span-6"),
                Field("item", wrapper_class="sm:col-span-6"),
                Field("quantity", wrapper_class="sm:col-span-3"),
                css_class="grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-6",
            ),
            Div(
                PrimaryButton("submit", "Save item"),
                CancelButton("upkeep:home"),
                delete_button,
                css_class="mt-4 flex gap-x-4",
            ),
        )
