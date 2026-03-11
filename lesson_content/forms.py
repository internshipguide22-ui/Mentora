from django import forms
from .models import VideoContent, TextContent, QuizContent, AssignmentContent

class VideoContentForm(forms.ModelForm):
    class Meta:
        model = VideoContent
        fields = ['title', 'video_url', 'order']

class TextContentForm(forms.ModelForm):
    class Meta:
        model = TextContent
        fields = ['title', 'text_content', 'order']

class QuizContentForm(forms.ModelForm):
    class Meta:
        model = QuizContent
        fields = ['title', 'quiz', 'order']

class AssignmentContentForm(forms.ModelForm):
    class Meta:
        model = AssignmentContent
        fields = ['title', 'description', 'assignment_details', 'order']