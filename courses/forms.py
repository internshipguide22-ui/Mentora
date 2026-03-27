from django import forms
from .models import Course, Lesson, CourseNote
from accounts.models import User

class CourseForm(forms.ModelForm):
    instructor = forms.ModelChoiceField(
        queryset=User.objects.filter(user_type='instructor'),
        required=True,
        help_text='Select the instructor for this course'
    )
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if code:
            code = code.upper()
            if self.instance.pk:
                if Course.objects.exclude(pk=self.instance.pk).filter(code=code).exists():
                    raise forms.ValidationError('A course with this code already exists.')
            else:
                if Course.objects.filter(code=code).exists():
                    raise forms.ValidationError('A course with this code already exists.')
        return code
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if self.instance.pk:
            if Course.objects.exclude(pk=self.instance.pk).filter(title=title).exists():
                raise forms.ValidationError('A course with this title already exists.')
        else:
            if Course.objects.filter(title=title).exists():
                raise forms.ValidationError('A course with this title already exists.')
        return title
    
    class Meta:
        model = Course
        fields = ['code', 'title', 'description', 'instructor', 'category', 'thumbnail', 'syllabus']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'description', 'content', 'video_file', 'video_url', 'attachment', 'module', 'order']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'video_file': 'Upload video file (main content)',
            'video_url': 'YouTube/Vimeo URL (optional reference only)',
            'attachment': 'Upload PDF, documents, images, or other files',
        }
    
    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course', None)
        super().__init__(*args, **kwargs)
        if course:
            from .models import Module
            self.fields['module'].queryset = Module.objects.filter(course=course)
            self.fields['module'].required = True


class CourseNoteForm(forms.ModelForm):
    class Meta:
        model = CourseNote
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Optional title for this note',
                'class': 'form-control'
            }),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
