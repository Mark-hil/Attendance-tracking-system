# members/views.py
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from .models import AttendanceSetting, Member, generate_qr_code_for_attendance
# from django.shortcuts import render
from .forms import FollowUpForm, MemberForm, MemberEditForm

# def member_list(request):
#     members = Member.objects.all()
#     return render(request, 'members/member_list.html', {'members': members})

# members/views.py
from django.template.loader import render_to_string
from django.http import HttpResponse
from .models import Member
import csv
import json

import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from .models import Member,  Visitor
from datetime import date
from django.db.models import Count

# from .models import WorshipServiceAttendance, EventAttendance, SmallGroupAttendance
# from .forms import AttendanceForm  # Assume you have a form for attendance

def scanner(request):
    return render(request, 'members/scanner.html')

def member_list(request):
    query = request.GET.get('q')
    if query:
        members = Member.objects.filter(
            first_name__icontains=query
        ) | Member.objects.filter(
            last_name__icontains=query
        ) | Member.objects.filter(
            email__icontains=query
        ) | Member.objects.filter(
            phone_number__icontains=query
        ) | Member.objects.filter(
            address__icontains=query
        )
    else:
        members = Member.objects.all()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('members/member_list_rows.html', {'members': members}, request=request)
        return HttpResponse(html)
    
    return render(request, 'members/member_list.html', {'members': members})


# import qrcode
# from io import BytesIO
# from django.core.files.base import ContentFile

# def generate_qr_code_for_attendance(member):
#     qr_data = f"http://localhost:8000/track_attendance/?data=Member ID:{member.id}, Name:{member.first_name} {member.last_name}, Phone Number: {member.phone_number}, Membership Class: {member.membership_class}"
    
#     qr = qrcode.QRCode(
#         version=1,
#         error_correction=qrcode.constants.ERROR_CORRECT_H,  # Adjust error correction level
#         box_size=10,
#         border=4,
#     )
#     qr.add_data(qr_data)
#     qr.make(fit=True)
    
#     img = qr.make_image(fill='black', back_color='white')
#     buffer = BytesIO()
#     img.save(buffer, format='PNG')
#     qr_code_file = ContentFile(buffer.getvalue(), 'attendance_qrcode.png')
    
#     return qr_code_file


def add_member(request):
    if request.method == 'POST':
        form = MemberForm(request.POST, request.FILES)
        if form.is_valid():
            member = form.save()

            # Generate QR code based on member's unique ID
            qr_data = f"http://127.0.0.1:8000/scan-attendance/?member_id={member.id}"
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)

            # Save QR Code as binary data
            img = qr.make_image(fill='black', back_color='white')
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            member.qr_code = buffer.getvalue()  # Store binary data in PostgreSQL
            member.save()

            return redirect('member_list')
    else:
        form = MemberForm()
    return render(request, 'members/add_member.html', {'form': form})
# def add_member(request):
#     if request.method == 'POST':
#         form = MemberForm(request.POST, request.FILES)
#         if form.is_valid():
#             member = form.save()

#             # Generate QR code
#             qr_code_file = generate_qr_code_for_attendance(member)
#             member.qr_code.save('member_qrcode.png', qr_code_file)
#             member.save()

#             return redirect('member_list')
#     else:
#         form = MemberForm()
#     return render(request, 'members/add_member.html', {'form': form})


# members/views.py
# from django.shortcuts import render
# # from .models import WorshipServiceAttendance, EventAttendance, SmallGroupAttendance

# def attendance_report(request):
#     # Calculate the number of attendees for different categories
#     worship_attendees = WorshipServiceAttendance.objects.count()
#     event_attendees = EventAttendance.objects.count()
#     small_group_attendees = SmallGroupAttendance.objects.count()

#     context = {
#         'worship_attendees': worship_attendees,
#         'event_attendees': event_attendees,
#         'small_group_attendees': small_group_attendees,
#     }

#     return render(request, 'members/attendance_report.html', context)

# def add_member(request):
#     if request.method == 'POST':
#         form = MemberForm(request.POST, request.FILES)
#         if form.is_valid():
#             member = form.save()
            
