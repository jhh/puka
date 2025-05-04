import logging
from datetime import UTC, datetime, timedelta

from django.core.mail import send_mail
from django.core.management import BaseCommand
from django.template.loader import render_to_string

from puka.upkeep.services import get_tasks_with_earliest_due_date

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *_args, **_options):
        within_days = datetime.now(UTC).date() + timedelta(days=1)
        tasks = (
            get_tasks_with_earliest_due_date()
            .select_related("area")
            .filter(earliest_due_date__lte=within_days, earliest_due_date__isnull=False)
            .order_by("earliest_due_date")
        )

        if not tasks:
            logger.info("No upcoming due tasks found")
            return

        context = {
            "tasks": tasks,
            "period": "within the next day",
        }
        text_content = render_to_string("upkeep/notify_email.txt", context)
        html_content = render_to_string("upkeep/notify_email.html", context)
        send_mail(
            "Upkeep Task Notification",
            text_content,
            html_message=html_content,
            from_email="Upkeep Home Maintenance Tracker <upkeep@j3ff.io>",
            recipient_list=["jeff@j3ff.io"],
            fail_silently=False,
        )
