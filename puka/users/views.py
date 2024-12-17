from django.contrib.auth import logout
from django.views.decorators.http import require_POST
from django_htmx.http import HttpResponseLocation


@require_POST
def logout_view(request):
    logout(request)
    return HttpResponseLocation("/", target="body")
