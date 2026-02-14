from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from core.api import API
from .forms import TaskForm
from core.mixins import LoginRequiredMixin
from core.utils import add_form_errors

class TaskListView(LoginRequiredMixin, TemplateView):
    template_name = 'tasks/list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener proyectos para el filtro
        success, projects_result = API.get_projects(self.request)
        if success:
            context['projects'] = projects_result.get('results', [])
        else:
            context['projects'] = []
        
        # Obtener tareas (filtradas por proyecto si se especifica)
        project_id = self.request.GET.get('project')
        success, tasks_result = API.get_tasks(self.request, project_id)
        if success:
            context['tasks'] = tasks_result.get('results', [])
            context['tasks_count'] = tasks_result.get('count', 0)
        else:
            context['tasks'] = []
            context['tasks_count'] = 0
            messages.error(self.request, 'Error al cargar las tareas.')
        
        return context

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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task_id = kwargs.get('pk')

        success, task = API.get_task(self.request, task_id)
        if success:
            context['task'] = task
        else:
            messages.error(self.request, 'Error al cargar la tarea.')
        
        return context

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
            messages.error(request, 'Error al cargar el proyecto.')
            return redirect('tasks:list')
        # Guardar la tarea para usarlo después
        self.task = task
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Asegurarnos de que self.task exista
        if not hasattr(self, 'project'):
            project_id = self.kwargs.get('pk')
            success, project = API.get_project(self.request, project_id)
            if not success:
                messages.error(self.request, 'Error al cargar el proyecto.')
                # NO retornes redirect aquí, solo retorna context vacío
                return context
            self.project = project
        
        context['task'] = self.task
        
        # Pre-cargar el formulario con datos actuales
        if 'form' not in kwargs:
            form = self.get_form()
            project_id = int(form.cleaned_data['project']) if form.cleaned_data['project'] else None
            assigned_to_id = int(form.cleaned_data['assigned_to']) if form.cleaned_data['assigned_to'] else None
            initial_data = {
                'title': form.cleaned_data['title'],
                'description': form.cleaned_data['description'],
                'project': project_id,
                'assigned_to_id': assigned_to_id,
                'status': form.cleaned_data['status'],
                'priority': form.cleaned_data['priority'],
                'due_date': form.cleaned_data['due_date'].isoformat() if form.cleaned_data['due_date'] else None,
            }
            form.initial = initial_data
            context['form'] = form
        
        return context
    
    def form_valid(self, form):
        task_id = self.kwargs.get('pk')
        project_id = int(form.cleaned_data['project']) if form.cleaned_data['project'] else None
        assigned_to_id = int(form.cleaned_data['assigned_to']) if form.cleaned_data['assigned_to'] else None

        # Asegurarnos de que self.task exista
        if not hasattr(self, 'task'):
            success, task = API.get_task(self.request, task_id)
            if not success:
                messages.error(self.request, 'Error al cargar la tarea.')
                return redirect('tasks:list')
            self.project = task
        
        task_data = {
            'title': form.cleaned_data['title'],
            'description': form.cleaned_data['description'],
            'project': project_id,
            'assigned_to_id': assigned_to_id,
            'status': form.cleaned_data['status'],
            'priority': form.cleaned_data['priority'],
            'due_date': form.cleaned_data['due_date'].isoformat() if form.cleaned_data['due_date'] else None,
        }
                
        success, result = API.update_project(self.request, task_id, task_data)
        
        if success:
            messages.success(self.request, '¡Tarea actualizado exitosamente!')
            return super().form_valid(form)
        
        add_form_errors(form, result)
        return self.form_invalid(form)
    
    def form_invalid(self, form):
        return super().form_invalid(form)