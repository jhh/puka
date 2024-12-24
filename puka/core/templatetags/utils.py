from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def get_current_class(context, url_name):
    request = context["request"]
    return (
        "bg-gray-800 text-white"
        if request.path == reverse(url_name)
        else "text-gray-400 hover:text-white hover:bg-gray-800"
    )
