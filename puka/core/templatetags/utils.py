from urllib.parse import urlparse

from django import template

register = template.Library()


@register.filter
def domain(url):
    """Extract domain from URL."""
    parsed_url = urlparse(url)
    return parsed_url.netloc
