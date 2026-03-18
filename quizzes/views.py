from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg

from accounts.decorators import instructor_required, student_required
from .models import Quiz, Question, Choice, QuizAttempt, QuizResponse
from .forms import QuizForm, QuestionForm
from courses.models import Course, Enrollment
from courses.progress import get_module_access_map

@login_required
@instructor_required
def create_quiz(request, course_id):
    course = get_object_or_404(Course, pk=course_id, instructor=request.user)
    if request.method == 'POST':
        form = QuizForm(request.POST, instructor=request.user)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.instructor = request.user
            quiz.save()
            messages.success(request, "Quiz created successfully!")
            return redirect('quizzes:quiz_detail', quiz_id=quiz.pk)
    else:
        form = QuizForm(instructor=request.user)
    return render(request, 'quizzes/quiz_form.html', {'form': form, 'course': course})

@login_required
@instructor_required
def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id, instructor=request.user)
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz, instructor=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Quiz updated successfully!")
            return redirect('quizzes:quiz_detail', quiz_id=quiz.pk)
    else:
        form = QuizForm(instance=quiz, instructor=request.user)
    return render(request, 'quizzes/quiz_form.html', {'form': form, 'quiz': quiz})

@login_required
@instructor_required
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id, instructor=request.user)
    if request.method == 'POST':
        course_id = quiz.module.course.pk
        quiz.delete()
        messages.success(request, "Quiz deleted successfully!")
        return redirect('courses:course_detail', pk=course_id)
    return render(request, 'quizzes/quiz_confirm_delete.html', {'quiz': quiz})

@login_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    course = quiz.module.course
    
    is_enrolled = Enrollment.objects.filter(student=request.user, course=course, is_active=True).exists()
    is_instructor = request.user == course.instructor
    
    if not (is_enrolled or is_instructor or request.user.is_admin):
        messages.error(request, "You must be enrolled in this course to access quizzes.")
        return redirect('courses:course_detail', pk=course.pk)

    if is_enrolled and request.user.is_student:
        module_access, _ = get_module_access_map(course, request.user)
        if not module_access.get(quiz.module_id, {'unlocked': True})['unlocked']:
            messages.error(request, "Complete the previous module to unlock this one.")
            return redirect('courses:course_detail', pk=course.pk)
    
    attempts = QuizAttempt.objects.filter(student=request.user, quiz=quiz).order_by('-started_at')
    attempts_count = attempts.count()
    can_attempt = attempts_count < quiz.max_attempts
    
    best_score = attempts.filter(score__isnull=False).aggregate(Avg('score'))['score__avg'] or 0
    
    context = {
        'quiz': quiz,
        'course': course,
        'attempts': attempts,
        'attempts_count': attempts_count,
        'can_attempt': can_attempt,
        'attempts_remaining': quiz.max_attempts - attempts_count,
        'best_score': best_score,
    }
    return render(request, 'quizzes/quiz_detail.html', context)

@login_required
@student_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    course = quiz.module.course
    
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course, is_active=True)
    module_access, _ = get_module_access_map(course, request.user)
    if not module_access.get(quiz.module_id, {'unlocked': True})['unlocked']:
        messages.error(request, "Complete the previous module to unlock this one.")
        return redirect('courses:course_detail', pk=course.pk)
    
    attempts_count = QuizAttempt.objects.filter(student=request.user, quiz=quiz).count()
    if attempts_count >= quiz.max_attempts:
        messages.error(request, f"You have reached the maximum number of attempts ({quiz.max_attempts}) for this quiz.")
        return redirect('quizzes:quiz_detail', quiz_id=quiz.pk)
    
    if request.method == 'POST':
        start_time = timezone.now()
        attempt = QuizAttempt.objects.create(
            student=request.user,
            quiz=quiz,
            attempt_number=attempts_count + 1,
            started_at=start_time
        )
        
        total_points = 0
        earned_points = 0
        
        for question in quiz.questions.all():
            total_points += question.points
            
            if question.question_type == 'multiple_choice':
                selected_choice_id = request.POST.get(f'question_{question.pk}')
                if selected_choice_id:
                    selected_choice = Choice.objects.get(pk=selected_choice_id)
                    is_correct = selected_choice.is_correct
                    QuizResponse.objects.create(
                        attempt=attempt,
                        question=question,
                        selected_choice=selected_choice,
                        is_correct=is_correct
                    )
                    if is_correct:
                        earned_points += question.points
            
            elif question.question_type == 'true_false':
                answer = request.POST.get(f'question_{question.pk}')
                if answer:
                    is_correct = answer.lower() == question.correct_answer.lower()
                    QuizResponse.objects.create(
                        attempt=attempt,
                        question=question,
                        text_response=answer,
                        is_correct=is_correct
                    )
                    if is_correct:
                        earned_points += question.points
            
            elif question.question_type == 'short_answer':
                answer = request.POST.get(f'question_{question.pk}', '').strip()
                QuizResponse.objects.create(
                    attempt=attempt,
                    question=question,
                    text_response=answer,
                    is_correct=None,
                    manually_graded=True
                )
        
        score = (earned_points / total_points * 100) if total_points > 0 else 0
        passed = score >= quiz.passing_score
        
        attempt.completed_at = timezone.now()
        attempt.time_taken_minutes = int((attempt.completed_at - attempt.started_at).total_seconds() / 60)
        attempt.score = score
        attempt.passed = passed
        attempt.save()
        
        if passed:
            messages.success(request, f"Congratulations! You passed with {score:.1f}%")
        else:
            messages.warning(request, f"You scored {score:.1f}%. Passing score is {quiz.passing_score}%")
        
        return redirect('quizzes:quiz_result', attempt_id=attempt.pk)
    
    # attempt = QuizAttempt.objects.create(student=request.user, quiz=quiz, attempt_number=attempts_count)
    context = {
        'quiz': quiz,
        # 'attempt': attempt,
        'attempts_remaining': quiz.max_attempts - attempts_count,
    }
    return render(request, 'quizzes/take_quiz.html', context)

