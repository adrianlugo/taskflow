from django.contrib import messages
from django.views.generic import TemplateView
from core.api import API
from core.mixins import LoginRequiredMixin

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener datos del usuario desde la sesión
        user_data = self.request.session.get('user_data', {})
        context['user'] = user_data
        
        # Obtener proyectos del usuario
        success, projects_result = API.get_projects(self.request)
        if success:
            context['projects'] = projects_result.get('results', [])
            context['projects_count'] = projects_result.get('count', 0)
        else:
            context['projects'] = []
            context['projects_count'] = 0
            messages.error(self.request, 'Error al cargar los proyectos.')
        
        # Obtener tareas del usuario
        success, tasks_result = API.get_tasks(self.request)
        if success:
            context['tasks'] = tasks_result.get('results', [])
            context['tasks_count'] = tasks_result.get('count', 0)
        else:
            context['tasks'] = []
            context['tasks_count'] = 0
            messages.error(self.request, 'Error al cargar las tareas.')
        
        return context
