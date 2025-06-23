# members/models.py
from django.db import models
from django.contrib.auth.models import User
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone

class MembershipClass(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name

class Member(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=25, blank=True)
    address = models.CharField(max_length=200)
    guardian_name = models.CharField(max_length=100)
    guardian_phone_number = models.CharField(max_length=25, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    date_joined = models.DateField(auto_now_add=True)
    # active = models.BooleanField(default=True)
    picture = models.ImageField(upload_to='member_pictures/', null=True, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)
    # relationship = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='family_members')
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('visitor', 'Visitor'),
    ]
    GENDER_CHOICES = [
        ('male', 'male'),
        ('female', 'female'),
    ]
    LEVEL_CHOICES = [
        ('100', '100'),
        ('200', '200'),
        ('300', '300'),
        ('400', '400'),
        ('Alumi', 'Alumi'),
    ]
    MEMBERSHIP_CLASS = [
        ('Milerites', 'Milerites'),
        ('Missionaries', 'Missionaries'),
        ('Patriachs', 'Patriachs'),
        ('Disciples', 'Disciples'),
        ('Soul Winners', 'Soul Winners'),
        ('Reminats', 'Reminats'),
        ('Pioneers', 'Pioneers'),
        ('Adventurers', 'Adventurers'),
        ('Baptismal', 'Baptismal'),
    ]

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='')
    program_of_study = models.CharField(max_length=100)
    level_of_study = models.CharField(max_length=100, choices=LEVEL_CHOICES, default='')
    membership_class = models.CharField(max_length=20,  choices=MEMBERSHIP_CLASS, default='')
    qr_code = models.BinaryField(null=True, blank=True)

# def generate_qr_code_for_attendance(member):
#     # Fetch the active attendance setting
#     active_setting = AttendanceSetting.objects.filter(is_active=True).first()
    
#     if active_setting:
#         qr_data = f"http://127.0.0.1:8000/scan-attendance/?member_id={member.id}&attendance_type={active_setting.attendance_type}"
        
#         if active_setting.attendance_type == 'event':
#             qr_data += f"&event_name={active_setting.event_name}"
#         elif active_setting.attendance_type == 'small_group':
#             qr_data += f"&group_name={active_setting.group_name}"

#         qr = qrcode.QRCode(
#             version=1,
#             error_correction=qrcode.constants.ERROR_CORRECT_L,
#             box_size=10,
#             border=4,
#         )
#         qr.add_data(qr_data)
#         qr.make(fit=True)
        
#         img = qr.make_image(fill='black', back_color='white')
#         buffer = BytesIO()
#         img.save(buffer, format='PNG')
#         qr_code_file = ContentFile(buffer.getvalue(), 'attendance_qrcode.png')
        
#         return qr_code_file

#     return None
from django.http import HttpResponseForbidden
def generate_qr_code_for_attendance(member):
    active_setting = AttendanceSetting.objects.filter(is_active=True).first()

    if not active_setting:
        return HttpResponseForbidden("No active attendance setting found.")

    qr_data = f"http://127.0.0.1:8000/scan-attendance/?member_id={member.id}&attendance_type={active_setting.attendance_type}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_code_file = ContentFile(buffer.getvalue(), 'attendance_qrcode.png')
    
    return qr_code_file
    # def save(self, *args, **kwargs):
    #     # Generate QR code
    #     qr = qrcode.QRCode(
    #         version=1,
    #         error_correction=qrcode.constants.ERROR_CORRECT_L,
    #         box_size=10,
    #         border=4,
    #     )
    #     qr.add_data(f'{self.first_name} {self.last_name}\nEmail: {self.email}\nPhone: {self.phone_number}')
    #     qr.make(fit=True)

    #     img = qr.make_image(fill='black', back_color='white')
    #     canvas = Image.new('RGB', (290, 290), 'white')
    #     draw = ImageDraw.Draw(canvas)
    #     canvas.paste(img)
    #     fname = f'qr_code-{self.first_name}{self.last_name}.png'
    #     buffer = BytesIO()
    #     canvas.save(buffer, 'PNG')
    #     self.qr_code.save(fname, File(buffer), save=False)
    #     canvas.close()

    #     super().save(*args, **kwargs)

    # def __str__(self):
    #     return f"{self.first_name} {self.last_name}"
    
    

