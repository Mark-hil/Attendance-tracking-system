# members/views.py
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from .models import AttendanceSetting, Member, generate_qr_code_for_attendance
# from django.shortcuts import render
from .forms import FollowUpForm, MemberForm, MemberEditForm

from django.template.loader import render_to_string
from django.http import HttpResponse
from .models import Member
import csv
import json

from PIL import Image
import io
import logging
from django.conf import settings
import os

import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from .models import Member,  Visitor
from datetime import date
from django.db.models import Count

from .models import AttendanceSetting, Member, WorshipServiceAttendance, EventAttendance, SmallGroupAttendance
from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404

from .models import AttendanceSetting
from .forms import AttendanceSettingForm

def scanner(request):
    return render(request, 'members/scanner.html')

def member_list(request):
    from django.utils import timezone
    from datetime import timedelta
    
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
    
    # Calculate statistics
    total_members = Member.objects.count()
    active_members = Member.objects.filter(status='active').count()
    
    # Get the first day of the current month
    first_day_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_this_month = Member.objects.filter(date_joined__gte=first_day_of_month).count()
    
    context = {
        'members': members,
        'member_count': total_members,
        'active_count': active_members,
        'new_members': new_this_month,
    }
    
    return render(request, 'members/member_list.html', context)


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
            # First save the member to get an ID
            member = form.save(commit=False)
            member.save()  # This generates the ID
            form.save_m2m()  # Save many-to-many relationships
            
            try:
                # Now that we have an ID, generate the QR code
                qr_data = f"http://{request.get_host()}/scan-attendance/?member_id={member.id}"
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
                
                # Update the member with the QR code
                member.qr_code = buffer.getvalue()
                member.save(update_fields=['qr_code'])  # Only update the QR code field
                
                return redirect('member_list')
                
            except Exception as e:
                # If QR code generation fails, delete the member and show error
                member.delete()
                form.add_error(None, f'Error generating QR code: {str(e)}')
                return render(request, 'members/add_member.html', {'form': form})
    else:
        form = MemberForm()
    return render(request, 'members/add_member.html', {'form': form})

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
    writer.writerow(['First Name', 'Last Name', 'Email', 'Phone Number','Specialization',
            'Level Of Profession','Gender', 'Address', 'Date of Birth', 'Status', 'Membership Class',  'Guardian Name','Guardian phone_number'])

    members = Member.objects.all()  # Get all members, or filter as needed
    for member in members:
        writer.writerow([
            member.first_name,
            member.last_name,
            member.email,
            member.phone_number,
            member.specialization,
            member.level_of_profession,
            member.gender,
            member.address,
            member.date_of_birth,
            member.get_status_display(),
            member.membership_class,
            member.guardian_name,
            member.guardian_phone_number
        ])

    return response


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





