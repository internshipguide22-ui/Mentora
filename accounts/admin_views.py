from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Avg
from accounts.models import User
from courses.models import Course, Enrollment
from quizzes.models import Quiz, QuizAttempt
from certificates.models import Certificate

@staff_member_required
def admin_analytics(request):
    context = {
        'total_users': User.objects.count(),
        'total_students': User.objects.filter(user_type='student').count(),
        'total_instructors': User.objects.filter(user_type='instructor').count(),
        'total_admins': User.objects.filter(user_type='admin').count(),
        'active_users': User.objects.filter(is_active=True).count(),
        
        'total_courses': Course.objects.count(),
        'total_enrollments': Enrollment.objects.count(),
        'active_enrollments': Enrollment.objects.filter(is_active=True).count(),
        'completed_courses': Enrollment.objects.filter(completed=True).count(),
        
        'total_quizzes': Quiz.objects.count(),
        'total_quiz_attempts': QuizAttempt.objects.count(),
        'completed_quizzes': QuizAttempt.objects.filter(completed_at__isnull=False).count(),
        
        'total_certificates': Certificate.objects.count(),
        
        'recent_users': User.objects.order_by('-date_joined')[:5],
        'recent_enrollments': Enrollment.objects.select_related('student', 'course').order_by('-enrollment_date')[:5],
        'popular_courses': Course.objects.annotate(enrollment_count=Count('enrollments')).order_by('-enrollment_count')[:5],
    }
    return render(request, 'admin/analytics.html', context)
