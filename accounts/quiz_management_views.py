from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import admin_required, instructor_required
from quizzes.models import Quiz, Question, Choice
from courses.models import Lesson

@login_required
def manage_quizzes(request):
    if request.user.is_admin:
        quizzes = Quiz.objects.all()
    elif request.user.is_instructor:
        quizzes = Quiz.objects.filter(instructor=request.user)
    else:
        return redirect('home')
    
    search = request.GET.get('search', '')
    if search:
        quizzes = quizzes.filter(title__icontains=search)
    
    return render(request, 'management/quizzes.html', {'quizzes': quizzes, 'search': search})

@login_required
def create_quiz_for_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    if not (request.user.is_admin or request.user == lesson.module.course.instructor):
        messages.error(request, 'You do not have permission to create quizzes for this lesson.')
        return redirect('courses:lesson_detail', pk=lesson_id)
    
    if request.method == 'POST':
        from django.utils.dateparse import parse_datetime
        
        quiz = Quiz.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description', ''),
            instructions=request.POST.get('instructions', ''),
            lesson=lesson,
            instructor=lesson.module.course.instructor,
            start_date=parse_datetime(request.POST.get('start_date')) if request.POST.get('start_date') else None,
            end_date=parse_datetime(request.POST.get('end_date')) if request.POST.get('end_date') else None,
            time_limit_minutes=request.POST.get('time_limit', 30),
            passing_score=request.POST.get('passing_score', 70),
            max_attempts=request.POST.get('max_attempts', 3),
            is_published=True
        )
        messages.success(request, 'Quiz created successfully!')
        return redirect('edit_quiz', quiz_id=quiz.id)
    
    return render(request, 'management/create_quiz.html', {'lesson': lesson})

@login_required
def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if not (request.user.is_admin or request.user == quiz.instructor):
        messages.error(request, 'You do not have permission to edit this quiz.')
        return redirect('manage_quizzes')
    
    if request.method == 'POST':
        quiz.title = request.POST.get('title')
        quiz.description = request.POST.get('description')
        quiz.instructions = request.POST.get('instructions', '')
        quiz.time_limit_minutes = request.POST.get('time_limit')
        quiz.passing_score = request.POST.get('passing_score')
        quiz.max_attempts = request.POST.get('max_attempts', 3)
        quiz.is_published = request.POST.get('is_published') == 'on'
        quiz.shuffle_questions = request.POST.get('shuffle_questions') == 'on'
        quiz.show_correct_answers = request.POST.get('show_correct_answers') == 'on'
        quiz.save()
        messages.success(request, 'Quiz updated successfully!')
        return redirect('edit_quiz', quiz_id=quiz.id)
    
    return render(request, 'management/edit_quiz.html', {'quiz': quiz})

@login_required
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if not (request.user.is_admin or request.user == quiz.instructor):
        messages.error(request, 'You do not have permission to delete this quiz.')
        return redirect('manage_quizzes')
    
    if request.method == 'POST':
        quiz.delete()
        messages.success(request, 'Quiz deleted successfully!')
        return redirect('manage_quizzes')
    
    return render(request, 'management/delete_quiz.html', {'quiz': quiz})

@login_required
def add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if not (request.user.is_admin or request.user == quiz.instructor):
        messages.error(request, 'You do not have permission.')
        return redirect('manage_quizzes')
    
    if request.method == 'POST':
        question_type = request.POST.get('question_type')
        question = Question.objects.create(
            quiz=quiz,
            text=request.POST.get('text'),
            question_type=question_type,
            points=request.POST.get('points', 1),
            order=quiz.questions.count() + 1
        )
        
        # Handle different question types
        if question_type == 'multiple_choice':
            for i in range(1, 5):
                choice_text = request.POST.get(f'choice_{i}')
                if choice_text:
                    Choice.objects.create(
                        question=question,
                        text=choice_text,
                        is_correct=request.POST.get('correct_choice') == str(i)
                    )
        elif question_type == 'true_false':
            correct_answer = request.POST.get('correct_answer')
            question.correct_answer = correct_answer
            question.save()
            # Create True/False choices
            Choice.objects.create(question=question, text='True', is_correct=(correct_answer == 'true'))
            Choice.objects.create(question=question, text='False', is_correct=(correct_answer == 'false'))
        elif question_type == 'short_answer':
            question.correct_answer = request.POST.get('correct_answer', '')
            question.save()
        
        messages.success(request, 'Question added successfully!')
        return redirect('edit_quiz', quiz_id=quiz.id)
    
    return render(request, 'management/add_question.html', {'quiz': quiz})

@login_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    quiz_id = question.quiz.id
    
    if not (request.user.is_admin or request.user == question.quiz.instructor):
        messages.error(request, 'You do not have permission.')
        return redirect('manage_quizzes')
    
    question.delete()
    messages.success(request, 'Question deleted successfully!')
    return redirect('edit_quiz', quiz_id=quiz_id)

@login_required
def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    
    if not (request.user.is_admin or request.user == question.quiz.instructor):
        messages.error(request, 'You do not have permission.')
        return redirect('manage_quizzes')
    
    if request.method == 'POST':
        question.text = request.POST.get('text')
        question.points = request.POST.get('points', 1)
        question_type = request.POST.get('question_type')
        
        # If type changed, delete old choices
        if question.question_type != question_type:
            question.choices.all().delete()
            question.question_type = question_type
        
        if question_type == 'multiple_choice':
            question.choices.all().delete()
            for i in range(1, 5):
                choice_text = request.POST.get(f'choice_{i}')
                if choice_text:
                    Choice.objects.create(
                        question=question,
                        text=choice_text,
                        is_correct=request.POST.get('correct_choice') == str(i)
                    )
        elif question_type == 'true_false':
            correct_answer = request.POST.get('correct_answer')
            question.correct_answer = correct_answer
            question.choices.all().delete()
            Choice.objects.create(question=question, text='True', is_correct=(correct_answer == 'true'))
            Choice.objects.create(question=question, text='False', is_correct=(correct_answer == 'false'))
        elif question_type == 'short_answer':
            question.correct_answer = request.POST.get('correct_answer', '')
        
        question.save()
        messages.success(request, 'Question updated successfully!')
        return redirect('edit_quiz', quiz_id=question.quiz.id)
    
    context = {
        'question': question,
        'quiz': question.quiz
    }
    return render(request, 'management/edit_question.html', context)