def mark_attendance(request):
    # Get parameters from request
    member_id = request.GET.get('member_id') or request.POST.get('member_id')
    token = request.GET.get('token') or request.POST.get('token')
    
    # Check for raw data in POST body (for JSON requests)
    if not all([member_id, token]) and request.body:
        try:
            import json
            body_data = json.loads(request.body)
            member_id = member_id or body_data.get('member_id')
            token = token or body_data.get('token')
        except json.JSONDecodeError:
            pass
    
    # Debug logging
    print("\n" + "="*50)
    print("[DEBUG] mark_attendance called")
    print("-"*50)
    print(f"[DEBUG] Request method: {request.method}")
    print(f"[DEBUG] Raw GET params: {dict(request.GET)}")
    print(f"[DEBUG] Raw POST params: {dict(request.POST)}")
    if request.body:
        print(f"[DEBUG] Request body: {request.body}")
    print(f"[DEBUG] Extracted member_id: {member_id} (type: {type(member_id)})")
    print(f"[DEBUG] Extracted token: {token} (type: {type(token)})")
    print("="*50 + "\n")
    
    # Validate required parameters
    if not all([member_id, token]):
        error_msg = f'Missing required parameters. Got member_id: {member_id}, token: {token}'
        print(f"[ERROR] {error_msg}")
        return JsonResponse({
            'success': False,
            'message': 'Missing required parameters. Please scan the QR code again.'
        }, status=400)
    
    # Validate member_id is a number
    try:
        if isinstance(member_id, str) and member_id.isdigit():
            member_id = int(member_id)
        elif not isinstance(member_id, int):
            raise ValueError("Invalid member ID format")
    except (ValueError, TypeError) as e:
        print(f"[ERROR] Invalid member ID: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Invalid member ID format. Must be a number.'
        }, status=400)
    
    # Validate token exists and is valid
    from django.core.cache import cache
    from datetime import datetime, date
    
    cache_key = f'qr_token_{member_id}_{token}'
    print(f"[DEBUG] Looking up cache key: {cache_key}")
    token_data = cache.get(cache_key, None)
    print(f"[DEBUG] Token data from cache: {token_data}")
    
    if token_data and 'member_id' not in token_data:
        print("[WARNING] Token data exists but missing member_id, fixing...")
        token_data['member_id'] = member_id
        cache.set(cache_key, token_data, timeout=None)
    
    # Check if token exists and is valid
    if not token_data or not token_data.get('valid', False):
        return JsonResponse({
            'success': False,
            'message': 'Invalid or expired QR code. Please generate a new one.'
        }, status=403)
    
    # Check if token was already used today
    today = date.today()
    last_used = token_data.get('last_used')
    
    if last_used and last_used.date() == today:
        return JsonResponse({
            'success': False,
            'message': 'This QR code has already been used today. Please try again tomorrow.'
        }, status=403)
    
    # Update the token with today's date (no expiration)
    token_data['last_used'] = datetime.now()
    cache.set(cache_key, token_data, timeout=None)  # Permanent storage
    
    try:
        # Get the member
        member = get_object_or_404(Member, id=member_id)
        
        # Check if there's an active attendance setting
        active_setting = AttendanceSetting.objects.filter(is_active=True).first()
        if not active_setting:
            return JsonResponse({
                'success': False,
                'message': 'No active attendance session found. Please set up an attendance type first.'
            }, status=400)
        
        # Check if attendance is already recorded for the member for today
        today = timezone.now().date()
        attendance_exists = False
        
        if active_setting.attendance_type == 'working_hours':
            attendance_exists = WorshipServiceAttendance.objects.filter(
                member=member, 
                date=today
            ).exists()
        elif active_setting.attendance_type == 'event':
            attendance_exists = EventAttendance.objects.filter(
                member=member, 
                setting=active_setting, 
                date=today
            ).exists()
        elif active_setting.attendance_type == 'small_group':
            attendance_exists = SmallGroupAttendance.objects.filter(
                member=member, 
                setting=active_setting, 
                date=today
            ).exists()

        if attendance_exists:
            return JsonResponse({
                'success': False, 
                'message': 'Attendance has already been recorded for today.'
            })

        # Mark attendance if it doesn't already exist
        if active_setting.attendance_type == 'working_hours':
            WorshipServiceAttendance.objects.create(
                member=member, 
                date=today,
                time=timezone.now().time()
            )
            attendance_type = 'Working Hours'
        elif active_setting.attendance_type == 'event':
            EventAttendance.objects.create(
                member=member, 
                setting=active_setting, 
                date=today,
                time=timezone.now().time(),
                event_name=active_setting.event_name or 'General Event'
            )
            attendance_type = 'Event'
        elif active_setting.attendance_type == 'small_group':
            SmallGroupAttendance.objects.create(
                member=member, 
                setting=active_setting, 
                date=today,
                time=timezone.now().time(),
                group_name=active_setting.group_name or 'General Group'
            )
            attendance_type = 'Small Group'
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid attendance type configured'
            }, status=400)

        return JsonResponse({
            'success': True, 
            'message': f'{attendance_type} attendance recorded successfully!',
            'member_name': f'{member.first_name} {member.last_name}',
            'attendance_type': attendance_type,
            'date': today.strftime('%Y-%m-%d'),
            'time': timezone.now().strftime('%H:%M:%S')
        })

    except ValueError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid member ID format'
        }, status=400)

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
            # Ensure end_date is not before start_date
            if end_date < start_date:
                end_date = start_date
        except (ValueError, TypeError):
            start_date = today
            end_date = today

    # Calculate counts for each attendance type within the date range
    # For working hours (WorshipServiceAttendance)
    worship_service_count = WorshipServiceAttendance.objects.filter(
        date__range=[start_date, end_date]
    ).count()
    
    # For events (EventAttendance)
    event_attendance_count = EventAttendance.objects.filter(
        date__range=[start_date, end_date]
    ).count()
    
    # For small groups (SmallGroupAttendance)
    small_group_attendance_count = SmallGroupAttendance.objects.filter(
        date__range=[start_date, end_date]
    ).count()
    
    # For visitors
    visitor_count = Visitor.objects.filter(
        visit_date__range=[start_date, end_date]
    ).count()
    
    # Get unique member counts for each attendance type
    unique_members_working = Member.objects.filter(
        worshipserviceattendance__date__range=[start_date, end_date]
    ).distinct().count()
    
    unique_members_events = Member.objects.filter(
        eventattendance__date__range=[start_date, end_date]
    ).distinct().count()
    
    unique_members_groups = Member.objects.filter(
        smallgroupattendance__date__range=[start_date, end_date]
    ).distinct().count()

    # Pass the totals to the template
    context = {
        'worship_service_count': worship_service_count,
        'event_attendance_count': event_attendance_count,
        'small_group_attendance_count': small_group_attendance_count,
        'visitor_count': visitor_count,
        'unique_members_working': unique_members_working,
        'unique_members_events': unique_members_events,
        'unique_members_groups': unique_members_groups,
        'start_date': start_date,
        'end_date': end_date,
        'today': today,
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
    # Generate tokens for each member if they don't have one
    from django.core.cache import cache
    import uuid
    
    member_data = []
    for member in members:
        # Generate a new token for this member
        token = str(uuid.uuid4())
        cache_key = f'qr_token_{member.id}_{token}'
        
        # Store token data
        token_data = {
            'valid': True,
            'last_used': None,
            'member_id': member.id,
            'member_name': f"{member.first_name} {member.last_name}"
        }
        cache.set(cache_key, token_data, timeout=None)
        
        # Add member data with token
        member_data.append({
            'id': str(member.id),  # Ensure ID is a string for template concatenation
            'first_name': member.first_name,
            'last_name': member.last_name,
            'token': token,
            'full_name': f"{member.first_name} {member.last_name}"
        })
        
        print(f"[DEBUG] Generated token for member {member.id} ({member.first_name} {member.last_name}): {token}")
    
    return render(request, 'members/print_badges.html', {'members': member_data})



def view_qr_code(request, member_id):
    """Retrieve and serve the QR code from PostgreSQL as an image."""
    member = get_object_or_404(Member, id=member_id)

    # If no QR code stored at all, generate it now and persist
    if not member.qr_code:
        try:
            import qrcode
            from io import BytesIO
            from django.core.files.base import ContentFile
            from django.core.cache import cache
            import uuid

            # Generate a token for the QR code
            token = str(uuid.uuid4())
            cache_key = f'qr_token_{member.id}_{token}'
            
            # Store token data
            token_data = {
                'valid': True,
                'last_used': None,
                'member_id': member.id
            }
            cache.set(cache_key, token_data, timeout=None)
            
            # Create QR code with production URL
            base_url = 'https://attendance-tracking-system-5d9n.onrender.com'
            qr_data = f"{base_url}/scan-attendance/?member_id={member.id}&token={token}"
            
            # Generate QR code with high error correction
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=12,
                border=6,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            # Create image with high contrast
            img = qr.make_image(fill_color='black', back_color='white')
            
            # Ensure the QR code is large enough to be scanned
            size = (img.size[0] * 2, img.size[1] * 2)
            img = img.resize(size, resample=0)
            
            # Save to buffer
            buffer = BytesIO()
            img.save(buffer, format='PNG', quality=100)
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

                            # qr_data = f"http://127.0.0.1:8000/scan-attendance/?member_id={member.id}"
                            qr = qrcode.QRCode(
                                version=1,
                                error_correction=qrcode.constants.ERROR_CORRECT_L,
                                box_size=10,
                                border=4,
                            )
                            # qr.add_data(qr_data)
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
    from datetime import date, timedelta
    import json
    
    # Get the total members, attendance, and visitors for today
    total_members = Member.objects.count()
    worship_service_count = WorshipServiceAttendance.objects.filter(date=date.today()).count()
    event_attendance_count = EventAttendance.objects.filter(date=date.today()).count()
    visitors_today = Visitor.objects.filter(visit_date=date.today()).count()
    
    # Generate trend data for the last 7 days
    trend_dates = []
    trend_data = []
    
    for i in range(6, -1, -1):
        current_date = date.today() - timedelta(days=i)
        total_attendance = (
            WorshipServiceAttendance.objects.filter(date=current_date).count() +
            EventAttendance.objects.filter(date=current_date).count()
        )
        trend_dates.append(current_date.strftime('%Y-%m-%d'))
        trend_data.append(total_attendance)

    context = {
        'total_members': total_members,
        'worship_service_count': worship_service_count,
        'event_attendance_count': event_attendance_count,
        'visitors_today': visitors_today,
        'trend_labels': json.dumps(trend_dates),
        'trend_data': json.dumps(trend_data),
    }

    return render(request, 'members/dashboard.html', context)