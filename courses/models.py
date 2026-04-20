import re

from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Course(models.Model):
    COURSE_ACCESS_CHOICES = [
        ('free', 'Free'),
        ('paid', 'Paid'),
    ]

    title = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=20, unique=True, blank=True, null=True, help_text="Unique course code (e.g., CS101)")
    description = models.TextField()
    course_access_type = models.CharField(
        max_length=10,
        choices=COURSE_ACCESS_CHOICES,
        default='free',
        help_text='Choose whether learners can access this course for free or as a paid course.'
    )
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses_taught'
    )
    thumbnail = models.ImageField(upload_to='course_thumbnails/', null=True, blank=True)
    syllabus = models.FileField(upload_to='syllabi/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class CourseNote(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to='course_notes/')
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_course_notes'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title or self.file.name


class VideoNote(models.Model):
    lesson = models.ForeignKey('Lesson', on_delete=models.CASCADE, related_name='video_notes')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_video_notes'
    )
    note_text = models.TextField()
    timestamp_seconds = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['timestamp_seconds', 'created_at']

    def __str__(self):
        return f'{self.lesson.title} - {self.formatted_timestamp}'

    @property
    def formatted_timestamp(self):
        hours, remainder = divmod(self.timestamp_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours:
            return f'{hours:02d}:{minutes:02d}:{seconds:02d}'
        return f'{minutes:02d}:{seconds:02d}'

class Enrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)
    progress = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f'{self.student.username} enrolled in {self.course.title}'
    
    def update_progress(self):
        from lessons.models import LessonCompletion
        total_lessons = sum(module.lessons.count() for module in self.course.modules.all())
        if total_lessons == 0:
            return
        completed_lessons = LessonCompletion.objects.filter(
            student=self.student,
            lesson__module__course=self.course
        ).count()
        self.progress = (completed_lessons / total_lessons) * 100
        if self.progress >= 100:
            self.completed = True
            if not self.completion_date:
                from django.utils import timezone
                self.completion_date = timezone.now()
            # Auto-generate certificate
            self._generate_certificate()
        self.save()
    
    def _generate_certificate(self):
        from certificates.models import Certificate
        if not Certificate.objects.filter(enrollment=self).exists():
            Certificate.objects.create(enrollment=self)

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.title} ({self.course.title})'

    def normalize_lesson_order(self):
        updates = []
        for index, lesson in enumerate(self.lessons.order_by('order', 'id'), start=1):
            if lesson.order != index:
                lesson.order = index
                updates.append(lesson)
        if updates:
            Lesson.objects.bulk_update(updates, ['order'])

class Lesson(models.Model):

    LANGUAGE_PYTHON = 'python'
    LANGUAGE_JAVASCRIPT = 'javascript'

    CODING_LANGUAGE_CHOICES = [
        (LANGUAGE_PYTHON, 'Python'),
        (LANGUAGE_JAVASCRIPT, 'JavaScript'),
    ]

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    description = models.TextField(blank=True, null=True)
    video_file = models.FileField(upload_to='lesson_videos/', blank=True, null=True, help_text="Upload video file (MP4, WebM, etc.)")
    video_url = models.URLField(blank=True, null=True, help_text="YouTube/Vimeo URL (optional reference)")
    attachment = models.FileField(upload_to='lesson_attachments/', blank=True, null=True)

    has_coding_lab = models.BooleanField(default=False)
    coding_language = models.CharField(max_length=20, choices=CODING_LANGUAGE_CHOICES, default=LANGUAGE_PYTHON, blank=True)
    coding_instructions = models.TextField(blank=True)
    starter_code = models.TextField(blank=True)
    stdin_placeholder = models.TextField(blank=True)

    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.title} ({self.module.title})'

    @property
    def display_title(self):
        return re.sub(r'^\s*Lesson\s+\d+\s*:\s*', '', self.title, flags=re.IGNORECASE)
