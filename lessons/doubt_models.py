from django.db import models
from django.conf import settings
from courses.models import Lesson

class LessonDoubt(models.Model):
    """Model for student doubts/questions on lessons"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='doubts')
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
        # Mark doubt as resolved when instructor responds
        self.doubt.is_resolved = True
        self.doubt.save()
