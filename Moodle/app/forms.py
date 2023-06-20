from django import forms
from .models import User, Subject, Enrollment, Role
from django.contrib.auth.forms import AuthenticationForm
from django.core.validators import MaxValueValidator, MinValueValidator

class SubjectForm(forms.ModelForm):
    ects_points = forms.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    sem_redovni = forms.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    sem_izvanredni = forms.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])

    class Meta:
        model = Subject
        fields = ('name', 'code', 'program', 'ects_points', 'sem_redovni', 'sem_izvanredni', 'izborni')


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class UserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password', 'role')
        widgets = {
            'password': forms.PasswordInput()
        }

class StudentForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = User
        fields = ('username', 'password', 'status')

class MentorForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = User
        fields = ('username', 'password')


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'subject', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = User.objects.filter(role=Role.objects.get(name='STUDENT'))
        self.fields['subject'].queryset = Subject.objects.all()

class EnrollmentFormStudent(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'subject', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject'].queryset = Subject.objects.all()

