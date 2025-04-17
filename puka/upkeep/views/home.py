from django.views.generic import ListView

from puka.core.views import get_template
from puka.upkeep.services import get_upcoming_due_tasks


class HomeListView(ListView):
    context_object_name = "tasks"
    paginate_by = 10

    def get_template_names(self):
        return get_template(self.request, "upkeep/home_list.html", "#list-partial")

    def get_queryset(self):
        return get_upcoming_due_tasks(within_days=14)
