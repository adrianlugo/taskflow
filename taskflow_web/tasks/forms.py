from django import forms

class TaskForm(forms.Form):
    title = forms.CharField(
        label='Título de la Tarea',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa el título de la tarea',
            'autofocus': True
        })
    )
    description = forms.CharField(
        label='Descripción',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Describe la tarea',
            'rows': 3
        })
    )
    project = forms.ChoiceField(
        label='Proyecto',
        choices=[],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    assigned_to = forms.ChoiceField(
        label='Asignar a',
        required=False,
        choices=[],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    status = forms.ChoiceField(
        label='Estado',
        choices=[
            ('por_hacer', 'Por Hacer'),
            ('en_progreso', 'En Progreso'),
            ('revision', 'Revisión'),
            ('completado', 'Completado'),
        ],
        initial='por_hacer',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    priority = forms.ChoiceField(
        label='Prioridad',
        choices=[
            ('baja', 'Baja'),
            ('media', 'Media'),
            ('alta', 'Alta'),
            ('urgente', 'Urgente'),
        ],
        initial='media',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    due_date = forms.DateTimeField(
        label='Fecha de Vencimiento',
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )
    
    def __init__(self, *args, **kwargs):
        user_projects = kwargs.pop('user_projects', [])
        users = kwargs.pop('users', [])
        super().__init__(*args, **kwargs)
        
        # Actualizar choices de proyectos
        project_choices = [(str(p['id']), p['name']) for p in user_projects]
        self.fields['project'].choices = project_choices
        
        # Actualizar choices de usuarios
        user_choices = [('', 'Sin asignar')] + [(str(u['id']), u['username']) for u in users]
        self.fields['assigned_to'].choices = user_choices
