from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.db.models import Prefetch
from accounts.decorators import admin_required
from accounts.models import User
from courses.models import Course, Enrollment
from django.contrib.auth.hashers import make_password

@login_required
@admin_required
def manage_users(request):
    search = request.GET.get('search', '')
    user_type = request.GET.get('user_type', '')
    
    users = User.objects.prefetch_related(
        Prefetch(
            'enrollments',
            queryset=Enrollment.objects.select_related('course').filter(is_active=True)
        )
    )
    if search:
        users = users.filter(Q(username__icontains=search) | Q(email__icontains=search))
    if user_type:
        users = users.filter(user_type=user_type)

    users = list(users)
    for user in users:
        if user.user_type != 'student':
            user.paid_courses_display = 'N/A'
            user.payment_status_display = 'N/A'
            continue

        active_enrollments = list(user.enrollments.all())
        if not active_enrollments:
            user.paid_courses_display = 'NA'
            user.payment_status_display = 'N/A'
            continue

        paid_enrollments = [
            enrollment for enrollment in active_enrollments
            if enrollment.course.course_access_type == 'paid'
        ]

        if paid_enrollments:
            user.paid_courses_display = ', '.join(
                enrollment.course.title for enrollment in paid_enrollments
            )
            user.payment_status_display = 'Paid'
        else:
            user.paid_courses_display = 'NA'
            user.payment_status_display = 'N/A'
    
    return render(request, 'management/users.html', {'users': users, 'search': search, 'user_type': user_type})

@login_required
@admin_required
def create_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user_type = request.POST.get('user_type')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return render(request, 'management/create_user.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists!')
            return render(request, 'management/create_user.html')
        
        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            first_name=first_name,
            last_name=last_name,
            user_type=user_type
        )
        messages.success(request, f'User {username} created successfully!')
        return redirect('manage_users')
    
    return render(request, 'management/create_user.html')

@login_required
@admin_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.user_type = request.POST.get('user_type')
        user.is_active = request.POST.get('is_active') == 'on'
        user.save()
        messages.success(request, 'User updated successfully!')
        return redirect('manage_users')
    return render(request, 'management/edit_user.html', {'edit_user': user})

@login_required
@admin_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully!')
        return redirect('manage_users')
    return render(request, 'management/delete_user.html', {'delete_user': user})

@login_required
@admin_required
def manage_courses(request):
    from django.db.models import Count
    search = request.GET.get('search', '')
    courses = Course.objects.annotate(
        student_count=Count('enrollments', filter=Q(enrollments__is_active=True))
    ).select_related('instructor')
    if search:
        courses = courses.filter(Q(title__icontains=search) | Q(description__icontains=search))
    return render(request, 'management/courses.html', {'courses': courses, 'search': search})

@login_required
@admin_required
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully!')
        return redirect('manage_courses')
    return render(request, 'management/delete_course.html', {'course': course})

@login_required
@admin_required
def manage_enrollments(request):
    search = request.GET.get('search', '')
    course_filter = request.GET.get('course', '')
    enrollments = Enrollment.objects.select_related('student', 'course').all()
    if search:
        enrollments = enrollments.filter(Q(student__username__icontains=search) | Q(course__title__icontains=search))
    if course_filter:
        enrollments = enrollments.filter(course_id=course_filter)
    return render(request, 'management/enrollments.html', {
        'enrollments': enrollments,
        'search': search,
        'course_filter': course_filter,
        'all_courses': Course.objects.all()
    })

@login_required
@admin_required
def toggle_enrollment(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    enrollment.is_active = not enrollment.is_active
    enrollment.save()
    messages.success(request, f'Enrollment {"activated" if enrollment.is_active else "deactivated"}!')
    return redirect('manage_enrollments')

@login_required
@admin_required
def mark_complete(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    enrollment.completed = True
    enrollment.progress = 100
    enrollment.save()
    messages.success(request, 'Enrollment marked as complete!')
    return redirect('manage_enrollments')
