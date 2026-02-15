from django.contrib import messages
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from core.api import API
from .forms import TaskForm
from core.mixins import LoginRequiredMixin
from core.utils import add_form_errors, handle_api_auth_error

STATUS_ORDER = ['por_hacer', 'en_progreso', 'revision', 'completado']
STATUS_LABELS = {
    'por_hacer': 'Por Hacer',
    'en_progreso': 'En Progreso',
    'revision': 'Revision',
    'completado': 'Completado',
}


def _get_next_status(current_status):
    if current_status in STATUS_ORDER:
        index = STATUS_ORDER.index(current_status)
        return STATUS_ORDER[(index + 1) % len(STATUS_ORDER)]
    return STATUS_ORDER[0]

class TaskListView(LoginRequiredMixin, TemplateView):
    template_name = 'tasks/list.html'

    def get(self, request, *args, **kwargs):
        context = {}

        # Obtener proyectos para el filtro
        success, projects_result = API.get_projects(request)
        if success:
            context['projects'] = projects_result.get('results', [])
        else:
            redirect_response = handle_api_auth_error(request, projects_result)
            if redirect_response:
                return redirect_response
            context['projects'] = []

        # Obtener tareas (filtradas por proyecto si se especifica)
        project_id = request.GET.get('project')
        success, tasks_result = API.get_tasks(request, project_id)
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

