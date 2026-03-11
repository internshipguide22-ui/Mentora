from django.contrib import admin
from .models import VideoContent, TextContent, QuizContent, AssignmentContent

@admin.register(VideoContent)
class VideoContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'order')
    list_filter = ('lesson',)
    search_fields = ('title',)

@admin.register(TextContent)
class TextContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'order')
    list_filter = ('lesson',)
    search_fields = ('title',)

@admin.register(QuizContent)
class QuizContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'order')
    list_filter = ('lesson',)
    search_fields = ('title',)

@admin.register(AssignmentContent)
class AssignmentContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'order')
    list_filter = ('lesson',)
    search_fields = ('title',)