#              # Generate QR code with all member data except the image
#             qr_data = (
#                 f"First Name: {member.first_name}\n"
#                 f"Last Name: {member.last_name}\n"
#                 f"Email: {member.email}\n"
#                 f"Phone Number: {member.phone_number}\n"
#                 f"Address: {member.address}\n"
#                 f"Date of Birth: {member.date_of_birth}\n"
#                 f"Status: {member.get_status_display()}\n"
#                 f"Membership Class: {member.membership_class}"
#             )
            
#             qr = qrcode.QRCode(
#                 version=1, 
#                 error_correction=qrcode.constants.ERROR_CORRECT_L,
#                 box_size=10, 
#                 border=4
#                 )
#             qr.add_data(qr_data)
#             qr.make(fit=True)
            
#             img = qr.make_image(fill='black', back_color='white')
#             buffer = BytesIO()
#             img.save(buffer, format='PNG')
#             qr_code_file = ContentFile(buffer.getvalue(), 'qrcode.png')
            
#             # Save QR code to the member instance
#             member.qr_code.save('qrcode.png', qr_code_file)
#             member.save()
            
#             return redirect('member_list')
#     else:
#         form = MemberForm()
#     return render(request, 'members/add_member.html', {'form': form})


def edit_member(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        form = MemberEditForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            return redirect('member_list')
    else:
        form = MemberEditForm(instance=member)
    return render(request, 'members/edit_member.html', {'form': form, 'member': member})

def delete_member(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        member.delete()
        return redirect('member_list')
    return render(request, 'members/delete_member.html', {'member': member})


def export_members_csv(request):
    # Create the HTTP response object with the CSV file
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=members.csv'

    writer = csv.writer(response)
    writer.writerow(['First Name', 'Last Name', 'Email', 'Phone Number','Program Of Study',
            'Level Of Study','Gender', 'Address', 'Date of Birth', 'Status', 'Membership Class',  'Guardian Name','Guardian phone_number'])

    members = Member.objects.all()  # Get all members, or filter as needed
    for member in members:
        writer.writerow([
            member.first_name,
            member.last_name,
            member.email,
            member.phone_number,
            member.program_of_study,
            member.level_of_study,
            member.gender,
            member.address,
            member.date_of_birth,
            member.get_status_display(),
            member.membership_class,
            member.guardian_name,
            member.guardian_phone_number
        ])

    return response


# # members/views.py
# from django.shortcuts import get_object_or_404
# from django.http import HttpResponse
# from .models import Member, WorshipServiceAttendance, EventAttendance, SmallGroupAttendance

def track_attendance(request):
#     qr_code_data = request.GET.get('data')
#     if qr_code_data:
#         # Parse QR code data to extract member ID
#         member_id = qr_code_data.split(',')[0].split(':')[1].strip()
#         member = get_object_or_404(Member, id=member_id)

#         # Mark attendance
#         # Assuming you're tracking worship service attendance
#         WorshipServiceAttendance.objects.create(
#             member=member,
#             service_name='Sunday Service',
#             date=datetime.date.today()
#         )

#         return HttpResponse('Attendance recorded successfully.')
    
  return HttpResponse('Invalid QR code data.')


from django.shortcuts import render, redirect, get_object_or_404
# from .models import Member, WorshipService, Event, Attendance

# def scan_attendance(request):
#     # This view would be called when a QR code is scanned.
#     member_id = request.GET.get('member_id')
#     attendance_type = request.GET.get('type')
#     worship_service_id = request.GET.get('service_id')
#     event_id = request.GET.get('event_id')
    
#     member = get_object_or_404(Member, id=member_id)
    
#     if attendance_type == 'Worship Service':
#         worship_service = get_object_or_404(WorshipService, id=worship_service_id)
#         Attendance.objects.create(member=member, attendance_type='Worship Service', worship_service=worship_service)
#     elif attendance_type == 'Event':
#         event = get_object_or_404(Event, id=event_id)
#         Attendance.objects.create(member=member, attendance_type='Event', event=event)
    
#     return redirect('attendance_success')

# def attendance_success(request):
#     return render(request, 'members/attendance_success.html')

# from .models import Attendance

def attendance_report(request):
    # Fetch all attendance records
    worship_attendance = WorshipServiceAttendance.objects.all()
    event_attendance = EventAttendance.objects.all()
    small_group_attendance = SmallGroupAttendance.objects.all()

    context = {
        'worship_attendance': worship_attendance,
        'event_attendance': event_attendance,
        'small_group_attendance': small_group_attendance,
    }

    return render(request, 'members/attendance_report.html', context)


from .models import AttendanceSetting, Member, WorshipServiceAttendance, EventAttendance, SmallGroupAttendance
from django.http import JsonResponse
from django.utils import timezone

# def mark_attendance(request):
#     member_id = request.GET.get('member_id')
#     active_setting = AttendanceSetting.objects.filter(is_active=True).first()

#     if not active_setting:
#         return JsonResponse({'success': False, 'message': 'No active attendance session found.'})

#     if member_id:
#         member = get_object_or_404(Member, id=member_id)

#         # Mark attendance based on the active setting
#         if active_setting.attendance_type == 'worship_service':
#             WorshipServiceAttendance.objects.create(member=member)
#         elif active_setting.attendance_type == 'event':
#             EventAttendance.objects.create(member=member, event_name=active_setting.event_name)
#         elif active_setting.attendance_type == 'small_group':
#             SmallGroupAttendance.objects.create(member=member, group_name=active_setting.group_name)

#         return JsonResponse({'success': True, 'message': 'Attendance recorded successfully!'})

#     return JsonResponse({'success': False, 'message': 'Failed to record attendance. Please try again.'})

def mark_attendance(request):
    member_id = request.GET.get('member_id')
    active_setting = AttendanceSetting.objects.filter(is_active=True).first()
    today = timezone.now().date()  # Automatically get today's date

    if not active_setting:
        return JsonResponse({'success': False, 'message': 'No active attendance session found.'})

    if member_id:
        member = get_object_or_404(Member, id=member_id)

        # Check if attendance is already recorded for the member for today
        attendance_exists = False
        if active_setting.attendance_type == 'worship_service':
            attendance_exists = WorshipServiceAttendance.objects.filter(member=member, date=today).exists()
        elif active_setting.attendance_type == 'event':
            attendance_exists = EventAttendance.objects.filter(member=member, setting=active_setting, date=today).exists()
        elif active_setting.attendance_type == 'small_group':
            attendance_exists = SmallGroupAttendance.objects.filter(member=member, setting=active_setting, date=today).exists()

        if attendance_exists:
            return JsonResponse({'success': False, 'message': 'Attendance has already been recorded for today.'})

        # Mark attendance if it doesn't already exist
        if active_setting.attendance_type == 'worship_service':
            WorshipServiceAttendance.objects.create(member=member, date=today)
        elif active_setting.attendance_type == 'event':
            EventAttendance.objects.create(member=member, setting=active_setting, date=today)  # Pass the setting
        elif active_setting.attendance_type == 'small_group':
            SmallGroupAttendance.objects.create(member=member, setting=active_setting, date=today)  # Pass the setting

        return JsonResponse({'success': True, 'message': 'Attendance recorded successfully!'})

    return JsonResponse({'success': False, 'message': 'Failed to record attendance. Please try again.'})

def attendance_report(request):
    # Get the current date or use a date provided by the user
    today = timezone.now().date()
    start_date = request.GET.get('start_date', str(today))
    end_date = request.GET.get('end_date', str(today))
    
    # Convert dates from query parameters
    if 'reset' in request.GET:
        # Reset to the current date
        start_date = today
        end_date = today
    else:
        try:
            start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            start_date = today
            end_date = today

    # Calculate counts for each attendance type within the date range
    worship_service_count = WorshipServiceAttendance.objects.filter(date__range=[start_date, end_date]).count()
    event_attendance_count = EventAttendance.objects.filter(date__range=[start_date, end_date]).count()
    small_group_attendance_count = SmallGroupAttendance.objects.filter(date__range=[start_date, end_date]).count()
    visitor_count = Visitor.objects.filter(visit_date__range=[start_date, end_date]).count()

    # Pass the totals to the template
    context = {
        'worship_service_count': worship_service_count,
        'event_attendance_count': event_attendance_count,
        'small_group_attendance_count': small_group_attendance_count,
        'visitor_count': visitor_count,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'members/attendance_report.html', context)


def export_attendance_report(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="detailed_attendance_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Attendance Type', 'Member Name', 'Event/Group Name', 'Date', 'Time'])

    # Export Working Hours Attendance
    working_hours_attendance = WorshipServiceAttendance.objects.all()
    for record in working_hours_attendance:
        writer.writerow([
            'Working Hours',
            f"{record.member.first_name} {record.member.last_name}",
            "N/A",  # No event or group name for working hours
            record.date,
            record.time.strftime("%H:%M:%S") if record.time else "N/A"
        ])

    # Export Event Attendance
    event_attendance = EventAttendance.objects.all()
    for record in event_attendance:
        writer.writerow([
            'Event',
            f"{record.member.first_name} {record.member.last_name}",
            record.setting.event_name if record.setting else "N/A",
            record.date,
            record.time.strftime("%H:%M:%S") if record.time else "N/A"
        ])

    # Export Small Group Attendance
    small_group_attendance = SmallGroupAttendance.objects.all()
    for record in small_group_attendance:
        writer.writerow([
            'Small Group',
            f"{record.member.first_name} {record.member.last_name}",
            record.setting.group_name if record.setting else "N/A",
            record.date,
            record.time.strftime("%H:%M:%S") if record.time else "N/A"
        ])

    return response

# def set_attendance_session(request):
#     if request.method == 'POST':
#         # Deactivate any previously active session
#         AttendanceSetting.objects.update(is_active=False)

#         # Create a new active session based on admin input
#         attendance_type = request.POST.get('attendance_type')
#         event_name = request.POST.get('event_name', None)
#         group_name = request.POST.get('group_name', None)

#         AttendanceSetting.objects.create(
#             attendance_type=attendance_type,
#             event_name=event_name,
#             group_name=group_name,
#             is_active=True
#         )

#         return redirect('scanner')  # Redirect to the scanning page after setting the session

#     return render(request, 'members/set_attendance_session.html')

from .models import AttendanceSetting
from .forms import AttendanceSettingForm

def set_attendance_type(request):
    if request.method == 'POST':
        form = AttendanceSettingForm(request.POST)
        if form.is_valid():
            setting = form.save(commit=False)
            # Deactivate all other settings
            AttendanceSetting.objects.update(is_active=False)
            setting.is_active = True
            setting.save()
            return redirect('scanner')  # Redirect to the settings page or another page
    else:
        form = AttendanceSettingForm()

    current_setting = AttendanceSetting.objects.filter(is_active=True).first()
    return render(request, 'members/set_attendance_type.html', {'form': form, 'current_setting': current_setting})


def print_badges(request):
    members = Member.objects.all()
    return render(request, 'members/print_badges.html', {'members': members})

from PIL import Image
import io
import logging
from django.conf import settings
import os

def view_qr_code(request, member_id):
    """Retrieve and serve the QR code from PostgreSQL as an image."""
    member = get_object_or_404(Member, id=member_id)

    # If no QR code stored at all, generate it now and persist
    if not member.qr_code:
        try:
            import qrcode
            from io import BytesIO

            qr_data = f"http://127.0.0.1:8000/scan-attendance/?member_id={member.id}"
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
            image_data = buffer.getvalue()
            # Persist for future requests
            member.qr_code = image_data
            member.save(update_fields=["qr_code"])
            return HttpResponse(image_data, content_type="image/png")
        except Exception as regen_err:
            logging.error(f"Could not generate QR code for member {member.id}: {regen_err}")
            return HttpResponse("QR code not available", status=404)

    if member.qr_code:
        # `qr_code` can be stored either as raw binary (BinaryField) or as a file path/FileField.
        try:
            # Case 1: qr_code already holds raw bytes / memoryview
            if isinstance(member.qr_code, (bytes, bytearray, memoryview)):
                # Convert memoryview to bytes if necessary
                image_data = bytes(member.qr_code)
                # Directly serve bytes without re-processing to avoid potential PIL issues
                return HttpResponse(image_data, content_type="image/png")
            elif hasattr(member.qr_code, "url"):
                # If it's a Django FiewldFile with its own URL, simply redirect to it.
                return redirect(member.qr_code.url)
            else:
                # Case 2: qr_code is an ImageField/FileField (Django `File` object or path)
                # Ensure the file is opened and read into memory as bytes
                if hasattr(member.qr_code, "read"):
                    # Django File object
                    member.qr_code.open("rb")
                    image_data = member.qr_code.read()
                else:
                    # Plain filesystem path stored as string (may be relative to MEDIA_ROOT)
                    file_path = str(member.qr_code)
                    if not os.path.isabs(file_path):
                        file_path = os.path.join(settings.MEDIA_ROOT, file_path)

                    if not os.path.exists(file_path):
                        # File missing – regenerate QR code on the fly and persist so future lookups succeed.
                        try:
                            import qrcode
                            from io import BytesIO

                            qr_data = f"http://127.0.0.1:8000/scan-attendance/?member_id={member.id}"
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
                            image_data = buffer.getvalue()

                            # Save regenerated bytes back to member record
                            member.qr_code = image_data
                            member.save(update_fields=["qr_code"])
                        except Exception as regen_err:
                            logging.error(f"Could not regenerate QR code for member {member.id}: {regen_err}")
                            return HttpResponse("QR code file not found", status=404)
                    else:
                        with open(file_path, "rb") as f:
                            image_data = f.read()

            image = Image.open(io.BytesIO(image_data))
            response = HttpResponse(content_type="image/png")
            image.save(response, "PNG")
            return response
        except Exception as e:
            # Log the error
            logging.error(f"Error serving QR code: {e}")
            # Return a friendly message
            return HttpResponse("Unable to render QR code", status=500)
    else:
        return HttpResponse("No QR code available", status=404)


from .models import Visitor
from .forms import VisitorForm

def add_visitor(request):
    if request.method == 'POST':
        form = VisitorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('visitor_list')
    else:
        form = VisitorForm()
    return render(request, 'visitors/add_visitor.html', {'form': form})

def visitor_list(request):
    visitors = Visitor.objects.all()
    return render(request, 'visitors/visitor_list.html', {'visitors': visitors})


from django.core.mail import send_mail
from django.conf import settings

def send_welcome_email(visitor):
    subject = "Welcome to Our Church!"
    message = f"Dear {visitor.first_name},\n\nThank you for visiting us. We are glad to have you."
    recipient_list = [visitor.email]
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)  



def follow_up_visitor(request, pk):
    visitor = get_object_or_404(Visitor, pk=pk)
    
    if request.method == 'POST':
        form = FollowUpForm(request.POST, instance=visitor)
        if form.is_valid():
            visitor = form.save()
            form.send_welcome_email_if_needed(visitor)  # Call the method to send the email
            return redirect('visitor_list')
    else:
        form = FollowUpForm(instance=visitor)
    
    return render(request, 'visitors/follow_up_visitor.html', {'form': form})

def dashboard(request):
    # Get the total members, attendance, and visitors for today
    total_members = Member.objects.count()
    # total_attendance = AttendanceSetting.objects.filter(date=date.today()).count()
    worship_service_count = WorshipServiceAttendance.objects.filter(date=date.today()).count()
    event_attendance_count = EventAttendance.objects.filter(date=date.today()).count()
    small_group_attendance_count = SmallGroupAttendance.objects.filter(date=date.today()).count()
    visitors_today = Visitor.objects.filter(visit_date=date.today()).count()

    context = {
        'total_members': total_members,
        'worship_service_count': worship_service_count,
        'event_attendance_count': event_attendance_count,
        'small_group_attendance_count': small_group_attendance_count,
        'visitors_today': visitors_today,
    }

    return render(request, 'members/dashboard.html', context)