# class WorshipServiceAttendance(models.Model):
#     member = models.ForeignKey('Member', on_delete=models.CASCADE)
#     date = models.DateField()
#     service_name = models.CharField(max_length=255)
#     checked_in = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.member} - {self.service_name} on {self.date}"

# class EventAttendance(models.Model):
#     member = models.ForeignKey('Member', on_delete=models.CASCADE)
#     event_name = models.CharField(max_length=255)
#     event_date = models.DateField()
#     checked_in = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.member} - {self.event_name} on {self.event_date}"

# class SmallGroupAttendance(models.Model):
#     member = models.ForeignKey('Member', on_delete=models.CASCADE)
#     group_name = models.CharField(max_length=255)
#     meeting_date = models.DateField()
#     checked_in = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.member} - {self.group_name} on {self.meeting_date}"
    


from django.db import models
from django.utils import timezone
from datetime import time


# class WorshipService(models.Model):
#     name = models.CharField(max_length=100)
#     date = models.DateTimeField()
#     location = models.CharField(max_length=200)

#     def __str__(self):
#         return self.name

# class Event(models.Model):
#     name = models.CharField(max_length=100)
#     date = models.DateTimeField()
#     location = models.CharField(max_length=200)

#     def __str__(self):
#         return self.name

# class Attendance(models.Model):
#     ATTENDANCE_TYPE_CHOICES = [
#         ('Worship Service', 'Worship Service'),
#         ('Event', 'Event'),
#         ('Small Group', 'Small Group'),
#     ]
#     member = models.ForeignKey(Member, on_delete=models.CASCADE)
#     attendance_type = models.CharField(max_length=20, choices=ATTENDANCE_TYPE_CHOICES)
#     worship_service = models.ForeignKey(WorshipService, on_delete=models.SET_NULL, null=True, blank=True)
#     event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)
#     date = models.DateTimeField(default=timezone.now)

#     def __str__(self):
#         return f"{self.member} - {self.attendance_type} on {self.date}"
    
class AttendanceSetting(models.Model):
    ATTENDANCE_TYPES = [
        ('working_hours', 'Working Hours'),
        ('event', 'Event'),
        ('small_group', 'Small Group'),
    ]

    attendance_type = models.CharField(max_length=20, choices=ATTENDANCE_TYPES)
    event_name = models.CharField(max_length=100, blank=True, null=True)
    group_name = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=False)  # To mark if this setting is currently in use
    # time_of_attendance = models.TimeField(default=None, null=True, blank=True)  # Store the actual time

class WorshipServiceAttendance(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    # Other fields...

class EventAttendance(models.Model):
    setting = models.ForeignKey(AttendanceSetting, on_delete=models.CASCADE, null=True, blank=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    event_name = models.CharField(max_length=255)
    
    # Other fields...

class SmallGroupAttendance(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    group_name = models.CharField(max_length=255)
    setting = models.ForeignKey(AttendanceSetting, on_delete=models.CASCADE, null=True, blank=True)
    # Other fields...



    # def __str__(self):
    #     return f"{self.attendance_type} - {self.date}"

    def __str__(self):
        return f"{self.attendance_type} on {self.date} - {'Active' if self.is_active else 'Inactive'}"
    
    # def __str__(self):
    #     return f"{self.get_attendance_type_display()} - Active: {self.is_active}"
    
    # def __str__(self):
    #     return f"Active Setting: {self.attendance_type}"

    

    class Meta:
        verbose_name = "Attendance Setting"
        verbose_name_plural = "Attendance Settings"



from django.utils import timezone

class Visitor(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    visit_date = models.DateField(auto_now_add=True)
    follow_up_status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('contacted', 'Contacted'),
        ('attended', 'Attended')
    ], default='pending')
    welcome_email_sent = models.BooleanField(default=False)  # New field
    # last_contacted = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
