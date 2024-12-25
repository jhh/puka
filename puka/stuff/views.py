from django.shortcuts import render


def home_view(request):
    return render(request, "stuff/home.html#home-partial" if request.htmx else "stuff/home.html")
