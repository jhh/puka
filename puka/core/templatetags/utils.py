from urllib.parse import urlparse

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


@register.filter
def domain(url):
    """Extract domain from URL."""
    parsed_url = urlparse(url)
    return parsed_url.netloc
