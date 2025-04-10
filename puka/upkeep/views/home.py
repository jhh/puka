from django.shortcuts import render

from puka.core.views import get_template


def home_view(request):
    template = get_template(request, "upkeep/home.html", "#home-partial")
    return render(request, template, {})
