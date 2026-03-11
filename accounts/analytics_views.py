from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Count, Avg
from accounts.decorators import admin_required
from accounts.models import User
from courses.models import Course, Enrollment
from quizzes.models import Quiz, QuizAttempt
from certificates.models import Certificate
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from django.utils import timezone
import io

@login_required
@admin_required
def analytics_dashboard(request):
    # Get filter parameters
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    user_type = request.GET.get('user_type', '')
    
    # Base querysets
    users = User.objects.all()
    enrollments = Enrollment.objects.all()
    certificates = Certificate.objects.all()
    
    # Apply filters
    if date_from:
        users = users.filter(date_joined__gte=date_from)
        enrollments = enrollments.filter(enrollment_date__gte=date_from)
        certificates = certificates.filter(issued_date__gte=date_from)
    
    if date_to:
        users = users.filter(date_joined__lte=date_to)
        enrollments = enrollments.filter(enrollment_date__lte=date_to)
        certificates = certificates.filter(issued_date__lte=date_to)
    
    if user_type:
        users = users.filter(user_type=user_type)
    
    context = {
        'total_users': users.count(),
        'total_students': users.filter(user_type='student').count(),
        'total_instructors': users.filter(user_type='instructor').count(),
        'total_admins': users.filter(user_type='admin').count(),
        'active_users': users.filter(is_active=True).count(),
        
        'total_courses': Course.objects.count(),
        'total_enrollments': enrollments.count(),
        'active_enrollments': enrollments.filter(is_active=True).count(),
        'completed_courses': enrollments.filter(completed=True).count(),
        
        'total_quizzes': Quiz.objects.count(),
        'total_quiz_attempts': QuizAttempt.objects.count(),
        'completed_quizzes': QuizAttempt.objects.filter(completed_at__isnull=False).count(),
        
        'total_certificates': certificates.count(),
        
        'recent_users': users.order_by('-date_joined')[:10],
        'recent_enrollments': enrollments.select_related('student', 'course').order_by('-enrollment_date')[:10],
        'popular_courses': Course.objects.annotate(enrollment_count=Count('enrollments')).order_by('-enrollment_count')[:10],
        
        'date_from': date_from,
        'date_to': date_to,
        'user_type': user_type,
    }
    return render(request, 'analytics/dashboard.html', context)

@login_required
@admin_required
def export_analytics_csv(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Analytics"
    
    header_fill = PatternFill(start_color="417690", end_color="417690", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    ws['A1'] = 'Metric'
    ws['B1'] = 'Value'
    ws['A1'].fill = header_fill
    ws['B1'].fill = header_fill
    ws['A1'].font = header_font
    ws['B1'].font = header_font
    
    ws.append(['Total Users', User.objects.count()])
    ws.append(['Total Students', User.objects.filter(user_type='student').count()])
    ws.append(['Total Instructors', User.objects.filter(user_type='instructor').count()])
    ws.append(['Total Courses', Course.objects.count()])
    ws.append(['Total Enrollments', Enrollment.objects.count()])
    ws.append(['Completed Courses', Enrollment.objects.filter(completed=True).count()])
    ws.append(['Total Certificates', Certificate.objects.count()])
    
    ws.column_dimensions['A'].width = 25
    ws.column_dimensions['B'].width = 15
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="analytics.xlsx"'
    return response

@login_required
@admin_required
def export_users_csv(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Users"
    
    header_fill = PatternFill(start_color="417690", end_color="417690", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    headers = ['Username', 'Email', 'User Type', 'Active', 'Date Joined']
    ws.append(headers)
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
    
    for user in User.objects.all():
        ws.append([user.username, user.email, user.user_type, 'Yes' if user.is_active else 'No', user.date_joined.strftime('%Y-%m-%d %H:%M')])
    
    for col in ['A', 'B', 'C', 'D', 'E']:
        ws.column_dimensions[col].width = 20
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="users.xlsx"'
    return response

@login_required
@admin_required
def export_enrollments_csv(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Enrollments"
    
    header_fill = PatternFill(start_color="417690", end_color="417690", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    headers = ['Student', 'Course', 'Progress', 'Completed', 'Enrollment Date']
    ws.append(headers)
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
    
    for enrollment in Enrollment.objects.select_related('student', 'course'):
        ws.append([
            enrollment.student.username,
            enrollment.course.title,
            f"{enrollment.progress}%",
            'Yes' if enrollment.completed else 'No',
            enrollment.enrollment_date.strftime('%Y-%m-%d %H:%M')
        ])
    
    for col in ['A', 'B', 'C', 'D', 'E']:
        ws.column_dimensions[col].width = 25
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="enrollments.xlsx"'
    return response
