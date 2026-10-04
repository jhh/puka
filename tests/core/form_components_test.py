"""The <c-form.*> components and the daisyUI form renderer (puka.core.forms)."""

from __future__ import annotations

import pytest
from django import forms
from django.test import RequestFactory

from puka.core.forms import DaisyBoundField, FormRenderer
from tests.core.components_test import classes, page, render
from tests.utils import parse_html


class SampleForm(forms.Form):
    name = forms.CharField(help_text="Shown in lists.")
    notes = forms.CharField(widget=forms.Textarea, required=False)
    kind = forms.ChoiceField(choices=[("a", "A"), ("b", "B")])
    active = forms.BooleanField(required=False, label="Is active")
    count = forms.IntegerField(required=False)
    when = forms.DateField(required=False)
    link = forms.URLField(required=False)
    upload = forms.FileField(required=False)
    secret = forms.CharField(widget=forms.HiddenInput, required=False)
    styled = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "font-mono"}))

    def clean(self):
        if self.cleaned_data.get("name") == "bad":
            msg = "Something is wrong."
            raise forms.ValidationError(msg)


def test_renderer_is_installed():
    form = SampleForm()
    assert isinstance(form.renderer, FormRenderer)
    assert isinstance(form["name"], DaisyBoundField)


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("name", ["input", "w-full"]),
        ("count", ["input", "w-full"]),
        ("when", ["input", "w-full"]),
        ("link", ["input", "w-full"]),
        ("notes", ["textarea", "w-full"]),
        ("kind", ["select", "w-full"]),
        ("active", ["checkbox"]),
        ("upload", ["file-input", "w-full"]),
        ("styled", ["input", "w-full", "font-mono"]),
    ],
)
def test_widget_classes(name, expected):
    el = parse_html(str(SampleForm()[name])).elements[0]
    assert classes(el) == expected


def test_hidden_widget_unstyled():
    assert "class" not in parse_html(str(SampleForm()["secret"])).elements[0].attrs


@pytest.mark.parametrize(
    ("name", "error_class"),
    [("name", "input-error"), ("kind", "select-error")],
)
def test_widget_error_class(name, error_class):
    form = SampleForm(data={"kind": "zzz"})
    assert not form.is_valid()
    el = parse_html(str(form[name])).elements[0]
    assert error_class in classes(el)
    assert el.attrs["aria-invalid"] == "true"


def test_field():
    form = SampleForm(data={"kind": "a"})
    form.is_valid()
    result = page('<c-form.field :field="form.name" class="sm:col-span-4" />', form=form)

    fieldset = result.elements[0]
    assert fieldset.tag == "fieldset"
    assert classes(fieldset) == ["fieldset", "sm:col-span-4"]
    label = result.find("label")[0]
    assert label.attrs["for"] == "id_name"
    assert label.text == "Name"
    assert result.find("span")[0].text == "*"
    field = result.field("name")
    assert field.attrs["aria-describedby"] == "id_name_helptext id_name_error"
    help_text, error = result.find("p")
    assert (help_text.attrs["id"], help_text.text) == ("id_name_helptext", "Shown in lists.")
    assert (error.attrs["id"], error.text) == ("id_name_error", "This field is required.")
    assert "text-error" in classes(error)


def test_field_label_override_and_optional():
    result = page('<c-form.field :field="form.notes" label="Remarks" />', form=SampleForm())
    assert result.find("label")[0].text == "Remarks"
    assert not result.find("span")
    assert not result.find("p")


def test_checkbox_field_label_wraps_box():
    result = page('<c-form.field :field="form.active" />', form=SampleForm())
    (label,) = result.find("label")
    checkbox = result.field("active")
    # The parser attaches text to the last opened element: the box, inside the label.
    assert result.elements.index(checkbox) == result.elements.index(label) + 1
    assert checkbox.text == "Is active"


def test_hidden_field_is_bare():
    result = page('<c-form.field :field="form.secret" />', form=SampleForm())
    assert [el.tag for el in result.elements] == ["input"]


