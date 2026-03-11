from django.urls import path
from .views import (
    VideoContentCreateView, VideoContentUpdateView, VideoContentDeleteView,
    TextContentCreateView, TextContentUpdateView, TextContentDeleteView,
    QuizContentCreateView, QuizContentUpdateView, QuizContentDeleteView,
    AssignmentContentCreateView, AssignmentContentUpdateView, AssignmentContentDeleteView
)

app_name = 'lesson_content'

urlpatterns = [
    path('lesson/<int:lesson_pk>/video/create/', VideoContentCreateView.as_view(), name='video_create'),
    path('lesson/<int:lesson_pk>/video/<int:pk>/update/', VideoContentUpdateView.as_view(), name='video_update'),
    path('lesson/<int:lesson_pk>/video/<int:pk>/delete/', VideoContentDeleteView.as_view(), name='video_delete'),

    path('lesson/<int:lesson_pk>/text/create/', TextContentCreateView.as_view(), name='text_create'),
    path('lesson/<int:lesson_pk>/text/<int:pk>/update/', TextContentUpdateView.as_view(), name='text_update'),
    path('lesson/<int:lesson_pk>/text/<int:pk>/delete/', TextContentDeleteView.as_view(), name='text_delete'),

    path('lesson/<int:lesson_pk>/quiz/create/', QuizContentCreateView.as_view(), name='quiz_create'),
    path('lesson/<int:lesson_pk>/quiz/<int:pk>/update/', QuizContentUpdateView.as_view(), name='quiz_update'),
    path('lesson/<int:lesson_pk>/quiz/<int:pk>/delete/', QuizContentDeleteView.as_view(), name='quiz_delete'),

    path('lesson/<int:lesson_pk>/assignment/create/', AssignmentContentCreateView.as_view(), name='assignment_create'),
    path('lesson/<int:lesson_pk>/assignment/<int:pk>/update/', AssignmentContentUpdateView.as_view(), name='assignment_update'),
    path('lesson/<int:lesson_pk>/assignment/<int:pk>/delete/', AssignmentContentDeleteView.as_view(), name='assignment_delete'),
]