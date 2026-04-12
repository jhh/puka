from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods


@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    return redirect("login")
