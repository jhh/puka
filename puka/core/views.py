from django.http import HttpRequest
from django.shortcuts import render


def get_template(request: HttpRequest, template: str, partial: str) -> list[str]:
    """
    Return a template path based on request type (full page vs htmx partial).

    When the request is an htmx request (indicated by the HX-Request header),
    appends the partial suffix to load a partial template for htmx swaps.

    """
    if request.headers.get("HX-Request"):
        template += partial
    return [template]


def view_404(request):
    return render(request, "404.html", status=404)
