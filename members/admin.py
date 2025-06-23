# members/admin.py
from django.contrib import admin
from .models import Member
from .models import Visitor
import csv
from django.http import HttpResponse

class MemberAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'status', 'gender','guardian_name')
    readonly_fields = ('qr_code',)
    search_fields = ('first_name', 'last_name', 'email', 'phone_number', 'address')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('picture',)
        return self.readonly_fields
    
    def export_as_csv(self, request, queryset):
        # Create the HTTP response object with the CSV file
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=members.csv'

        writer = csv.writer(response)
        writer.writerow(['First Name', 'Last Name', 'Email', 'Phone Number', 'Address', 'Date of Birth', 'Status', 'Membership Class'])

        for member in queryset:
            writer.writerow([member.first_name, member.last_name, member.email, member.phone_number, member.address, member.date_of_birth, member.get_status_display(), member.membership_class])

        return response

    export_as_csv.short_description = 'Export Selected'

    actions = [export_as_csv]

admin.site.register(Member, MemberAdmin)


from .models import AttendanceSetting

class AttendanceSettingAdmin(admin.ModelAdmin):
    list_display = ['attendance_type', 'event_name', 'group_name', 'is_active']
    list_filter = ['attendance_type', 'is_active']
    actions = ['set_as_active']

    def set_as_active(self, request, queryset):
        # Deactivate all settings
        AttendanceSetting.objects.update(is_active=False)
        # Activate the selected setting
        queryset.update(is_active=True)
        self.message_user(request, "Selected attendance setting is now active.")
    set_as_active.short_description = "Set selected attendance setting as active"

admin.site.register(AttendanceSetting, AttendanceSettingAdmin)


from .models import Member, WorshipServiceAttendance, EventAttendance, SmallGroupAttendance, AttendanceSetting

# admin.site.register(Member)
admin.site.register(WorshipServiceAttendance)
admin.site.register(EventAttendance)
admin.site.register(SmallGroupAttendance)
admin.site.register(Visitor)
# admin.site.register(AttendanceSetting)