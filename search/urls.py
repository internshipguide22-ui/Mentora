from django.urls import path

from .views import CourseSearchView


urlpatterns = [
    path('course-search/', CourseSearchView.as_view(), name='course_search'),
]
