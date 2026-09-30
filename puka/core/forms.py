"""
Form rendering: daisyUI classes on widgets, and a renderer that uses the project templates.

Markup around each widget (label, help text, errors, grid) lives in the ``<c-form.*>`` Cotton
components; this module only adds the daisyUI class to the widget itself, which templates
can't do. It's installed for every form through ``FORM_RENDERER``.
"""

from __future__ import annotations

from django.forms import BoundField
from django.forms.renderers import TemplatesSetting

# widget_type -> (base class, error class). Full class names so Tailwind finds them.
WIDGET_CLASSES: dict[str, tuple[str, str]] = {
    "textarea": ("textarea w-full", "textarea-error"),
    "select": ("select w-full", "select-error"),
    "selectmultiple": ("select w-full", "select-error"),
    "nullbooleanselect": ("select w-full", "select-error"),
    "checkbox": ("checkbox", "checkbox-error"),
    "file": ("file-input w-full", "file-input-error"),
    "clearablefile": ("file-input w-full", "file-input-error"),
}
INPUT_CLASSES = ("input w-full", "input-error")
UNSTYLED = {"hidden", "multiplehidden", "radioselect", "checkboxselectmultiple"}


class DaisyBoundField(BoundField):
    def build_widget_attrs(self, attrs, widget=None):
        attrs = super().build_widget_attrs(attrs, widget)
        widget = widget or self.field.widget
        if self.widget_type in UNSTYLED or widget.is_hidden:
            return attrs
        base, error = WIDGET_CLASSES.get(self.widget_type, INPUT_CLASSES)
        # These attrs replace widget.attrs["class"] when rendered, so keep it.
        classes = [base, str(widget.attrs.get("class", "")), str(attrs.get("class", ""))]
        if self.errors:
            classes.append(error)
        attrs["class"] = " ".join(c for c in classes if c)
        return attrs


class FormRenderer(TemplatesSetting):
    """Render forms with ``settings.TEMPLATES`` (so Cotton components work) and daisyUI widgets."""

    bound_field_class = DaisyBoundField
    form_template_name = "forms/default.html"