class TaskCreateView(LoginRequiredMixin, FormView):
    template_name = 'tasks/create.html'
    form_class = TaskForm
    success_url = reverse_lazy('tasks:list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        
        # Obtener proyectos del usuario para el formulario
        success, projects_result = API.get_projects(self.request)
        if success:
            kwargs['user_projects'] = projects_result.get('results', [])
        else:
            kwargs['user_projects'] = []
        
        # Obtener usuarios (por ahora usamos los miembros de proyectos)
        kwargs['users'] = []
        
        return kwargs
    
    def form_valid(self, form):
        project_id = int(form.cleaned_data['project']) if form.cleaned_data['project'] else None
        assigned_to_id = int(form.cleaned_data['assigned_to']) if form.cleaned_data['assigned_to'] else None
        task_data = {
            'title': form.cleaned_data['title'],
            'description': form.cleaned_data['description'],
            'project': project_id,
            'assigned_to_id': assigned_to_id,
            'status': form.cleaned_data['status'],
            'priority': form.cleaned_data['priority'],
            'due_date': form.cleaned_data['due_date'].isoformat() if form.cleaned_data['due_date'] else None,
        }
        
        success, result = API.create_task(self.request, task_data)
        
        if success:
            messages.success(self.request, '¡Tarea creada exitosamente!')
            return self.form_invalid(form)
        
        add_form_errors(form, result)
        return self.form_invalid(form)
    
    def form_invalid(self, form):
        return super().form_invalid(form)

class TaskDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'tasks/detail.html'

    def get(self, request, *args, **kwargs):
        context = {}
        task_id = kwargs.get('pk')

        success, task = API.get_task(request, task_id)
        if success:
            context['task'] = task
            current_status = task.get('status')
            next_status = _get_next_status(current_status)
            context['next_status'] = next_status
            context['next_status_label'] = STATUS_LABELS.get(next_status, next_status)
        else:
            redirect_response = handle_api_auth_error(request, task)
            if redirect_response:
                return redirect_response
            messages.error(request, 'Error al cargar la tarea.')

        return self.render_to_response(context)

class TaskUpdateView(LoginRequiredMixin, FormView):
    template_name = 'tasks/update.html'
    form_class = TaskForm
    success_url = reverse_lazy('tasks:list')

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        task_id = kwargs.get('pk')
        success, task = API.get_task(request, task_id)
        if not success:
            redirect_response = handle_api_auth_error(request, task)
            if redirect_response:
                return redirect_response
            messages.error(request, 'Error al cargar la tarea.')
            return redirect('tasks:list')
        self.task = task
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        success, projects_result = API.get_projects(self.request)
        if success:
            kwargs['user_projects'] = projects_result.get('results', [])
        else:
            kwargs['user_projects'] = []

        success, users_result = API.get_users(self.request)
        if success:
            kwargs['users'] = users_result if isinstance(users_result, list) else users_result.get('results', [])
        else:
            kwargs['users'] = []

        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not hasattr(self, 'task'):
            task_id = self.kwargs.get('pk')
            success, task = API.get_task(self.request, task_id)
            if not success:
                messages.error(self.request, 'Error al cargar la tarea.')
                return context
            self.task = task

        raw_due = self.task.get('due_date')  # "2026-02-14T08:37:00-06:00"
        due_local = ''
        if raw_due:
            due_local = raw_due[:16]  # "2026-02-14T08:37"

        context['task'] = self.task

        if 'form' not in kwargs:
            form = self.get_form()
            assigned_to = self.task.get('assigned_to')
            assigned_to_id = assigned_to.get('id') if isinstance(assigned_to, dict) else assigned_to
            initial_data = {
                'title': self.task.get('title'),
                'description': self.task.get('description'),
                'project': str(self.task.get('project') or ''),
                'assigned_to': str(assigned_to_id or ''),
                'status': self.task.get('status'),
                'priority': self.task.get('priority'),
                'due_date': due_local,
            }
            form.initial = initial_data
            context['form'] = form

        return context

    def form_valid(self, form):
        task_id = self.kwargs.get('pk')
        project_id = int(form.cleaned_data['project']) if form.cleaned_data['project'] else None
        assigned_to_id = int(form.cleaned_data['assigned_to']) if form.cleaned_data['assigned_to'] else None

        if not hasattr(self, 'task'):
            success, task = API.get_task(self.request, task_id)
            if not success:
                messages.error(self.request, 'Error al cargar la tarea.')
                return redirect('tasks:list')
            self.task = task

        task_data = {
            'title': form.cleaned_data['title'],
            'description': form.cleaned_data['description'],
            'project': project_id,
            'assigned_to_id': assigned_to_id,
            'status': form.cleaned_data['status'],
            'priority': form.cleaned_data['priority'],
            'due_date': form.cleaned_data['due_date'].isoformat() if form.cleaned_data['due_date'] else None,
        }

        success, result = API.update_task(self.request, task_id, task_data)

        if success:
            messages.success(self.request, 'Tarea actualizada exitosamente.')
            return super().form_valid(form)

        add_form_errors(form, result)
        return self.form_invalid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class TaskCompleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        task_id = kwargs.get('pk')
        success, result = API.update_task(request, task_id, {'status': 'completado'})
        if success:
            messages.success(request, 'Tarea marcada como completada.')
        else:
            redirect_response = handle_api_auth_error(request, result)
            if redirect_response:
                return redirect_response
            messages.error(request, 'No se pudo completar la tarea.')
        return redirect('tasks:detail', pk=task_id)


class TaskChangeStatusView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        task_id = kwargs.get('pk')
        success, task = API.get_task(request, task_id)
        if not success:
            redirect_response = handle_api_auth_error(request, task)
            if redirect_response:
                return redirect_response
            messages.error(request, 'No se pudo obtener la tarea para cambiar el estado.')
            return redirect('tasks:list')

        current_status = task.get('status')
        next_status = _get_next_status(current_status)
        success, result = API.update_task(request, task_id, {'status': next_status})

        if success:
            messages.success(request, f'Estado cambiado a {STATUS_LABELS.get(next_status, next_status)}.')
        else:
            messages.error(request, 'No se pudo cambiar el estado de la tarea.')

        return redirect('tasks:detail', pk=task_id)


class TaskDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        task_id = kwargs.get('pk')
        success, result = API.delete_task(request, task_id)
        if success:
            messages.success(request, 'Tarea eliminada exitosamente.')
            return redirect('tasks:list')
        redirect_response = handle_api_auth_error(request, result)
        if redirect_response:
            return redirect_response
        messages.error(request, 'No se pudo eliminar la tarea.')
        return redirect('tasks:detail', pk=task_id)
