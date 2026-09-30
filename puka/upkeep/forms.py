from django import forms

from puka.stuff.models import Item

from .models import Area, Schedule, Task, TaskItem


def _task_choices():
    tasks = Task.objects.values_list("id", "area__name", "name")
    return [(pk, f"{area}: {name}") for pk, area, name in tasks]


class AreaForm(forms.ModelForm):
    template_name = "upkeep/forms/area.html"

    class Meta:
        model = Area
        fields = ("name", "notes")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs["autocomplete"] = "off"
        if self.instance.pk is None:
            self.fields["name"].widget.attrs["autofocus"] = True


class TaskForm(forms.ModelForm):
    template_name = "upkeep/forms/task.html"

    class Meta:
        model = Task
        fields = ("area", "name", "interval", "frequency", "notes")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs["autocomplete"] = "off"
        if self.instance.pk is None:
            self.fields["name"].widget.attrs["autofocus"] = True


class ScheduleForm(forms.ModelForm):
    template_name = "upkeep/forms/schedule.html"

    class Meta:
        model = Schedule
        fields = ("task", "due_date", "completion_date", "notes")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["task"].choices = _task_choices()  # ty: ignore[unresolved-attribute]


class TaskItemForm(forms.ModelForm):
    template_name = "upkeep/forms/task_item.html"

    class Meta:
        model = TaskItem
        fields = ("task", "item", "quantity")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["task"].choices = _task_choices()  # ty: ignore[unresolved-attribute]
        # A queryset (not just choices) so validation also rejects other items.
        item = self.fields["item"]
        item.queryset = Item.objects.filter(tags__name="upkeep").order_by("name")  # ty: ignore[unresolved-attribute]
        item.empty_label = "---"  # ty: ignore[unresolved-attribute]
