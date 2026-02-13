from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from core.api import API
from core.mixins import LoginRequiredMixin
from core.utils import add_form_errors
from .forms import ProjectForm

class ProjectListView(LoginRequiredMixin, TemplateView):
    template_name = 'projects/list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener proyectos del usuario
        success, projects_result = API.get_projects(self.request)
        if success:
            context['projects'] = projects_result.get('results', [])
            context['projects_count'] = projects_result.get('count', 0)
        else:
            context['projects'] = []
            context['projects_count'] = 0
            messages.error(self.request, 'Error al cargar los proyectos.')
        
        return context


class ProjectDeleteView(LoginRequiredMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        project_id = kwargs.get('pk')
        success, result = API.delete_project(request, project_id)
        if success:
            messages.success(request, 'Proyecto eliminado correctamente.')
        else:
            msg = 'No se pudo eliminar el proyecto.'
            if isinstance(result, dict):
                msg = result.get('detail') or result.get('error') or msg
            messages.error(request, msg)

        return redirect('projects:list')

class ProjectCreateView(LoginRequiredMixin, FormView):
    template_name = 'projects/create.html'
    form_class = ProjectForm
    success_url = reverse_lazy('projects:list')
    
    def form_valid(self, form):
        project_data = {
            'name': form.cleaned_data['name'],
            'description': form.cleaned_data['description'],
            'status': form.cleaned_data['status'],
            'member_ids': []  # Por ahora sin miembros
        }
        
        # Manejar fechas solo si tienen valor
        if form.cleaned_data['start_date']:
            project_data['start_date'] = form.cleaned_data['start_date'].isoformat()
        if form.cleaned_data['end_date']:
            project_data['end_date'] = form.cleaned_data['end_date'].isoformat()
        
        success, result = API.create_project(self.request, project_data)
        
        if success:
            messages.success(self.request, '¡Proyecto creado exitosamente!')
            # Redirigir a la lista de proyectos
            return super().form_valid(form)
        
        add_form_errors(form, result)
        return self.form_invalid(form)
    
    def form_invalid(self, form):
        # No agregar mensaje general, el template ya muestra los errores por campo
        return super().form_invalid(form)

class ProjectUpdateView(LoginRequiredMixin, FormView):
    template_name = 'projects/update.html'
    form_class = ProjectForm
    success_url = reverse_lazy('projects:list')
    
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        project_id = kwargs.get('pk')
        success, project = API.get_project(request, project_id)
        if not success:
            messages.error(request, 'Error al cargar el proyecto.')
            return redirect('projects:list')
        # Guardar el proyecto para usarlo después
        self.project = project
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Asegurarnos de que self.project exista
        if not hasattr(self, 'project'):
            project_id = self.kwargs.get('pk')
            success, project = API.get_project(self.request, project_id)
            if not success:
                messages.error(self.request, 'Error al cargar el proyecto.')
                # NO retornes redirect aquí, solo retorna context vacío
                return context
            self.project = project
        
        context['project'] = self.project
        
        # Pre-cargar el formulario con datos actuales
        if 'form' not in kwargs:
            form = self.get_form()
            initial_data = {
                'name': self.project.get('name'),
                'description': self.project.get('description'),
                'status': self.project.get('status'),
                'start_date': self.project.get('start_date'),
                'end_date': self.project.get('end_date'),
            }
            form.initial = initial_data
            context['form'] = form
        
        return context
    
    def form_valid(self, form):
        project_id = self.kwargs.get('pk')
        
        # Asegurarnos de que self.project exista
        if not hasattr(self, 'project'):
            success, project = API.get_project(self.request, project_id)
            if not success:
                messages.error(self.request, 'Error al cargar el proyecto.')
                return redirect('projects:list')
            self.project = project
        
        project_data = {
            'name': form.cleaned_data['name'],
            'description': form.cleaned_data['description'],
            'status': form.cleaned_data['status'],
        }
        
        if form.cleaned_data['start_date']:
            project_data['start_date'] = form.cleaned_data['start_date'].isoformat()
        if form.cleaned_data['end_date']:
            project_data['end_date'] = form.cleaned_data['end_date'].isoformat()
        
        success, result = API.update_project(self.request, project_id, project_data)
        
        if success:
            messages.success(self.request, '¡Proyecto actualizado exitosamente!')
            return super().form_valid(form)
        
        add_form_errors(form, result)
        return self.form_invalid(form)
    
    def form_invalid(self, form):
        return super().form_invalid(form)

class AddProjectMemberView(LoginRequiredMixin, TemplateView):
    def get(self, request, project_id): 
        """ Devuelve la lista de usuarios disponibles para agregar al proyecto """ 
        success, result = API.get_users(request)
        if not success:
            return JsonResponse({'success': False, 'error': result.get('error', 'Error cargando usuarios')}) 
        return JsonResponse({'success': True, 'users': result})
    
    def post(self, request, project_id): 
        """ Agrega un miembro al proyecto """ 
        user_id = request.POST.get('user_id')  
        if not user_id: 
            return JsonResponse({'success': False, 'error': 'user_id requerido'}, status=400)
        
        # Convertir a entero y enviar a la API
        success, result = API.add_project_member(request, project_id, {'user_id': int(user_id)}) 
        if success: 
            messages.success(request, 'Miembro agregado exitosamente')
            return JsonResponse({'success': True, 'message': 'Miembro agregado exitosamente'})
        else: 
            error_msg = result.get('error', 'Error al agregar miembro')
            messages.error(request, f'Error: {error_msg}')
            return JsonResponse({'success': False, 'error': error_msg}, status=400)


class RemoveProjectMemberView(LoginRequiredMixin, TemplateView):
    def post(self, request, project_id, user_id):
        success, result = API.remove_project_member(request, project_id, user_id)

        if success:
            messages.success(request, 'Miembro eliminado exitosamente')
            return JsonResponse({'success': True, 'message': 'Miembro eliminado exitosamente'})
        else:
            error_msg = result.get('error', 'Error al eliminar miembro')
            messages.error(request, f'Error: {error_msg}')
            return JsonResponse({'success': False, 'error': error_msg}, status=400)


class ProjectDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'projects/detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = kwargs.get('pk')

        success, project = API.get_project(self.request, project_id)
        if success:
            context['project'] = project
        else:
            messages.error(self.request, 'Error al cargar el proyecto.')
        
        # Agregar información del usuario
        user_data = self.request.session.get('user_data', {})
        context['user'] = user_data
        
        return context
