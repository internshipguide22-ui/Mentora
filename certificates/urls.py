from django.urls import path
from . import views

app_name = 'certificates'

urlpatterns = [
    path('generate/<int:enrollment_id>/', views.generate_certificate_view, name='generate'),
    path('view/<int:certificate_id>/', views.view_certificate, name='view_certificate'),
    path('view/<uuid:uuid>/', views.verify_certificate, name='view_certificate_uuid'),
    path('verify/<uuid:uuid>/', views.verify_certificate, name='verify_certificate'),
    path('admin/generate/', views.certificate_generate_admin_view, name='certificate_generate_admin'),
    path('create/<int:course_id>/', views.create_certificate, name='create_certificate'),
    path('edit/<int:certificate_id>/', views.edit_certificate, name='edit_certificate'),
    path('delete/<int:certificate_id>/', views.delete_certificate, name='delete_certificate'),
]