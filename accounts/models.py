from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('admin', 'Admin'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Learning preferences for students
    LEARNING_STYLE_CHOICES = (
        ('visual', 'Visual'),
        ('auditory', 'Auditory'),
        ('reading', 'Reading/Writing'),
        ('kinesthetic', 'Kinesthetic'),
    )
    learning_style = models.CharField(max_length=20, choices=LEARNING_STYLE_CHOICES, null=True, blank=True)
    preferred_language = models.CharField(max_length=50, blank=True, null=True)
    daily_study_goal = models.PositiveIntegerField(default=30, validators=[MinValueValidator(15), MaxValueValidator(480)])  # in minutes

    @property
    def is_student(self):
        return self.user_type == 'student'

    @property
    def is_instructor(self):
        return self.user_type == 'instructor'

    @property
    def is_admin(self):
        return self.is_superuser or self.user_type == 'admin'
    
    def save(self, *args, **kwargs):
        if self.user_type == 'admin' or self.is_superuser:
            self.is_staff = True
            self.is_superuser = True
        super().save(*args, **kwargs)


class RegistrationRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    email_sent = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.name} - {self.email} ({self.status})"
