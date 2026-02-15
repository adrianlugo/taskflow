from django.contrib import messages
from django.views.generic import TemplateView
from core.api import API
from core.mixins import LoginRequiredMixin
from core.utils import handle_api_auth_error


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'

    def get(self, request, *args, **kwargs):
        context = {}

        # Obtener datos del usuario desde la sesion
        context['user'] = request.session.get('user_data', {})

        # Obtener proyectos del usuario
        success, projects_result = API.get_projects(request)
        if success:
            context['projects'] = projects_result.get('results', [])
            context['projects_count'] = projects_result.get('count', 0)
        else:
            redirect_response = handle_api_auth_error(request, projects_result)
            if redirect_response:
                return redirect_response
            context['projects'] = []
            context['projects_count'] = 0
            messages.error(request, 'Error al cargar los proyectos.')

        # Obtener tareas del usuario
        success, tasks_result = API.get_tasks(request)
        if success:
            context['tasks'] = tasks_result.get('results', [])
            context['tasks_count'] = tasks_result.get('count', 0)
        else:
            redirect_response = handle_api_auth_error(request, tasks_result)
            if redirect_response:
                return redirect_response
            context['tasks'] = []
            context['tasks_count'] = 0
            messages.error(request, 'Error al cargar las tareas.')

        return self.render_to_response(context)
