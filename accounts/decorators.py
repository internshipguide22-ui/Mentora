from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from functools import wraps

def instructor_required(function=None, redirect_field_name=None, login_url='login'):
    """
    Decorator for views that checks that the user is logged in and is an instructor,
    redirecting to the login page if necessary.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.is_instructor:
                return view_func(request, *args, **kwargs)
            messages.error(request, "You must be an instructor to access this page.")
            return redirect(login_url)
        return _wrapped_view

    if function:
        return decorator(function)
    return decorator

def student_required(function=None, redirect_field_name=None, login_url='login'):
    """
    Decorator for views that checks that the user is logged in and is a student.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.is_student:
                return view_func(request, *args, **kwargs)
            messages.error(request, "You must be a student to access this page.")
            return redirect(login_url)
        return _wrapped_view

    if function:
        return decorator(function)
    return decorator

def admin_required(function=None, redirect_field_name=None, login_url='login'):
    """
    Decorator for views that checks that the user is logged in and is an admin.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.is_admin:
                return view_func(request, *args, **kwargs)
            messages.error(request, "You must be an admin to access this page.")
            return redirect(login_url)
        return _wrapped_view

    if function:
        return decorator(function)
    return decorator

def owns_course(view_func):
    """
    Decorator to check if the user owns the course or is an admin.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        course_id = kwargs.get('course_id') or kwargs.get('pk')
        if not course_id:
            raise PermissionDenied("Course not found")
        
        from courses.models import Course
        try:
            course = Course.objects.get(pk=course_id)
            if request.user == course.instructor or request.user.is_admin:
                return view_func(request, *args, **kwargs)
        except Course.DoesNotExist:
            raise PermissionDenied("Course not found")
            
        raise PermissionDenied("You don't have permission to modify this course")
    return _wrapped_view

def enrolled_required(view_func):
    """
    Decorator to check if the user is enrolled in the course, is the instructor, or is an admin.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        course_id = kwargs.get('course_id') or kwargs.get('pk')
        if not course_id:
            raise PermissionDenied("Course not found")
        
        from courses.models import Course, Enrollment
        try:
            course = Course.objects.get(pk=course_id)
            is_enrolled = Enrollment.objects.filter(
                student=request.user,
                course=course,
                is_active=True
            ).exists()
            
            if is_enrolled or request.user == course.instructor or request.user.is_admin:
                return view_func(request, *args, **kwargs)
                
            messages.error(request, "You must be enrolled in this course to access this content.")
            return redirect('courses:course_detail', pk=course_id)
            
        except Course.DoesNotExist:
            raise PermissionDenied("Course not found")
    return _wrapped_view
