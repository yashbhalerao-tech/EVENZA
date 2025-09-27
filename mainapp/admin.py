from django.contrib import admin
from .models import Announcement , Student, Event, Participation

#Register your models here.
admin.site.register(Student)
admin.site.register(Event)
admin.site.register(Participation)
admin.site.register(Announcement)




