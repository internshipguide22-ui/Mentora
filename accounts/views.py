from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.utils import timezone
from django.urls import reverse
from django.http import JsonResponse
from django.core.paginator import Paginator

from .forms import (
    UserRegisterForm, UserProfileForm, CustomAuthenticationForm,
    InstructorProfileForm, AdminProfileForm
)
from .decorators import student_required, instructor_required, admin_required
from .models import User
from courses.models import Course, Enrollment, Module, Lesson
from quizzes.models import Quiz, QuizAttempt
from certificates.models import Certificate
from notifications.models import Notification

def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
        
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Account created successfully! Please login with your credentials.')
            
            # Create welcome notification
            try:
                Notification.objects.create(
                    recipient=user,
                    title='Welcome to LMS!',
                    message=f'Welcome {user.first_name}! We\'re glad to have you here.',
                    notification_type='system'
                )
            except:
                pass
            
            return redirect('accounts:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegisterForm()
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile_view(request):
    if request.method == 'POST':
        if request.user.is_admin:
            form = AdminProfileForm(request.POST, request.FILES, instance=request.user)
        elif request.user.is_instructor:
            form = InstructorProfileForm(request.POST, request.FILES, instance=request.user)
        else:
            form = UserProfileForm(request.POST, request.FILES, instance=request.user)
            
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
    else:
        if request.user.is_admin:
            form = AdminProfileForm(instance=request.user)
        elif request.user.is_instructor:
            form = InstructorProfileForm(instance=request.user)
        else:
            form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})

@login_required
def dashboard_view(request):
    context = {
        'notifications': Notification.objects.filter(
            recipient=request.user,
            is_read=False
        )[:5]
    }
    
    if request.user.is_admin:
        # Admin Dashboard Data
        context.update({
            'total_users': User.objects.count(),
            'total_students': User.objects.filter(user_type='student').count(),
            'total_instructors': User.objects.filter(user_type='instructor').count(),
            'total_admins': User.objects.filter(user_type='admin').count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'total_courses': Course.objects.count(),
            'total_enrollments': Enrollment.objects.count(),
            'total_certificates': Certificate.objects.count(),
            'recent_users': User.objects.order_by('-date_joined')[:5],
            'recent_courses': Course.objects.order_by('-created_at')[:5],
            'user_types': User.objects.values('user_type').annotate(count=Count('id')),
            'course_categories': Course.objects.values('category__name').annotate(count=Count('id')),
            'completion_rate': Enrollment.objects.filter(completed=True).count() / Enrollment.objects.count() * 100 if Enrollment.objects.exists() else 0
        })
        template = 'dashboard/admin_dashboard.html'
        
    elif request.user.is_instructor:
        # Instructor Dashboard Data
        courses = Course.objects.filter(instructor=request.user)
        context.update({
            'courses': courses,
            'total_students': Enrollment.objects.filter(course__instructor=request.user).count(),
            'total_quizzes': Quiz.objects.filter(instructor=request.user).count(),
            'recent_enrollments': Enrollment.objects.filter(
                course__instructor=request.user
            ).order_by('-enrollment_date')[:5],
            'completion_rates': {
                course.id: course.enrollments.filter(completed=True).count() / course.enrollments.count() * 100 
                if course.enrollments.exists() else 0 
                for course in courses
            }
        })
        template = 'dashboard/instructor_dashboard.html'
        
    else:
        # Student Dashboard Data
        enrollments = request.user.enrollments.select_related('course').all()
        context.update({
            'enrollments': enrollments,
            'completed_courses': enrollments.filter(completed=True).count(),
            'in_progress_courses': enrollments.filter(completed=False).count(),
            'recent_activities': QuizAttempt.objects.filter(
                student=request.user
            ).order_by('-started_at')[:5],
            'certificates': Certificate.objects.filter(
                enrollment__student=request.user
            ).select_related('enrollment__course'),
            'course_progress': {
                enrollment.id: enrollment.progress 
                for enrollment in enrollments
            }
        })
        template = 'dashboard/student_dashboard.html'
    
    return render(request, template, context)

@login_required
def notification_list_view(request):
    notifications = Notification.objects.filter(recipient=request.user)
    paginator = Paginator(notifications, 20)
    page = request.GET.get('page')
    notifications = paginator.get_page(page)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'notifications': [{
                'id': n.id,
                'message': n.message,
                'created_at': n.created_at.strftime('%Y-%m-%d %H:%M'),
                'is_read': n.is_read
            } for n in notifications]
        })
    
    return render(request, 'accounts/notifications.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, notification_id):
    if request.method == 'POST':
        notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@admin_required
def user_list_view(request):
    user_type = request.GET.get('user_type', '')
    search = request.GET.get('search', '')
    
    users = User.objects.all()
    
    if user_type:
        users = users.filter(user_type=user_type)
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
        
    paginator = Paginator(users, 20)
    page = request.GET.get('page')
    users = paginator.get_page(page)
    
    return render(request, 'accounts/user_list.html', {
        'users': users,
        'user_type': user_type,
        'search': search
    })
