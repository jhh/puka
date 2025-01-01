from django.shortcuts import render


def view_404(request):
    return render(request, "404.html", status=404)
