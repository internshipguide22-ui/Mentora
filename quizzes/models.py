from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from courses.models import Module

class Quiz(models.Model):
    """
    Quiz model for storing quiz information.
    """
    title = models.CharField(max_length=200)
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='quizzes',
        null=True,   # TEMP (we will remove later)
        blank=True
    )

    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quizzes'
    )
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True, help_text="Instructions for students")
    start_date = models.DateTimeField(null=True, blank=True, help_text="When quiz becomes available")
    end_date = models.DateTimeField(null=True, blank=True, help_text="When quiz closes")
    time_limit_minutes = models.PositiveIntegerField(default=30, help_text="Duration in minutes")
    passing_score = models.PositiveIntegerField(default=70, help_text="Percentage to pass")
    max_attempts = models.PositiveIntegerField(default=3, help_text="Maximum attempts allowed")
    is_published = models.BooleanField(default=False)
    shuffle_questions = models.BooleanField(default=True)
    show_correct_answers = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_points(self):
        return sum(question.points for question in self.questions.all())

    @property
    def total_questions(self):
        return self.questions.count()
    
    def __str__(self):
        return f"{self.title} - {self.title}"

class Question(models.Model):
    """
    Question model for storing quiz questions.
    """
    MULTIPLE_CHOICE = 'multiple_choice'
    TRUE_FALSE = 'true_false'
    SHORT_ANSWER = 'short_answer'
    
    QUESTION_TYPE_CHOICES = [
        (MULTIPLE_CHOICE, 'Multiple Choice'),
        (TRUE_FALSE, 'True/False'),
        (SHORT_ANSWER, 'Short Answer'),
    ]
    
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    text = models.TextField()
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPE_CHOICES,
        default=MULTIPLE_CHOICE
    )
    correct_answer = models.TextField(blank=True, help_text="For short answer questions")
    feedback = models.TextField(blank=True, help_text="Feedback shown after answering")
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=1)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Question {self.order}: {self.text[:30]}..."

class Choice(models.Model):
    """
    Choice model for storing multiple choice options.
    """
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices'
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return self.text

class QuizAttempt(models.Model):
    """
    QuizAttempt model for tracking student quiz attempts.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_attempts'
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    attempt_number = models.PositiveIntegerField(default=1)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_taken_minutes = models.PositiveIntegerField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    passed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.student.username}'s attempt #{self.attempt_number} on {self.quiz.title}"

class QuizResponse(models.Model):
    """
    QuizResponse model for storing student responses to questions.
    """
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    selected_choice = models.ForeignKey(
        Choice,
        on_delete=models.CASCADE,
        related_name='responses',
        null=True,
        blank=True
    )
    text_response = models.TextField(blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    manually_graded = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Response to {self.question}"
