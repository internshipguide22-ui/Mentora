from django.urls import path
from . import category_views

urlpatterns = [
    path('', category_views.manage_categories, name='manage_categories'),
    path('create/', category_views.create_category, name='create_category'),
    path('<int:category_id>/edit/', category_views.edit_category, name='edit_category'),
    path('<int:category_id>/delete/', category_views.delete_category, name='delete_category'),
]
