from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from .forms import LoginForm, RegisterForm, ProfileForm
from core.api import API
from core.utils import add_form_errors
from core.mixins import LoginRequiredMixin


class LoginView(FormView):
    """
    Vista de inicio de sesión.

    Esta vista muestra el formulario de login y envía las credenciales
    al servicio de autenticación externo (API). Si las credenciales
    son válidas, se almacena la sesión y el usuario es redirigido al dashboard.
    En caso contrario, se muestran errores en el formulario.

    Métodos principales:
    - form_valid(): procesa credenciales y maneja la autenticación.
    - form_invalid(): muestra mensajes de error cuando el formulario no es válido.
    """
    template_name = 'authentication/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('dashboard:home')

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return str(self.success_url)
    
    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        
        success, result = API.login(self.request, username, password)
        
        if success:
            messages.success(self.request, '¡Bienvenido de nuevo!')
            
            # PASAR TOKENS AL FRONTEND
            response = super().form_valid(form)
            
            # Guardar tokens en cookies para que JavaScript los acceda
            response.set_cookie('access', self.request.session.get('access'))
            response.set_cookie('refresh', self.request.session.get('refresh'))
            
            return response
            
        form.add_error(None, 'Credenciales inválidas. Inténtalo de nuevo.')
        return self.form_invalid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrige los errores.')
        return super().form_invalid(form)

class RegisterView(FormView):
    """
    Vista de registro de nuevos usuarios.

    Muestra un formulario para crear una cuenta y envía los datos al backend
    mediante API. Si el registro es exitoso, redirige al login.
    Si la API devuelve errores de validación, se agregan al formulario.

    Métodos principales:
    - form_valid(): envía los datos del usuario a la API.
    """
    template_name = 'authentication/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('authentication:login')
    
    def form_valid(self, form):
        user_data = {
            'username': form.cleaned_data['username'],
            'email': form.cleaned_data['email'],
            'password': form.cleaned_data['password'],
            'confirm_password': form.cleaned_data['confirm_password'],
            'first_name': form.cleaned_data['first_name'],
            'last_name': form.cleaned_data['last_name'],
        }
        
        success, result = API.register(self.request, user_data)
        
        if success:
            messages.success(self.request, '¡Cuenta creada exitosamente! Ahora puedes iniciar sesión.')
            return super().form_valid(form)

        add_form_errors(form, result)
        return self.form_invalid(form)

def logout_view(request):
    """
    Cierra la sesión del usuario.

    Elimina los datos de autenticación almacenados en la sesión mediante API
    y redirige al formulario de login.
    """
    API.logout(request)
    
    # LIMPIAR COOKIES DE TOKENS
    response = redirect('authentication:login')
    response.delete_cookie('access')
    response.delete_cookie('refresh')
    
    messages.success(request, '¡Sesión cerrada correctamente!')
    return response

class ProfileView(LoginRequiredMixin, TemplateView):
    """
    Vista de perfil del usuario autenticado.

    Obtiene la información del usuario y su perfil desde la API. Si la API no responde,
    utiliza los datos almacenados en la sesión como respaldo. Muestra información básica
    del usuario y detalles adicionales del perfil.

    Esta vista requiere que el usuario esté autenticado; de lo contrario,
    será redirigido al login.
    """
    template_name = 'authentication/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        success, result = API.get_user_profile(self.request)
        context['user_profile'] = result if success else self.request.session.get('user_data', {})

        context['user_data'] = self.request.session.get('user_data', {})

        success, profile = API.get_profile(self.request)
        context['profile_data'] = profile if success else self.request.session.get('profile_data', {})

        return context

class ProfileEditView(LoginRequiredMixin, FormView):
    """
    Vista para editar el perfil del usuario.

    Muestra un formulario con los datos actuales del perfil (bio, avatar, teléfono, ubicación)
    obtenidos desde la API o desde la sesión si la API falla. Al enviar el formulario,
    actualiza el perfil mediante API.

    Métodos principales:
    - get_form_kwargs(): carga los valores iniciales del formulario.
    - form_valid(): envía los datos actualizados a la API.
    """
    template_name = 'authentication/profile_edit.html'
    form_class = ProfileForm
    success_url = reverse_lazy('authentication:profile')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        success, profile = API.get_profile(self.request)
        data = profile if success else self.request.session.get('profile_data', {})

        kwargs['initial'] = {
            'bio': data.get('bio', ''),
            'avatar': data.get('avatar', ''),
            'phone': data.get('phone', ''),
            'location': data.get('location', ''),
        }

        return kwargs

    def form_valid(self, form):
        profile_data = {
            'bio': form.cleaned_data['bio'],
            'avatar': form.cleaned_data['avatar'],
            'phone': form.cleaned_data['phone'],
            'location': form.cleaned_data['location'],
        }

        success, result = API.update_profile(self.request, profile_data)

        if success:
            messages.success(self.request, '¡Perfil actualizado exitosamente!')
            return super().form_valid(form)

        messages.error(self.request, 'Error al actualizar el perfil.')
        print("DEBUG: Datos enviados:", profile_data)
        print("DEBUG: Respuesta de la API:", result)    
        add_form_errors(form, result)
        return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrige los errores.')
        return super().form_invalid(form)

