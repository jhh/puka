import datetime

from dateutil.relativedelta import relativedelta
from django.db import models
from django.urls import reverse

from puka.stuff.models import Item


class Area(models.Model):
    name = models.CharField("area name", max_length=200)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def first_due_schedule(self) -> "Schedule | None":
        schedules: list[Schedule] = []
        for task in self.tasks.prefetch_related("schedules").all():
            schedules += task.schedules.filter(completion_date__isnull=True).all()
        return min(schedules, key=lambda s: s.due_date) if schedules else None


class TaskManager(models.Manager):
    def search(self, _query):
        return self.order_by("area__name", "name")

    def get_upcoming_due_tasks(self, within_days: int = 14, start_date=None):
        if start_date is None:
            start_date = datetime.datetime.now(tz=datetime.UTC).date()
        return self.filter(
            schedules__due_date__lte=start_date + datetime.timedelta(days=within_days),
            schedules__completion_date__isnull=True,
        ).order_by("schedules__due_date")


class Task(models.Model):
    name = models.CharField("task name", max_length=200)
    notes = models.TextField(blank=True)
    duration = models.DurationField(blank=True, null=True)
    interval = models.PositiveIntegerField(blank=True, null=True)
    frequency = models.CharField(
        max_length=10,
        choices=[("days", "Days"), ("weeks", "Weeks"), ("months", "Months")],
        default="months",
    )
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="tasks")
    objects = TaskManager()

    def __str__(self):
        return f"{self.name} ({self.id})"

    def get_absolute_url(self):
        return reverse("upkeep:task-detail", args=[self.id])

    def is_recurring(self) -> bool:
        return self.interval is not None

    def next_date(self, start_date=None) -> datetime.date:
        if start_date is None:
            start_date = datetime.datetime.now(tz=datetime.UTC).date()

        if not self.interval:
            return start_date

        match self.frequency:
            case "days":
                return start_date + relativedelta(days=self.interval)
            case "weeks":
                return start_date + relativedelta(weeks=self.interval)
            case "months":
                return start_date + relativedelta(months=self.interval)
            case _:
                error_msg = f"Invalid frequency: {self.frequency}"
                raise ValueError(error_msg)

    def first_due_schedule(self) -> "Schedule | None":
        return self.schedules.filter(completion_date__isnull=True).order_by("due_date").first()

    def are_consumables_stocked(self) -> bool:
        task_consumables = TaskItem.objects.filter(task=self)
        is_ready = True
        for tc in task_consumables:
            if tc.quantity > tc.item.quantity():
                is_ready = False
        return is_ready


class TaskItem(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField("quantity required", default=1)

    class Meta:
        unique_together = ("task", "item")

    def __str__(self):
        return f"{self.task.name} - {self.item.name} ({self.quantity})"

    def get_absolute_url(self):
        return reverse("upkeep:task-detail", args=[self.task.id])


class Schedule(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="schedules")
    due_date = models.DateField()
    completion_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("due_date",)

    def __str__(self):
        return f"{self.task.name} due on {self.due_date}"

    def get_absolute_url(self):
        return reverse("upkeep:task-detail", args=[self.task.id])

    def is_complete(self) -> bool:
        return self.completion_date is not None

    def reschedule(self):
        start_date = self.completion_date or datetime.datetime.now(tz=datetime.UTC).date()
        next_date = self.task.next_date(start_date)
        if not next_date:
            error_msg = "Cannot reschedule a non-recurring task"
            raise ValueError(error_msg)
        Schedule.objects.create(task=self.task, due_date=next_date)
