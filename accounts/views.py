from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings

from .forms import (
    UserRegisterForm, UserProfileForm, CustomAuthenticationForm,
    InstructorProfileForm, AdminProfileForm
)
from .decorators import student_required, instructor_required, admin_required
from .models import User, RegistrationRequest
from courses.models import Course, Enrollment, Module, Lesson
from quizzes.models import Quiz, QuizAttempt
from certificates.models import Certificate
from notifications.models import Notification
from reviews.models import Review


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)

        RegistrationRequest.objects.filter(
            email__iexact=form.get_user().email
        ).exclude(status='rejected').update(status='completed')

        return response

def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    show_user_type = request.user.is_authenticated and request.user.is_admin

    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES, show_user_type=show_user_type)
        if form.is_valid():
            user = form.save()
            try:
                login_url = f"{settings.SITE_URL}/accounts/login/"
                message = f'''Dear {user.first_name or user.username},

Your LMS account has been created successfully.

Login credentials:
- Username: {user.username}
- Email: {user.email}
- Password: The password you created during registration

Login here:
{login_url}

Best regards,
LMS Team
'''

                send_mail(
                    'Your LMS Login Credentials',
                    message,
                    getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@lms.com'),
                    [user.email],
                    fail_silently=False,
                )
            except Exception:
                pass

            messages.success(request, 'Account created successfully! Login credentials have been sent to your email.')
            
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
            
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegisterForm(show_user_type=show_user_type)
    
    return render(request, 'registration/register.html', {
        'form': form,
        'show_user_type': show_user_type,
    })


def registration_request_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if not all([name, email, phone]):
            message = 'All fields are required.'
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': message
                })
            messages.error(request, message)
            return redirect('home')
        
        try:
            registration_request = RegistrationRequest.objects.create(
                name=name,
                email=email,
                phone=phone,
                status='pending'
            )

            registration_url = f"{settings.SITE_URL}/accounts/register/"
            message = f'''Dear {name},

Your registration request has been received.

Please complete your registration using the link below:
{registration_url}

Best regards,
LMS Team
'''

            email_sent = False
            try:
                send_mail(
                    'Complete Your LMS Registration',
                    message,
                    getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@lms.com'),
                    [email],
                    fail_silently=False,
                )
                email_sent = True
            except Exception:
                email_sent = False

            if email_sent:
                registration_request.status = 'processed'
                registration_request.email_sent = True
                registration_request.save(update_fields=['status', 'email_sent'])
                success_message = 'Registration request submitted successfully! A registration email has been sent.'
            else:
                success_message = 'Registration request was saved, but email delivery is not configured yet.'

            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': success_message
                })
            messages.success(request, success_message)
            return redirect('home')
            
        except Exception as e:
            error_message = 'Failed to send email. Please try again later.'
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': error_message
                })
            messages.error(request, error_message)
            return redirect('home')

    return JsonResponse({
        'success': False,
        'message': 'Invalid request.'
    }, status=400)


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
            'total_registration_requests': RegistrationRequest.objects.count(),
            'pending_registration_requests': RegistrationRequest.objects.filter(status='pending').count(),
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
        reviewed_course_ids = set(
            Review.objects.filter(student=request.user).values_list('course_id', flat=True)
        )
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
            },
            'reviewed_course_ids': reviewed_course_ids,
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
