from django.urls import path
from . import views

# We will create the actual views for these later
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.home, name='home'),
]