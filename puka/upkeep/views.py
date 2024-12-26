from django.shortcuts import render


def home_view(request):
    return render(request, "upkeep/home.html#home-partial" if request.htmx else "upkeep/home.html")
