from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q, Prefetch
from accounts.models import User
from courses.models import Course, Enrollment
from lessons.models import LessonCompletion

@staff_member_required
def instructor_students_view(request):
    """View all students grouped by instructor"""
    instructors = User.objects.filter(user_type='instructor').prefetch_related(
        Prefetch('courses_taught', queryset=Course.objects.all()),
        Prefetch('courses_taught__enrollments', queryset=Enrollment.objects.filter(is_active=True).select_related('student'))
    ).annotate(
        total_students=Count('courses_taught__enrollments', filter=Q(courses_taught__enrollments__is_active=True), distinct=True)
    ).order_by('-total_students')
    
    instructor_data = []
    for instructor in instructors:
        # Get unique students across all instructor's courses
        student_ids = set()
        student_courses = {}
        
        for course in instructor.courses_taught.all():
            for enrollment in course.enrollments.all():
                student = enrollment.student
                student_ids.add(student.id)
                
                if student.id not in student_courses:
                    student_courses[student.id] = {
                        'student': student,
                        'courses': [],
                        'total_progress': 0,
                        'completed_count': 0
                    }
                
                student_courses[student.id]['courses'].append({
                    'course': course,
                    'enrollment': enrollment
                })
                student_courses[student.id]['total_progress'] += float(enrollment.progress)
                if enrollment.completed:
                    student_courses[student.id]['completed_count'] += 1
        
        # Calculate average progress
        for student_id in student_courses:
            course_count = len(student_courses[student_id]['courses'])
            if course_count > 0:
                student_courses[student_id]['avg_progress'] = student_courses[student_id]['total_progress'] / course_count
        
        instructor_data.append({
            'instructor': instructor,
            'student_count': len(student_ids),
            'students': list(student_courses.values())
        })
    
    context = {
        'instructor_data': instructor_data,
        'total_instructors': instructors.count()
    }
    return render(request, 'admin/instructor_students_view.html', context)

@staff_member_required
def student_instructors_view(request):
    """View all instructors a student is learning from"""
    students = User.objects.filter(user_type='student').prefetch_related(
        Prefetch('enrollments', queryset=Enrollment.objects.filter(is_active=True).select_related('course__instructor'))
    ).annotate(
        enrollment_count=Count('enrollments', filter=Q(enrollments__is_active=True))
    ).order_by('-enrollment_count')
    
    student_data = []
    for student in students:
        instructor_courses = {}
        
        for enrollment in student.enrollments.all():
            instructor = enrollment.course.instructor
            
            if instructor.id not in instructor_courses:
                instructor_courses[instructor.id] = {
                    'instructor': instructor,
                    'courses': [],
                    'total_progress': 0,
                    'completed_count': 0
                }
            
            instructor_courses[instructor.id]['courses'].append({
                'course': enrollment.course,
                'enrollment': enrollment
            })
            instructor_courses[instructor.id]['total_progress'] += float(enrollment.progress)
            if enrollment.completed:
                instructor_courses[instructor.id]['completed_count'] += 1
        
        # Calculate average progress per instructor
        for instructor_id in instructor_courses:
            course_count = len(instructor_courses[instructor_id]['courses'])
            if course_count > 0:
                instructor_courses[instructor_id]['avg_progress'] = instructor_courses[instructor_id]['total_progress'] / course_count
        
        student_data.append({
            'student': student,
            'instructor_count': len(instructor_courses),
            'instructors': list(instructor_courses.values())
        })
    
    context = {
        'student_data': student_data,
        'total_students': students.count()
    }
    return render(request, 'admin/student_instructors_view.html', context)
