from django import forms
from courses.models import Lesson, Module

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'description', 'order', 'module']

    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course', None)
        super().__init__(*args, **kwargs)
        if course:
            self.fields['module'].queryset = Module.objects.filter(course=course).order_by('order')