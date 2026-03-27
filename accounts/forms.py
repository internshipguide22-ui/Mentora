from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import User

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    user_type = forms.ChoiceField(
        choices=[('student', 'Student'), ('instructor', 'Instructor')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone = forms.CharField(required=False)
    profile_picture = forms.ImageField(required=False)
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'user_type', 
                 'phone', 'date_of_birth', 'profile_picture')
        
    def __init__(self, *args, **kwargs):
        self.show_user_type = kwargs.pop('show_user_type', False)
        super().__init__(*args, **kwargs)
        if not self.show_user_type:
            self.fields.pop('user_type', None)
        for field in self.fields:
            if not isinstance(self.fields[field].widget, (forms.CheckboxInput, forms.RadioSelect)):
                self.fields[field].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.show_user_type:
            user.user_type = self.cleaned_data.get('user_type', 'student')
        else:
            user.user_type = 'student'
        if commit:
            user.save()
            self.save_m2m()
        return user

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already in use.")
        return email

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'profile_picture',
                 'bio', 'date_of_birth', 'website', 'address',
                 'learning_style', 'preferred_language', 'daily_study_goal')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'learning_style': forms.Select(attrs={'class': 'form-select'}),
            'daily_study_goal': forms.NumberInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if not isinstance(self.fields[field].widget, (forms.CheckboxInput, forms.RadioSelect)):
                self.fields[field].widget.attrs.update({'class': 'form-control'})

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_messages['invalid_login'] = 'Invalid username or password. Please try again.'

class InstructorProfileForm(UserProfileForm):
    class Meta(UserProfileForm.Meta):
        fields = ('first_name', 'last_name', 'email', 'phone', 'profile_picture',
                 'bio', 'website', 'address')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if not isinstance(self.fields[field].widget, (forms.CheckboxInput, forms.RadioSelect)):
                self.fields[field].widget.attrs.update({'class': 'form-control'})

class AdminProfileForm(UserProfileForm):
    class Meta(UserProfileForm.Meta):
        fields = ('first_name', 'last_name', 'email', 'phone', 'profile_picture',
                 'bio', 'website', 'address')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if not isinstance(self.fields[field].widget, (forms.CheckboxInput, forms.RadioSelect)):
                self.fields[field].widget.attrs.update({'class': 'form-control'})
