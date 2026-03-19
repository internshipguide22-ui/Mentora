from django import forms
from .models import Quiz, Question, Choice

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'module', 'time_limit_minutes', 'passing_score', 'max_attempts', 'is_published']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        instructor = kwargs.pop('instructor', None)
        super().__init__(*args, **kwargs)
        if instructor:
            from courses.models import Module
            self.fields['module'].queryset = Module.objects.filter(course__instructor=instructor)

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'correct_answer', 'feedback', 'points']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
            'correct_answer': forms.TextInput(attrs={'placeholder': 'For True/False: enter "true" or "false"'}),
            'feedback': forms.Textarea(attrs={'rows': 2}),
        }
        help_texts = {
            'correct_answer': 'Required for True/False and Short Answer questions',
            'feedback': 'Optional feedback shown after answering',
        }

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct']
