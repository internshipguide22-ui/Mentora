from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Q, Avg
from accounts.models import User
from courses.models import Course, Enrollment, Module
from lessons.models import LessonCompletion
from quizzes.models import QuizAttempt

@staff_member_required
def instructor_details(request, instructor_id):
    """Detailed view of instructor's courses and students"""
    instructor = get_object_or_404(User, id=instructor_id, user_type='instructor')
    courses = Course.objects.filter(instructor=instructor).annotate(
        enrollment_count=Count('enrollments', filter=Q(enrollments__is_active=True)),
        completion_count=Count('enrollments', filter=Q(enrollments__completed=True))
    )
    
    # Get all students across instructor's courses
    student_ids = Enrollment.objects.filter(
        course__instructor=instructor,
        is_active=True
    ).values_list('student_id', flat=True).distinct()
    
    total_students = len(student_ids)
    
    context = {
        'instructor': instructor,
        'courses': courses,
        'total_students': total_students,
        'total_courses': courses.count(),
    }
    return render(request, 'admin/instructor_details.html', context)

@staff_member_required
def course_student_progress(request, course_id):
    """Detailed view of all students in a course with module-level progress"""
    course = get_object_or_404(Course, id=course_id)
    enrollments = Enrollment.objects.filter(
        course=course,
        is_active=True
    ).select_related('student').order_by('-enrollment_date')
    
    # Prepare student progress data
    student_data = []
    for enrollment in enrollments:
        total_lessons = sum(module.lessons.count() for module in course.modules.all())
        completed_lessons = LessonCompletion.objects.filter(
            student=enrollment.student,
            lesson__module__course=course
        ).count()
        
        # Module-wise progress
        module_progress = []
        for module in course.modules.all():
            module_total = module.lessons.count()
            module_completed = LessonCompletion.objects.filter(
                student=enrollment.student,
                lesson__module=module
            ).count()
            module_progress.append({
                'module': module,
                'total': module_total,
                'completed': module_completed,
                'percentage': (module_completed / module_total * 100) if module_total > 0 else 0
            })
        
        student_data.append({
            'enrollment': enrollment,
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'module_progress': module_progress
        })
    
    context = {
        'course': course,
        'student_data': student_data,
        'total_students': enrollments.count(),
    }
    return render(request, 'admin/course_student_progress.html', context)

@staff_member_required
def student_course_details(request, student_id, course_id):
    """Detailed view of a specific student's progress in a course"""
    student = get_object_or_404(User, id=student_id, user_type='student')
    course = get_object_or_404(Course, id=course_id)
    enrollment = get_object_or_404(Enrollment, student=student, course=course)
    
    # Get completed lessons
    completed_lesson_ids = LessonCompletion.objects.filter(
        student=student,
        lesson__module__course=course
    ).values_list('lesson_id', flat=True)
    
    # Module-wise details
    module_details = []
    for module in course.modules.all():
        lessons = []
        for lesson in module.lessons.all():
            is_completed = lesson.id in completed_lesson_ids
            completion = None
            if is_completed:
                completion = LessonCompletion.objects.get(student=student, lesson=lesson)
            
            # Get quiz attempts for this lesson
            quiz_attempts = QuizAttempt.objects.filter(
                student=student,
                quiz__lesson=lesson
            ).order_by('-started_at')
            
            lessons.append({
                'lesson': lesson,
                'is_completed': is_completed,
                'completion_date': completion.completed_at if completion else None,
                'quiz_attempts': quiz_attempts
            })
        
        module_total = module.lessons.count()
        module_completed = sum(1 for l in lessons if l['is_completed'])
        
        module_details.append({
            'module': module,
            'lessons': lessons,
            'total': module_total,
            'completed': module_completed,
            'percentage': (module_completed / module_total * 100) if module_total > 0 else 0
        })
    
    context = {
        'student': student,
        'course': course,
        'enrollment': enrollment,
        'module_details': module_details,
    }
    return render(request, 'admin/student_course_details.html', context)

@staff_member_required
def all_instructors(request):
    """List all instructors with their statistics"""
    instructors = User.objects.filter(user_type='instructor').annotate(
        course_count=Count('courses_taught'),
        student_count=Count('courses_taught__enrollments', filter=Q(courses_taught__enrollments__is_active=True), distinct=True)
    ).order_by('-course_count')
    
    context = {
        'instructors': instructors,
    }
    return render(request, 'admin/all_instructors.html', context)

@staff_member_required
def all_students_progress(request):
    """List all students with their overall progress"""
    students = User.objects.filter(user_type='student').annotate(
        enrollment_count=Count('enrollments', filter=Q(enrollments__is_active=True)),
        completed_count=Count('enrollments', filter=Q(enrollments__completed=True))
    ).order_by('-enrollment_count')
    
    student_data = []
    for student in students:
        enrollments = Enrollment.objects.filter(student=student, is_active=True)
        avg_progress = enrollments.aggregate(Avg('progress'))['progress__avg'] or 0
        
        student_data.append({
            'student': student,
            'enrollments': enrollments.count(),
            'completed': enrollments.filter(completed=True).count(),
            'avg_progress': avg_progress
        })
    
    context = {
        'student_data': student_data,
    }
    return render(request, 'admin/all_students_progress.html', context)

@staff_member_required
def system_statistics(request):
    """Comprehensive system statistics"""
    # Instructor statistics
    instructors = User.objects.filter(user_type='instructor').annotate(
        course_count=Count('courses_taught'),
        student_count=Count('courses_taught__enrollments__student', filter=Q(courses_taught__enrollments__is_active=True), distinct=True),
        active_enrollments=Count('courses_taught__enrollments', filter=Q(courses_taught__enrollments__is_active=True))
    ).order_by('-student_count')
    
    # Course statistics
    courses = Course.objects.annotate(
        student_count=Count('enrollments', filter=Q(enrollments__is_active=True)),
        completed_count=Count('enrollments', filter=Q(enrollments__completed=True))
    ).select_related('instructor')
    
    # Calculate completion rate
    for course in courses:
        if course.student_count > 0:
            course.completion_rate = (course.completed_count / course.student_count) * 100
        else:
            course.completion_rate = 0
    
    context = {
        'instructors': instructors,
        'courses': courses,
    }
    return render(request, 'management/statistics.html', context)