def test_fields_renders_visible_then_hidden():
    result = page('<c-form.fields :form="form" />', form=SampleForm())
    assert len(result.find("fieldset")) == 9
    assert result.elements[-1].attrs["name"] == "secret"


def test_default_form_template():
    html = str(SampleForm())
    assert "<c-" not in html
    assert len(parse_html(html).find("fieldset")) == 9


def test_form_post_with_htmx_action():
    request = RequestFactory().get("/")
    source = '<c-form.form action="/save/" :form="form" hx-target="#content">x</c-form.form>'
    result = page(source, request, form=SampleForm())
    (form,) = result.forms
    assert form.attrs["method"] == "post"
    assert form.attrs["hx-post"] == "/save/"
    assert form.attrs["hx-target"] == "#content"
    assert classes(form) == ["space-y-4"]
    assert result.find("input", name="csrfmiddlewaretoken")


def test_form_preserves_explicit_target_when_rendering_invalid_fields():
    form = SampleForm(data={"name": "bad", "kind": "invalid"})
    assert not form.is_valid()
    result = page(
        '<c-form.form action="/save/" :form="form" hx-target="#content">'
        '<c-form.fields :form="form" /></c-form.form>',
        RequestFactory().get("/save/"),
        form=form,
    )
    (rendered_form,) = result.forms
    assert rendered_form.attrs["hx-target"] == "#content"
    assert rendered_form.attrs["hx-post"] == "/save/"
    assert result.field("kind").attrs["aria-invalid"] == "true"
    assert result.find("input", name="csrfmiddlewaretoken")


def test_form_get_plain():
    result = page(
        '<c-form.form method="get" class="mb-4">x</c-form.form>',
        RequestFactory().get("/"),
    )
    (form,) = result.forms
    assert form.attrs["method"] == "get"
    assert "hx-get" not in form.attrs
    assert "hx-post" not in form.attrs
    assert classes(form) == ["mb-4"]
    assert not result.find("input")


def test_form_get_with_htmx_action():
    result = page('<c-form.form method="get" action="/find/">x</c-form.form>')
    assert result.forms[0].attrs["hx-get"] == "/find/"


def test_form_errors():
    form = SampleForm(data={"name": "bad", "kind": "a", "secret": ""})
    form.is_valid()
    form.add_error("secret", "Hidden problem.")
    result = page(
        '<c-form.form :form="form">x</c-form.form>',
        RequestFactory().get("/"),
        form=form,
    )
    alerts = [el for el in result.elements if el.attrs.get("role") == "alert"]
    assert len(alerts) == 2
    assert [el.text for el in result.find("p")] == [
        "Something is wrong.",
        "Secret: Hidden problem.",
    ]


def test_actions():
    source = (
        '<c-form.actions submit="Save area" cancel="/areas/" delete="/areas/1/delete/"'
        ' confirm="Delete this area?" />'
    )
    result = page(source)
    submit, delete = result.find("button")
    assert (submit.attrs["type"], submit.text) == ("submit", "Save area")
    assert "btn-primary" in classes(submit)
    (cancel,) = result.find("a")
    assert cancel.text == "Cancel"
    assert cancel.attrs["href"] == cancel.attrs["hx-get"] == "/areas/"
    assert cancel.attrs["hx-target"] == "#content"
    assert cancel.attrs["hx-push-url"] == "true"
    assert delete.attrs["type"] == "button"
    assert delete.attrs["hx-post"] == "/areas/1/delete/"
    assert delete.attrs["hx-confirm"] == "Delete this area?"
    assert classes(delete) == ["btn", "btn-error", "btn-outline", "ml-auto"]


def test_actions_plain_cancel_and_no_delete():
    result = page('<c-form.actions cancel="/b/" cancel_label="Clear" cancel_target="" />')
    (cancel,) = result.find("a")
    assert cancel.text == "Clear"
    assert "hx-get" not in cancel.attrs
    assert len(result.find("button")) == 1


def test_actions_submit_only():
    html = render("<c-form.actions />")
    result = parse_html(html)
    assert [b.text for b in result.find("button")] == ["Save"]
    assert not result.find("a")
