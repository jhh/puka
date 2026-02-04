from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def get_current_class(context, url_name):
    request = context["request"]
    return (
        "active text-neutral-content"
        if request.path.startswith(reverse(url_name))
        else "text-neutral-content/70 hover:text-neutral-content hover:bg-neutral-focus"
    )
