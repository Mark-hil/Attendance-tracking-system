# # # members/forms.py
# # from django import forms
# # from .models import Member, MembershipClass

# # class MemberForm(forms.ModelForm):
# #     class Meta:
# #         model = Member
# #         fields = [
# #             'first_name', 
# #             'last_name', 
# #             'email', 
# #             'phone_number', 
# #             'address', 
# #             'date_of_birth', 
# #             'picture', 
# #             'status', 
# #             'relationship', 
# #             'membership_class',
# #         ]
# # members/forms.py
# from django import forms
# from django.conf import settings

# # from members.views import send_welcome_email
# from .models import Member, Visitor
# # from .models import WorshipServiceAttendance, EventAttendance, SmallGroupAttendance



# from django import forms
# from .models import Member

# class MemberForm(forms.ModelForm):
#     class Meta:
#         model = Member
#         fields = '__all__'  # Or specify individual fields if you prefer
#         widgets = {
#             'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
#             'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter First Name'}),
#             'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Last Name'}),
#             'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email'}),
#             'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Phone Number'}),
#             'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Address'}),
#             'guardian_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Guardian Name'}),
#             'guardian_phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Guardian Phone Number'}),
#             'status': forms.Select(attrs={'class': 'form-select'}),
#             'gender': forms.Select(attrs={'class': 'form-select'}),
#             'program_of_study': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Program of Study'}),
#             'level_of_study': forms.Select(attrs={'class': 'form-select'}),
#             'membership_class': forms.Select(attrs={'class': 'form-select'}),
#             'picture': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
#             'qr_code': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
#         }



# class MemberForm(forms.ModelForm):
#     class Meta:
#         model = Member
#         exclude = ('qr_code',)

# class MemberEditForm(forms.ModelForm):
#     class Meta:
#         model = Member
#         exclude = ('qr_code',)  # Exclude the QR code field for editing

# # class AttendanceForm(forms.ModelForm):
# #     class Meta:
# #         model = WorshipServiceAttendance  # Adjust for EventAttendance or SmallGroupAttendance as needed
# #         fields = ['service_name', 'date']
# from .models import AttendanceSetting
# class AttendanceSettingForm(forms.ModelForm):
#     class Meta:
#         model = AttendanceSetting
#         fields = ['attendance_type', 'event_name', 'group_name']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['event_name'].widget.attrs.update({'class': 'form-control'})
#         self.fields['group_name'].widget.attrs.update({'class': 'form-control'})

#         #  # Set field visibility based on initial data
#         # attendance_type = self.initial.get('attendance_type')
#         # if attendance_type == 'event':
#         #     self.fields['group_name'].widget.attrs.update({'style': 'display: none;'})
#         # elif attendance_type == 'small_group':
#         #     self.fields['event_name'].widget.attrs.update({'style': 'display: none;'})
#         # else:
#         #     self.fields['event_name'].widget.attrs.update({'style': 'display: none;'})
#         #     self.fields['group_name'].widget.attrs.update({'style': 'display: none;'})

# class VisitorForm(forms.ModelForm):
#     class Meta:
#         model = Visitor
#         fields = ['first_name', 'last_name', 'email', 'phone_number']


# from django.core.mail import send_mail

# class FollowUpForm(forms.ModelForm):
#     class Meta:
#         model = Visitor
#         fields = ['follow_up_status']

#     def send_welcome_email_if_needed(self, visitor):
#         if not visitor.welcome_email_sent:
#             subject = "Welcome to Our Church"
#             message = f"Dear {visitor.first_name} {visitor.last_name},\n\nThank you for visiting our church! We are delighted to have you as our guest and look forward to welcoming you again."
#             from_email = settings.DEFAULT_FROM_EMAIL
#             recipient_list = [visitor.email]

#             send_mail(subject, message, from_email, recipient_list)

#             visitor.welcome_email_sent = True
#             visitor.save()


