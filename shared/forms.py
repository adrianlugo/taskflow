"""
Forms Django para Web
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Project, Task, Comment


class CustomUserCreationForm(UserCreationForm):
    """Formulario de registro personalizado"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    """Formulario de perfil"""
    class Meta:
        model = Profile
        fields = ('bio', 'phone', 'location')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }


class ProjectForm(forms.ModelForm):
    """Formulario de proyecto"""
    class Meta:
        model = Project
        fields = ('name', 'description', 'status')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class TaskForm(forms.ModelForm):
    """Formulario de tarea"""
    class Meta:
        model = Task
        fields = ('title', 'description', 'project', 'assigned_to', 'priority', 'due_date')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class CommentForm(forms.ModelForm):
    """Formulario de comentario"""
    class Meta:
        model = Comment
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Añade un comentario...'}),
        }
