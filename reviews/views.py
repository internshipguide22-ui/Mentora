from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from courses.models import Course, Enrollment
from .models import Review

@login_required
def add_review(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    enrollment = Enrollment.objects.filter(student=request.user, course=course, completed=True).first()
    next_url = request.POST.get('next')
    
    if not enrollment:
        messages.error(request, "You must complete the course before reviewing.")
        if next_url:
            return redirect(next_url)
        return redirect('courses:course_detail', pk=course_id)

    existing_review = Review.objects.filter(course=course, student=request.user).first()
    if existing_review:
        messages.info(request, "You have already submitted a review for this course.")
        if next_url:
            return redirect(next_url)
        return redirect('courses:course_detail', pk=course_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        Review.objects.create(
            course=course,
            student=request.user,
            rating=rating,
            comment=comment,
        )
        messages.success(request, "Review submitted successfully!")
    
    if next_url:
        return redirect(next_url)
    return redirect('courses:course_detail', pk=course_id)
