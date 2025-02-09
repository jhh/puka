from crispy_forms.layout import HTML
from crispy_tailwind.layout import Button, Submit


class PrimaryButton(Submit):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault(
            "css_class",
            "rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-xs "
            "hover:bg-indigo-500 focus-visible:outline-2 focus-visible:outline-offset-2 "
            "focus-visible:outline-indigo-600",
        )
        super().__init__(*args, **kwargs)


class CancelButton(Button):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("css_class", "text-sm/6 font-semibold text-gray-900")
        super().__init__(*args, **kwargs)


class DeleteButton(HTML):
    def __init__(self, url_name, pk, name):
        super().__init__(
            f"""<button type="button"
            class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-red-600 ring-1 shadow-xs ring-red-300 ring-inset hover:bg-gray-50 ml-auto"
            hx-post="{{% url '{url_name}' {pk} %}}" hx-params="none"
            hx-confirm="Delete this {name}?">Delete</button>""",
        )
