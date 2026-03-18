from django.db import models
from courses.models import Module


class VideoContent(models.Model):
    lesson = models.ForeignKey('courses.Lesson', on_delete=models.CASCADE, related_name='video_contents')
    title = models.CharField(max_length=200)
    video_url = models.URLField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'Video: {self.title} (Lesson: {self.lesson.title})'

class TextContent(models.Model):
    lesson = models.ForeignKey('courses.Lesson', on_delete=models.CASCADE, related_name='text_contents')
    title = models.CharField(max_length=200)
    text_content = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'Text: {self.title} (Lesson: {self.lesson.title})'

from quizzes.models import Quiz

class QuizContent(models.Model):
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='quiz_contents',
        null=True,
        blank=True
    )
    title = models.CharField(max_length=200)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='lesson_content_quizzes')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'Quiz: {self.title} (Module: {self.module.title})'

class AssignmentContent(models.Model):
    lesson = models.ForeignKey('courses.Lesson', on_delete=models.CASCADE, related_name='assignment_contents')
    title = models.CharField(max_length=200)
    description = models.TextField()
    # In a real application, this would link to an Assignment model
    # For now, we'll just have a placeholder
    assignment_details = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'Assignment: {self.title} (Lesson: {self.lesson.title})'
