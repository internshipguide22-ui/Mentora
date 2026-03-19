from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse
from django.contrib import messages
from .models import Certificate
from courses.models import Enrollment, Course
from .utils import generate_certificate
import uuid
from .forms import CertificateGenerationForm, CertificateForm

@login_required
def generate_certificate_view(request, enrollment_id):
    """Generate a certificate for a completed course"""
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=request.user, completed=True)
    
    # Get or create certificate
    certificate, created = Certificate.objects.get_or_create(
        enrollment=enrollment,
        defaults={'uuid': uuid.uuid4()}
    )
    
    # Generate certificate PDF if it doesn't exist
    if not certificate.file or not certificate.file.name:
        certificate = generate_certificate(certificate)
        certificate.save()
        messages.success(request, "Certificate generated successfully!")
    
    return redirect('certificates:view_certificate', certificate_id=certificate.id)

@login_required
def view_certificate(request, certificate_id):
    """View a generated certificate"""
    certificate = get_object_or_404(Certificate, id=certificate_id, enrollment__student=request.user)
    return render(request, 'certificates/view_certificate.html', {'certificate': certificate})

def verify_certificate(request, uuid):
    """Public verification of certificate authenticity"""
    certificate = get_object_or_404(Certificate, uuid=uuid)
    return render(request, 'certificates/verify_certificate.html', {'certificate': certificate})

@login_required
def certificate_generate_admin_view(request):
    if request.method == 'POST':
        form = CertificateGenerationForm(request.POST)
        if form.is_valid():
            enrollment = form.cleaned_data['enrollment']
            grade = form.cleaned_data['grade']
            
            certificate, created = Certificate.objects.get_or_create(
                enrollment=enrollment,
                defaults={'uuid': uuid.uuid4(), 'grade': grade}
            )
            
            if created:
                certificate = generate_certificate(certificate)
                messages.success(request, "Certificate generated successfully!")
            else:
                messages.info(request, "Certificate already exists for this enrollment.")
            
            return redirect('admin:certificates_certificate_changelist') # Redirect to admin list view
    else:
        form = CertificateGenerationForm()
    
    return render(request, 'admin/certificate_generate_form.html', {'form': form})

@login_required
def create_certificate(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    if request.method == 'POST':
        form = CertificateForm(request.POST)
        if form.is_valid():
            certificate = form.save(commit=False)
            # Assuming the form has a field for enrollment, or we select one here
            # For now, let's assume we'll select an enrollment from the course
            # This part needs further refinement based on how we want to select the student/enrollment
            # For demonstration, let's just create a dummy certificate for the first enrollment in the course
            enrollment = Enrollment.objects.filter(course=course).first()
            if enrollment:
                certificate.enrollment = enrollment
                certificate.uuid = uuid.uuid4()
                certificate.save()
                messages.success(request, "Certificate created successfully!")
                return redirect('certificates:view_certificate', certificate_id=certificate.id)
            else:
                messages.error(request, "No enrollments found for this course to create a certificate.")
    else:
        form = CertificateForm()
    return render(request, 'certificates/certificate_form.html', {'form': form, 'course': course})

@login_required
def edit_certificate(request, certificate_id):
    certificate = get_object_or_404(Certificate, id=certificate_id)
    if request.method == 'POST':
        form = CertificateForm(request.POST, instance=certificate)
        if form.is_valid():
            form.save()
            messages.success(request, "Certificate updated successfully!")
            return redirect('certificates:view_certificate', certificate_id=certificate.id)
    else:
        form = CertificateForm(instance=certificate)
    return render(request, 'certificates/certificate_form.html', {'form': form, 'certificate': certificate})

@login_required
def delete_certificate(request, certificate_id):
    certificate = get_object_or_404(Certificate, id=certificate_id)
    if request.method == 'POST':
        certificate.delete()
        messages.success(request, "Certificate deleted successfully!")
        return redirect('home') # Redirect to home page after deletion
    return render(request, 'certificates/certificate_confirm_delete.html', {'certificate': certificate})
