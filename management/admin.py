from django.contrib import admin

from management.models import Parking, ParkingSpace, Ticket
# Register your models here.

admin.site.register(Parking)
admin.site.register(ParkingSpace)
admin.site.register(Ticket)