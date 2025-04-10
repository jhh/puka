# Register your models here.

from django.contrib import admin

from puka.upkeep.models import Area, Schedule, Task

admin.site.register(Area)
admin.site.register(Task)
admin.site.register(Schedule)
