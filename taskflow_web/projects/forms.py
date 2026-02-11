from django import forms

class ProjectForm(forms.Form):
    name = forms.CharField(
        label='Nombre del Proyecto',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa el nombre del proyecto',
            'autofocus': True
        })
    )
    description = forms.CharField(
        label='Descripción',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Describe el proyecto',
            'rows': 3
        })
    )
    status = forms.ChoiceField(
        label='Estado',
        choices=[
            ('activo', 'Activo'),
            ('completado', 'Completado'),
            ('archivado', 'Archivado'),
            ('en_pausa', 'En Pausa'),
        ],
        initial='activo',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    start_date = forms.DateField(
        label='Fecha de Inicio',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    end_date = forms.DateField(
        label='Fecha de Fin',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
