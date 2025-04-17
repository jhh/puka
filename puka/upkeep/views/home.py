from datetime import UTC, datetime, timedelta

from django.views.generic import ListView

from puka.core.views import get_template
from puka.upkeep.services import get_tasks_with_earliest_due_date


class HomeListView(ListView):
    context_object_name = "tasks"
    paginate_by = 10

    def get_template_names(self):
        return get_template(self.request, "upkeep/task_list.html", "#list-partial")

    def get_queryset(self):
        # Calculate date 14 days from now
        within_days = datetime.now(UTC).date() + timedelta(days=14)

        return (
            get_tasks_with_earliest_due_date()
            .select_related("area")
            .filter(earliest_due_date__lte=within_days, earliest_due_date__isnull=False)
            .order_by("earliest_due_date")
        )