@login_required
def quiz_result(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, pk=attempt_id)
    quiz = attempt.quiz
    
    # Check permission - student can see their own, instructor can see all
    if not (request.user == attempt.student or request.user == quiz.instructor or request.user.is_admin):
        messages.error(request, "You don't have permission to view this result.")
        return redirect('home')
    
    responses = attempt.responses.all().select_related('question', 'selected_choice')
    
    context = {
        'attempt': attempt,
        'quiz': quiz,
        'responses': responses,
        'is_instructor_view': request.user == quiz.instructor or request.user.is_admin,
    }
    return render(request, 'quizzes/quiz_result.html', context)

@login_required
@instructor_required
def create_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id, instructor=request.user)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.order = quiz.questions.count() + 1
            question.save()
            messages.success(request, "Question added successfully!")
            return redirect('quizzes:quiz_detail', quiz_id=quiz.pk)
    else:
        form = QuestionForm()
    return render(request, 'quizzes/question_form.html', {'form': form, 'quiz': quiz})

@login_required
@instructor_required
def edit_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id, quiz__instructor=request.user)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, "Question updated successfully!")
            return redirect('quizzes:quiz_detail', quiz_id=question.quiz.pk)
    else:
        form = QuestionForm(instance=question)
    return render(request, 'quizzes/question_form.html', {'form': form, 'question': question, 'quiz': question.quiz})

@login_required
@instructor_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id, quiz__instructor=request.user)
    quiz_id = question.quiz.pk
    if request.method == 'POST':
        question.delete()
        messages.success(request, "Question deleted successfully!")
        return redirect('quizzes:quiz_detail', quiz_id=quiz_id)
    return render(request, 'quizzes/question_confirm_delete.html', {'question': question})

@login_required
@instructor_required
def create_choice(request, question_id):
    question = get_object_or_404(Question, pk=question_id, quiz__instructor=request.user)
    if request.method == 'POST':
        text = request.POST.get('text')
        is_correct = request.POST.get('is_correct') == 'on'
        Choice.objects.create(question=question, text=text, is_correct=is_correct)
        messages.success(request, "Choice added successfully!")
        return redirect('quizzes:quiz_detail', quiz_id=question.quiz.pk)
    return render(request, 'quizzes/choice_form.html', {'question': question})

@login_required
@instructor_required
def edit_choice(request, choice_id):
    choice = get_object_or_404(Choice, pk=choice_id, question__quiz__instructor=request.user)
    if request.method == 'POST':
        choice.text = request.POST.get('text')
        choice.is_correct = request.POST.get('is_correct') == 'on'
        choice.save()
        messages.success(request, "Choice updated successfully!")
        return redirect('quizzes:quiz_detail', quiz_id=choice.question.quiz.pk)
    return render(request, 'quizzes/choice_form.html', {'choice': choice})

@login_required
@instructor_required
def delete_choice(request, choice_id):
    choice = get_object_or_404(Choice, pk=choice_id, question__quiz__instructor=request.user)
    quiz_id = choice.question.quiz.pk
    if request.method == 'POST':
        choice.delete()
        messages.success(request, "Choice deleted successfully!")
        return redirect('quizzes:quiz_detail', quiz_id=quiz_id)
    return render(request, 'quizzes/choice_confirm_delete.html', {'choice': choice})

@login_required
def quiz_results_dashboard(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    
    # Check permission
    if not (request.user == quiz.instructor or request.user.is_admin):
        messages.error(request, "You don't have permission to view these results.")
        return redirect('quizzes:quiz_detail', quiz_id=quiz_id)
    
    # Get all attempts for this quiz
    attempts = QuizAttempt.objects.filter(quiz=quiz, completed_at__isnull=False).select_related('student').order_by('-completed_at')
    
    # Calculate statistics
    total_attempts = attempts.count()
    passed_attempts = attempts.filter(passed=True).count()
    failed_attempts = total_attempts - passed_attempts
    avg_score = attempts.aggregate(Avg('score'))['score__avg'] or 0
    
    # Group by student
    student_results = {}
    for attempt in attempts:
        student = attempt.student
        if student not in student_results:
            student_results[student] = {
                'attempts': [],
                'best_score': 0,
                'passed': False,
                'total_attempts': 0
            }
        student_results[student]['attempts'].append(attempt)
        student_results[student]['total_attempts'] += 1
        if attempt.score > student_results[student]['best_score']:
            student_results[student]['best_score'] = attempt.score
        if attempt.passed:
            student_results[student]['passed'] = True
    
    context = {
        'quiz': quiz,
        'total_attempts': total_attempts,
        'passed_attempts': passed_attempts,
        'failed_attempts': failed_attempts,
        'avg_score': avg_score,
        'student_results': student_results,
        'pass_rate': (passed_attempts / total_attempts * 100) if total_attempts > 0 else 0,
    }
    return render(request, 'quizzes/quiz_results_dashboard.html', context)
