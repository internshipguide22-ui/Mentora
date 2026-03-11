from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LessonViewSet
from . import doubt_views

app_name = 'lessons'

router = DefaultRouter()
router.register(r'lessons', LessonViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('lesson/<int:lesson_id>/doubt/add/', doubt_views.add_doubt, name='add_doubt'),
    path('doubts/', doubt_views.view_doubts, name='view_doubts'),
    path('my-doubts/', doubt_views.my_doubts, name='my_doubts'),
    path('doubt/<int:doubt_id>/respond/', doubt_views.respond_doubt, name='respond_doubt'),
]