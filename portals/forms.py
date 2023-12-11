from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db import transaction
from .models import User, Student, Teacher, Question, Answer
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class StudentSignUpForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput())
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    first_name = forms.CharField(widget=forms.TextInput())
    last_name = forms.CharField(widget=forms.TextInput())
    batch = forms.CharField(widget=forms.TextInput())
    roll_no = forms.CharField(widget=forms.TextInput())

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True
        if commit:
            user.save()
        student = Student.objects.create(user=user, first_name=self.cleaned_data.get('first_name'), last_name=self.cleaned_data.get('last_name'), batch=self.cleaned_data.get('batch'), roll_no=self.cleaned_data.get('roll_no'))
        return user
    

class TeacherSignUpForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput())
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    first_name = forms.CharField(widget=forms.TextInput())
    last_name = forms.CharField(widget=forms.TextInput())
    subject = forms.CharField(widget=forms.TextInput())

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_teacher = True
        if commit:
            user.save()
        teacher = Teacher.objects.create(user=user, first_name=self.cleaned_data.get('first_name'), last_name=self.cleaned_data.get('last_name'), subject=self.cleaned_data.get('subject'))
        return user
    


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())



