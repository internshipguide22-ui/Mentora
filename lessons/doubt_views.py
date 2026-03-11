from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import student_required, instructor_required
from courses.models import Lesson, Enrollment
from .models import LessonDoubt, DoubtResponse

@login_required
@student_required
def add_doubt(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    course = lesson.module.course
    
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course, is_active=True)
    
    if request.method == 'POST':
        question = request.POST.get('question')
        if question:
            LessonDoubt.objects.create(lesson=lesson, student=request.user, question=question)
            messages.success(request, "Your doubt has been submitted. The instructor will be notified.")
        return redirect('courses:lesson_detail', pk=lesson.pk)
    
    return redirect('courses:lesson_detail', pk=lesson.pk)

@login_required
@instructor_required
def view_doubts(request):
    courses = request.user.courses_taught.all()
    doubts = LessonDoubt.objects.filter(lesson__module__course__in=courses).select_related('lesson', 'student')
    
    unresolved_count = doubts.filter(is_resolved=False).count()
    
    context = {
        'doubts': doubts,
        'unresolved_count': unresolved_count,
    }
    return render(request, 'lessons/instructor_doubts.html', context)

@login_required
@student_required
def my_doubts(request):
    doubts = LessonDoubt.objects.filter(student=request.user).select_related('lesson__module__course').order_by('-created_at')
    
    answered_count = doubts.filter(responses__isnull=False).distinct().count()
    pending_count = doubts.filter(responses__isnull=True).count()
    
    context = {
        'doubts': doubts,
        'answered_count': answered_count,
        'pending_count': pending_count,
    }
    return render(request, 'lessons/student_doubts.html', context)

@login_required
@instructor_required
def respond_doubt(request, doubt_id):
    doubt = get_object_or_404(LessonDoubt, pk=doubt_id)
    course = doubt.lesson.module.course
    
    if course.instructor != request.user and not request.user.is_admin:
        messages.error(request, "You are not authorized to respond to this doubt.")
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        response_text = request.POST.get('response')
        if response_text:
            DoubtResponse.objects.create(doubt=doubt, instructor=request.user, response=response_text)
            messages.success(request, "Your response has been posted.")
        return redirect('lessons:view_doubts')
    
    context = {'doubt': doubt}
    return render(request, 'lessons/respond_doubt.html', context)
