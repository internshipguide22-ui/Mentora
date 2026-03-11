from django.contrib import admin
from django.utils.html import format_html
from .models import Quiz, Question, Choice, QuizAttempt

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3
    fields = ('text', 'is_correct')

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    fields = ('text', 'question_type', 'points', 'order')

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'instructor', 'question_count', 'is_published', 'created_at')
    list_filter = ('is_published', 'instructor', 'created_at')
    search_fields = ('title', 'description', 'lesson__title')
    date_hierarchy = 'created_at'
    inlines = [QuestionInline]
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'lesson', 'instructor')
        }),
        ('Settings', {
            'fields': ('time_limit_minutes', 'passing_score', 'max_attempts', 'is_published')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['publish_quizzes', 'unpublish_quizzes']
    
    def question_count(self, obj):
        count = obj.questions.count()
        color = 'green' if count > 0 else 'red'
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, count)
    question_count.short_description = 'Questions'
    
    def publish_quizzes(self, request, queryset):
        queryset.update(is_published=True)
    publish_quizzes.short_description = 'Publish selected quizzes'
    
    def unpublish_quizzes(self, request, queryset):
        queryset.update(is_published=False)
    unpublish_quizzes.short_description = 'Unpublish selected quizzes'

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text_preview', 'quiz', 'question_type', 'points', 'choice_count', 'order')
    list_filter = ('question_type', 'quiz')
    search_fields = ('text', 'quiz__title')
    inlines = [ChoiceInline]
    
    fieldsets = (
        ('Question Details', {
            'fields': ('quiz', 'text', 'question_type', 'points', 'order')
        }),
    )
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Question'
    
    def choice_count(self, obj):
        return obj.choices.count()
    choice_count.short_description = 'Choices'

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('text_preview', 'question_preview', 'is_correct_display')
    list_filter = ('is_correct', 'question__quiz')
    search_fields = ('text', 'question__text')
    
    def text_preview(self, obj):
        return obj.text[:40] + '...' if len(obj.text) > 40 else obj.text
    text_preview.short_description = 'Choice Text'
    
    def question_preview(self, obj):
        return obj.question.text[:40] + '...' if len(obj.question.text) > 40 else obj.question.text
    question_preview.short_description = 'Question'
    
    def is_correct_display(self, obj):
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            'green' if obj.is_correct else 'red',
            '✓ Correct' if obj.is_correct else '✗ Wrong'
        )
    is_correct_display.short_description = 'Correct Answer'

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'score_display', 'passed_display', 'started_at', 'completed_at')
    list_filter = ('quiz', 'started_at', 'completed_at')
    search_fields = ('student__username', 'quiz__title')
    date_hierarchy = 'started_at'
    readonly_fields = ('started_at', 'completed_at')
    
    fieldsets = (
        ('Attempt Info', {
            'fields': ('student', 'quiz')
        }),
        ('Results', {
            'fields': ('score', 'passed')
        }),
        ('Timestamps', {
            'fields': ('started_at', 'completed_at')
        }),
    )
    
    def score_display(self, obj):
        if obj.score is not None:
            color = 'green' if obj.score >= 70 else 'orange' if obj.score >= 50 else 'red'
            return format_html('<span style="color: {}; font-weight: bold;">{:.1f}%</span>', color, obj.score)
        return '-'
    score_display.short_description = 'Score'
    
    def passed_display(self, obj):
        if obj.passed is not None:
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                'green' if obj.passed else 'red',
                '✓ Passed' if obj.passed else '✗ Failed'
            )
        return '-'
    passed_display.short_description = 'Status'
