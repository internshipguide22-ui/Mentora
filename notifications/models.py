from django.db import models
from django.conf import settings
from django.utils import timezone

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('course_update', 'Course Update'),
        ('assignment', 'Assignment'),
        ('quiz', 'Quiz'),
        ('enrollment', 'Enrollment'),
        ('completion', 'Course Completion'),
        ('announcement', 'Announcement'),
        ('feedback', 'Feedback'),
        ('reminder', 'Reminder'),
        ('system', 'System Notification'),
    )
    
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.URLField(blank=True, null=True)  # Optional link to related content
    is_read = models.BooleanField(default=False)
    is_email_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # For scheduling notifications
    scheduled_for = models.DateTimeField(null=True, blank=True)
    is_scheduled = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Notification for {self.recipient.username}: {self.message[:50]}...'