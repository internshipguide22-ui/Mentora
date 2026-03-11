from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.admin_views import admin_analytics
from accounts.analytics_views import analytics_dashboard, export_analytics_csv, export_users_csv, export_enrollments_csv
from accounts.management_views import manage_users, create_user, edit_user, delete_user, manage_courses, delete_course, manage_enrollments, toggle_enrollment, mark_complete
from accounts.quiz_management_views import manage_quizzes, create_quiz_for_lesson, edit_quiz, delete_quiz, add_question, delete_question, edit_question
from accounts.certificate_review_views import manage_certificates, revoke_certificate, regenerate_certificate, manage_reviews, delete_review
from accounts.instructor_management_views import instructor_details, course_student_progress, student_course_details, all_instructors, all_students_progress, system_statistics
from accounts.instructor_student_views import instructor_students_view, student_instructors_view

# These are placeholder views. We will create real ones in the accounts app later.
from django.views.generic import TemplateView

urlpatterns = [
    # Admin
    path('admin/analytics/', admin_analytics, name='admin_analytics'),
    path('admin/', admin.site.urls),
    
    # Analytics
    path('analytics/', analytics_dashboard, name='analytics_dashboard'),
    path('analytics/export/', export_analytics_csv, name='export_analytics_csv'),
    path('analytics/export/users/', export_users_csv, name='export_users_csv'),
    path('analytics/export/enrollments/', export_enrollments_csv, name='export_enrollments_csv'),
    
    # Management
    path('manage/instructor-students/', instructor_students_view, name='instructor_students_view'),
    path('manage/student-instructors/', student_instructors_view, name='student_instructors_view'),
    path('manage/instructors/', all_instructors, name='all_instructors'),
    path('manage/instructors/<int:instructor_id>/', instructor_details, name='instructor_details'),
    path('manage/courses/<int:course_id>/students/', course_student_progress, name='course_student_progress'),
    path('manage/students/<int:student_id>/course/<int:course_id>/', student_course_details, name='student_course_details'),
    path('manage/students/progress/', all_students_progress, name='all_students_progress'),
    path('manage/statistics/', system_statistics, name='system_statistics'),
    path('manage/users/', manage_users, name='manage_users'),
    path('manage/users/create/', create_user, name='create_user'),
    path('manage/users/<int:user_id>/edit/', edit_user, name='edit_user'),
    path('manage/users/<int:user_id>/delete/', delete_user, name='delete_user'),
    path('manage/courses/', manage_courses, name='manage_courses'),
    path('manage/courses/<int:course_id>/delete/', delete_course, name='delete_course'),
    path('manage/enrollments/', manage_enrollments, name='manage_enrollments'),
    path('manage/enrollments/<int:enrollment_id>/toggle/', toggle_enrollment, name='toggle_enrollment'),
    path('manage/enrollments/<int:enrollment_id>/complete/', mark_complete, name='mark_complete'),
    path('manage/quizzes/', manage_quizzes, name='manage_quizzes'),
    path('manage/lesson/<int:lesson_id>/quiz/create/', create_quiz_for_lesson, name='create_quiz_for_lesson'),
    path('manage/quiz/<int:quiz_id>/edit/', edit_quiz, name='edit_quiz'),
    path('manage/quiz/<int:quiz_id>/delete/', delete_quiz, name='delete_quiz'),
    path('manage/quiz/<int:quiz_id>/question/add/', add_question, name='add_question'),
    path('manage/question/<int:question_id>/edit/', edit_question, name='edit_question'),
    path('manage/question/<int:question_id>/delete/', delete_question, name='delete_question'),
    path('manage/certificates/', manage_certificates, name='manage_certificates'),
    path('manage/certificates/<int:certificate_id>/revoke/', revoke_certificate, name='revoke_certificate'),
    path('manage/certificates/<int:certificate_id>/regenerate/', regenerate_certificate, name='regenerate_certificate'),
    path('manage/reviews/', manage_reviews, name='manage_reviews'),
    path('manage/reviews/<int:review_id>/delete/', delete_review, name='delete_review'),

    # Categories
    path('manage/categories/', include('accounts.category_urls')),

    # Frontend
    path('', include('frontend.urls')),

    # Accounts
    path('accounts/', include('accounts.urls')),

    # Courses
    path('courses/', include('courses.urls')),
    
    # Certificates
    path('certificates/', include('certificates.urls')),
    
    # Quizzes
    path('quizzes/', include('quizzes.urls')),
    
    # Reviews
    path('reviews/', include('reviews.urls')),
    
    # Lessons
    path('lessons/', include('lessons.urls')),

    path('create-course/', TemplateView.as_view(template_name="base.html"), name='create_course'),
    path('my-quizzes/', TemplateView.as_view(template_name="base.html"), name='list_quizzes'),
    path('my-certificates/', TemplateView.as_view(template_name="base.html"), name='list_certificates'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)