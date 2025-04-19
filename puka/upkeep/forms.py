from crispy_forms.bootstrap import StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Field, Layout, Submit
from django import forms
from django.urls import reverse

from puka.core.forms import CancelButton, DeleteButton, PrimaryButton

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
                CancelButton("cancel", "Cancel", onclick="window.history.back();"),
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
                CancelButton("cancel", "Cancel", onclick="window.history.back();"),
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
        is_edit = self.instance.id is not None

        self.helper = FormHelper()
        self.helper.render_hidden_fields = True
        self.helper.form_method = "post"
        self.helper.form_action = (
            reverse("schedule_edit", args=[self.instance.id])
            if is_edit
            else reverse("schedule_new")
        )

        tasks = Task.objects.select_related().values_list("id", "area__name", "name")
        self.fields["task"].choices = [(t[0], f"{t[1]}: {t[2]}") for t in tasks]  # type:ignore[attr-defined]

        self.helper.layout = Layout(
            Field("task"),
            Field("due_date", css_class="form-control"),
            Field("completion_date", css_class="form-control"),
            Field("notes", css_class="form-control"),
            Div(
                Submit(
                    "submit",
                    "Update" if is_edit else "Save",
                    css_class="btn btn-primary",
                ),
                StrictButton(
                    "Cancel",
                    name="cancel",
                    css_class="btn-secondary ms-2",
                    onclick="window.history.back();",
                ),
                HTML(f"""<button type="button" class="btn btn-outline-danger ms-auto"
                hx-delete="{{% url 'schedule_edit' {self.instance.id} %}}"
                hx-confirm="Delete this schedule?"
                >Delete</button>""")
                if is_edit
                else None,
                css_class="d-flex",
            ),
        )


class TaskItemForm(forms.ModelForm):
    class Meta:
        model = TaskItem
        fields = ("task", "item", "quantity")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        is_edit = self.instance.id is not None

        self.helper = FormHelper()
        self.helper.form_method = "post"

        self.helper.form_action = (
            reverse("task_consumable_edit", args=[self.instance.id])
            if is_edit
            else reverse("task_consumable_new", args=[self["task"].value()])
        )
        self.helper.layout = Layout(
            Field("task", css_class="form-control"),
            Field("consumable", css_class="form-control"),
            Field("quantity", css_class="form-control"),
            Div(
                Submit(
                    "submit",
                    "Update" if is_edit else "Save",
                    css_class="btn btn-primary",
                ),
                StrictButton(
                    "Cancel",
                    name="cancel",
                    css_class="btn-secondary ms-2",
                    onclick="window.history.back();",
                ),
                HTML(f"""<button type="button" class="btn btn-outline-danger ms-auto"
                hx-delete="{{% url 'task_consumable_edit' {self.instance.id} %}}"
                hx-confirm="Delete this consumable from {self.instance.task.name}?"
                >Delete</button>""")
                if is_edit
                else None,
                css_class="d-flex",
            ),
        )