from django import forms
from django.conf import settings
from .models import Member, Visitor, AttendanceSetting
from django.core.mail import send_mail

# Member Form for creating and editing members
class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        exclude = ('qr_code',)  # Exclude the QR code for this form
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Phone Number'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Address'}),
            'guardian_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Guardian Name'}),
            'guardian_phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Guardian Phone Number'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Specialization'}),
            'level_of_profession': forms.Select(attrs={'class': 'form-select'}),
            # 'membership_class': forms.Select(attrs={'class': 'form-select'}),
            'picture': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

# Member form for editing (similar to MemberForm, but if needed, more specific widgets/fields could be added)
class MemberEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add required attribute to all required fields
        for field_name, field in self.fields.items():
            if field_name != 'picture':  # Picture is optional
                field.required = True
                if field_name in ['first_name', 'last_name', 'email', 'phone_number', 'address', 
                                'guardian_name', 'guardian_phone_number', 'specialization']:
                    self.fields[field_name].widget.attrs.update({
                        'required': 'required',
                        'aria-required': 'true'
                    })

    class Meta:
        model = Member
        fields = [
            'first_name', 'last_name', 'email', 'phone_number', 'address',
            'guardian_name', 'guardian_phone_number', 'date_of_birth',
            'gender', 'status', 'specialization', 'level_of_profession', 'picture'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all',
                'required': 'required',
                'aria-required': 'true'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all',
                'placeholder': 'Enter First Name',
                'required': 'required',
                'aria-required': 'true'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all',
                'placeholder': 'Enter Last Name',
                'required': 'required',
                'aria-required': 'true'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all',
                'placeholder': 'Enter Email',
                'required': 'required',
                'aria-required': 'true'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all',
                'placeholder': 'Enter Phone Number',
                'required': 'required',
                'aria-required': 'true'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all',
                'placeholder': 'Enter Full Address',
                'rows': 2,
                'required': 'required',
                'aria-required': 'true'
            }),
            'guardian_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all',
                'placeholder': 'Enter Guardian Name',
                'required': 'required',
                'aria-required': 'true'
            }),
            'guardian_phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all',
                'placeholder': 'Enter Guardian Phone Number',
                'required': 'required',
                'aria-required': 'true'
            }),
            'specialization': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all',
                'placeholder': 'Enter Specialization',
                'required': 'required',
                'aria-required': 'true'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all bg-white',
                'required': 'required',
                'aria-required': 'true'
            }),
            'gender': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all bg-white',
                'required': 'required',
                'aria-required': 'true'
            }),
            'level_of_profession': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all bg-white',
                'required': 'required',
                'aria-required': 'true'
            }),
            'picture': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-orange-50 file:text-orange-700 hover:file:bg-orange-100'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make the qr_code field readonly in the form
        if 'qr_code' in self.fields:
            self.fields['qr_code'].widget.attrs['readonly'] = True

# Attendance setting form for events or small group attendance
class AttendanceSettingForm(forms.ModelForm):
    class Meta:
        model = AttendanceSetting
        fields = ['attendance_type', 'event_name', 'group_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['event_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['group_name'].widget.attrs.update({'class': 'form-control'})

# Visitor Form
class VisitorForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = ['first_name', 'last_name', 'email', 'phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            # 'follow_up_status': forms.TextInput(attrs={'class': 'form-control'}),
        }
# Follow-up form for visitor follow-up
class FollowUpForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = ['follow_up_status']

    def send_welcome_email_if_needed(self, visitor):
        if not visitor.welcome_email_sent:
            subject = "Welcome to Our Church"
            message = f"Dear {visitor.first_name} {visitor.last_name},\n\nThank you for visiting our church! We are delighted to have you as our guest and look forward to welcoming you again."
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [visitor.email]

            send_mail(subject, message, from_email, recipient_list)

            visitor.welcome_email_sent = True
            visitor.save()
