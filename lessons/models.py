from django.db import models
from django.conf import settings


class LessonDoubt(models.Model):
    """Model for student doubts/questions on lessons"""
    lesson = models.ForeignKey('courses.Lesson', on_delete=models.CASCADE, related_name='doubts')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lesson_doubts')
    question = models.TextField(help_text="Student's question or doubt")
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.lesson.title[:30]}"

class DoubtResponse(models.Model):
    """Model for instructor responses to doubts"""
    doubt = models.ForeignKey(LessonDoubt, on_delete=models.CASCADE, related_name='responses')
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doubt_responses')
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Response by {self.instructor.username}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.doubt.is_resolved = True
        self.doubt.save()

class LessonCompletion(models.Model):
    """
    LessonCompletion model for tracking student progress through lessons.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='completed_lessons'
    )
    lesson = models.ForeignKey(
        'courses.Lesson', # Use Lesson from courses.models
        on_delete=models.CASCADE,
        related_name='completions'
    )
    completed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'lesson']
        
    def __str__(self):
        return f"{self.student.username} completed {self.lesson.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_course_progress()

    def update_course_progress(self):
        from courses.models import Enrollment, Lesson
        course = self.lesson.module.course
        enrollment = Enrollment.objects.filter(
            student=self.student,
            course=course
        ).first()

        if enrollment:
            total_lessons = Lesson.objects.filter(module__course=course).count()
            completed_lessons = self.student.completed_lessons.filter(
                lesson__module__course=course
            ).count()

            if total_lessons > 0:
                progress = (completed_lessons / total_lessons) * 100
                enrollment.progress = progress
                if progress >= 100:
                    enrollment.completed = True
                    if not enrollment.completion_date:
                        from django.utils import timezone
                        enrollment.completion_date = timezone.now()
                enrollment.save()
