# members/urls.py
from django.urls import path
from .views import member_list, add_member
from . import views

urlpatterns = [
    path('', member_list, name='member_list'),  # The root URL of this app shows the member list
    path('add/', add_member, name='add_member'),
    path('edit/<int:pk>/', views.edit_member, name='edit_member'),
    path('delete/<int:pk>/', views.delete_member, name='delete_member'),
    path('export/csv/', views.export_members_csv, name='export_members_csv'),
    path('track_attendance/', views.track_attendance, name='track_attendance'), 
    path('attendance_report/', views.attendance_report, name='attendance_report'),
    path('scanner/', views.scanner, name='scanner'),
    # path('attendance-success/', views.attendance_success, name='attendance_success'),
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    # path('set-attendance-session/', views.set_attendance_session, name='set_attendance_session'),
    path('set-attendance-type/', views.set_attendance_type, name='set_attendance_type'),
    path('scan-attendance/', views.mark_attendance, name='mark_attendance'),
    path('attendance-report/export/', views.export_attendance_report, name='export_attendance_report'),
    path('print_badges/', views.print_badges, name='print_badges'),
    path('qr-code/<int:member_id>/', views.view_qr_code, name='view_qr_code'),
    # path('print-badge/<int:member_id>/', views.print_badge, name='print_badge'),
    path('add-visitor/', views.add_visitor, name='add_visitor'),
    path('visitors/', views.visitor_list, name='visitor_list'),
    path('follow-up/<int:pk>/', views.follow_up_visitor, name='follow_up_visitor'),
    path('dashboard/', views.dashboard, name='dashboard'),
]

