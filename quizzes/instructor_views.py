from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models
from accounts.decorators import instructor_required
from .models import Quiz, QuizAttempt
from courses.models import Course

@login_required
@instructor_required
def instructor_assessments(request):
    courses = Course.objects.filter(instructor=request.user)
    quizzes = Quiz.objects.filter(instructor=request.user).select_related('module__course')
    
    total_quizzes = quizzes.count()
    total_attempts = QuizAttempt.objects.filter(quiz__in=quizzes).count()
    avg_score = QuizAttempt.objects.filter(quiz__in=quizzes, score__isnull=False).aggregate(
        avg=models.Avg('score')
    )['avg'] or 0
    
    context = {
        'courses': courses,
        'quizzes': quizzes,
        'total_quizzes': total_quizzes,
        'total_attempts': total_attempts,
        'avg_score': avg_score,
    }
    return render(request, 'quizzes/instructor_assessments.html', context)
