from django.views.generic import ListView

from puka.core.views import get_template
from puka.upkeep.models import Area
from puka.upkeep.services import get_areas_tasks_schedules


class AreaListView(ListView):
    context_object_name = "areas"
    model = Area

    def get_template_names(self):
        return get_template(self.request, "upkeep/area_list.html", "#list-partial")

    def get_queryset(self):
        return get_areas_tasks_schedules()
