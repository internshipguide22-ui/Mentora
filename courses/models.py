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
    title = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=20, unique=True, blank=True, null=True, help_text="Unique course code (e.g., CS101)")
    description = models.TextField()
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

class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    description = models.TextField(blank=True, null=True)
    video_file = models.FileField(upload_to='lesson_videos/', blank=True, null=True, help_text="Upload video file (MP4, WebM, etc.)")
    video_url = models.URLField(blank=True, null=True, help_text="YouTube/Vimeo URL (optional reference)")
    attachment = models.FileField(upload_to='lesson_attachments/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.title} ({self.module.title})'
