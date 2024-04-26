from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Creating groups..."

    def handle(self, *args, **kwargs):
        managers_group = Group.objects.get_or_create(name="Manager")
        if managers_group:
            self.stdout.write(self.style.SUCCESS("'Manager' group created."))
        employee_group = Group.objects.get_or_create(name="Employee")
        if employee_group:
            self.stdout.write(self.style.SUCCESS("'Employee' group created."))
        