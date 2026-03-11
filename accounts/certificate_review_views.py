from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from accounts.decorators import admin_required
from certificates.models import Certificate
from reviews.models import Review

@login_required
@admin_required
def manage_certificates(request):
    search = request.GET.get('search', '')
    certificates = Certificate.objects.select_related('enrollment__student', 'enrollment__course').all()
    
    if search:
        certificates = certificates.filter(
            Q(enrollment__student__username__icontains=search) |
            Q(enrollment__course__title__icontains=search)
        )
    
    return render(request, 'management/certificates.html', {'certificates': certificates, 'search': search})

@login_required
@admin_required
def revoke_certificate(request, certificate_id):
    certificate = get_object_or_404(Certificate, id=certificate_id)
    
    if request.method == 'POST':
        certificate.delete()
        messages.success(request, 'Certificate revoked successfully!')
        return redirect('manage_certificates')
    
    return render(request, 'management/revoke_certificate.html', {'certificate': certificate})

@login_required
@admin_required
def regenerate_certificate(request, certificate_id):
    certificate = get_object_or_404(Certificate, id=certificate_id)
    
    from certificates.utils import generate_certificate_pdf
    generate_certificate_pdf(certificate)
    
    messages.success(request, 'Certificate regenerated successfully!')
    return redirect('manage_certificates')

@login_required
@admin_required
def manage_reviews(request):
    search = request.GET.get('search', '')
    rating = request.GET.get('rating', '')
    
    reviews = Review.objects.select_related('student', 'course').all()
    
    if search:
        reviews = reviews.filter(
            Q(student__username__icontains=search) |
            Q(course__title__icontains=search) |
            Q(comment__icontains=search)
        )
    
    if rating:
        reviews = reviews.filter(rating=rating)
    
    return render(request, 'management/reviews.html', {'reviews': reviews, 'search': search, 'rating': rating})

@login_required
@admin_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Review deleted successfully!')
        return redirect('manage_reviews')
    
    return render(request, 'management/delete_review.html', {'review': review})
