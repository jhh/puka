import logging
from datetime import UTC, datetime, timedelta

from django.core.mail import send_mail
from django.core.management import BaseCommand, CommandError
from django.template.loader import render_to_string
from environs import Env

from puka.upkeep.services import get_tasks_with_earliest_due_date

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *_args, **_options):
        env = Env(prefix="PUKA_")
        task_within_date = datetime.now(UTC).date() + env.timedelta(
            "TASK_WITHIN",
            timedelta(days=1),
        )
        supplies_within_date = datetime.now(UTC).date() + env.timedelta(
            "SUPPLIES_WITHIN",
            timedelta(weeks=2),
        )
        if supplies_within_date < task_within_date:
            msg = "SUPPLIES_WITHIN must be greater or equal to TASK_WITHIN"
            raise CommandError(msg)

        tasks_qs = (
            get_tasks_with_earliest_due_date()
            .select_related("area")
            .filter(earliest_due_date__lte=supplies_within_date, earliest_due_date__isnull=False)
            .order_by("earliest_due_date")
        )

        tasks = []

        for task in tasks_qs:
            if not task.are_consumables_stocked():
                tasks.append(task)
                continue
            if task.earliest_due_date <= task_within_date:
                tasks.append(task)

        if not tasks:
            logger.info("No upcoming due tasks found")
            return

        context = {"tasks": tasks}
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
