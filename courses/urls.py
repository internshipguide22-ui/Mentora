from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.CourseListView.as_view(), name='course_list'),
    path('create/', views.CourseCreateView.as_view(), name='course_create'),
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('<int:pk>/update/', views.CourseUpdateView.as_view(), name='course_update'),
    path('<int:pk>/enroll/', views.enroll_course, name='course_enroll'),
    path('<int:pk>/notes/upload/', views.upload_course_note, name='course_note_upload'),
    
    # Module URLs
    path('<int:course_pk>/modules/add/', views.create_module, name='module_create'),
    
    # Lesson URLs
    path('<int:course_pk>/lessons/add/', views.LessonCreateView.as_view(), name='lesson_create'),
    path('lessons/<int:pk>/', views.lesson_detail, name='lesson_detail'),
    path('lessons/<int:pk>/update/', views.LessonUpdateView.as_view(), name='lesson_update'),
    path('lessons/<int:pk>/delete/', views.LessonDeleteView.as_view(), name='lesson_delete'),
    path('lessons/<int:pk>/complete/', views.mark_lesson_complete, name='lesson_complete'),
    
    # Instructor Student Management
    path('<int:pk>/students/', views.manage_course_students, name='manage_students'),
    path('enrollment/<int:enrollment_id>/toggle/', views.toggle_student_enrollment, name='toggle_enrollment'),
    path('instructor/students/', views.instructor_manage_all_students, name='instructor_manage_all_students'),
]
