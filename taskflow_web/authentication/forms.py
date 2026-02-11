from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(
        label='Nombre de usuario',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu nombre de usuario',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu contraseña'
        })
    )

class RegisterForm(forms.Form):
    username = forms.CharField(
        label='Nombre de usuario',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Elige un nombre de usuario',
            'autofocus': True
        })
    )
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    first_name = forms.CharField(
        label='Nombre',
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu nombre'
        })
    )
    last_name = forms.CharField(
        label='Apellido',
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu apellido'
        })
    )
    password = forms.CharField(
        label='Contraseña',
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mínimo 8 caracteres'
        })
    )
    confirm_password = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repite tu contraseña'
        })
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 3:
            raise forms.ValidationError('El nombre de usuario debe tener al menos 3 caracteres.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        return email.lower()
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError('Las contraseñas no coinciden.')
        
        return cleaned_data

class ProfileForm(forms.Form):
    bio = forms.CharField(
        label='Biografía',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Cuéntanos sobre ti...',
            'rows': 4
        })
    )
    avatar = forms.URLField(
        label='Avatar (URL)',
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://ejemplo.com/avatar.jpg'
        })
    )
    phone = forms.CharField(
        label='Teléfono',
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+52 1 234 567 890'
        })
    )
    location = forms.CharField(
        label='Ubicación',
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ciudad, País'
        })
    )
    
    def __init__(self, *args, **kwargs):
        initial_data = kwargs.pop('initial', {})
        super().__init__(*args, **kwargs)
        
        # Establecer valores iniciales desde initial_data
        if initial_data:
            self.fields['bio'].initial = initial_data.get('bio', '')
            self.fields['avatar'].initial = initial_data.get('avatar', '')
            self.fields['phone'].initial = initial_data.get('phone', '')
            self.fields['location'].initial = initial_data.get('location', '')
