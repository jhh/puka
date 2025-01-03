from django.http import HttpRequest
from django.shortcuts import render


def get_template(request: HttpRequest, template: str, partial: str):
    if request.headers.get("HX-Request"):
        template += partial
    return [template]


def view_404(request):
    return render(request, "404.html", status=404)
