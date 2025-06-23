from django.core.management.base import BaseCommand
from members.models import EventAttendance, SmallGroupAttendance, WorshipServiceAttendance

class Command(BaseCommand):
    help = 'Clears all attendance records from the database'

    def handle(self, *args, **kwargs):
        # Clear records from all attendance models
        EventAttendance.objects.all().delete()
        SmallGroupAttendance.objects.all().delete()
        WorshipServiceAttendance.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('Successfully cleared all attendance records'))
