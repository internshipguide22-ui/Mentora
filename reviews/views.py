from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from courses.models import Course, Enrollment
from .models import Review

@login_required
def add_review(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    enrollment = Enrollment.objects.filter(student=request.user, course=course, completed=True).first()
    
    if not enrollment:
        messages.error(request, "You must complete the course before reviewing.")
        return redirect('courses:course_detail', pk=course_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        Review.objects.update_or_create(
            course=course, student=request.user,
            defaults={'rating': rating, 'comment': comment}
        )
        messages.success(request, "Review submitted successfully!")
    
    return redirect('courses:course_detail', pk=course_id)
