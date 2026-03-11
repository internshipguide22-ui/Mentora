from django import forms
from .models import Certificate
from courses.models import Enrollment

class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['enrollment', 'grade']

class CertificateGenerationForm(forms.Form):
    enrollment = forms.ModelChoiceField(queryset=Enrollment.objects.all(), label="Enrollment")
    grade = forms.DecimalField(max_digits=5, decimal_places=2, required=False, label="Grade")