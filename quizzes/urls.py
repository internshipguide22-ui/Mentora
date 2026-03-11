from django.urls import path
from . import views, instructor_views

app_name = 'quizzes'

urlpatterns = [
    path('assessments/', instructor_views.instructor_assessments, name='instructor_assessments'),
    path('course/<int:course_id>/quiz/create/', views.create_quiz, name='create_quiz'),
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('quiz/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('quiz/<int:quiz_id>/edit/', views.edit_quiz, name='edit_quiz'),
    path('quiz/<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),
    path('attempt/<int:attempt_id>/result/', views.quiz_result, name='quiz_result'),
    path('quiz/<int:quiz_id>/question/create/', views.create_question, name='create_question'),
    path('question/<int:question_id>/edit/', views.edit_question, name='edit_question'),
    path('question/<int:question_id>/delete/', views.delete_question, name='delete_question'),
    path('question/<int:question_id>/choice/create/', views.create_choice, name='create_choice'),
    path('choice/<int:choice_id>/edit/', views.edit_choice, name='edit_choice'),
    path('choice/<int:choice_id>/delete/', views.delete_choice, name='delete_choice'),
    path('quiz/<int:quiz_id>/results/', views.quiz_results_dashboard, name='quiz_results'),
]
