from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from core.api import API
from .forms import TaskForm, TaskCommentForm
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
            tasks_list = tasks_result.get('results', [])
            
            # Anotar permisos en cada tarea para el template
            session_user_id = request.session.get('user_data', {}).get('id')
            for task in tasks_list:
                owner = task.get('project_detail', {}).get('owner')
                created_by = task.get('created_by')
                assigned_to = task.get('assigned_to')
                
                is_project_owner = bool(owner and owner.get('id') == session_user_id)
                is_task_creator = bool(created_by and created_by.get('id') == session_user_id)
                
                task['is_owner'] = is_project_owner or is_task_creator
                task['is_assigned'] = bool(assigned_to and assigned_to.get('id') == session_user_id)
                
            context['tasks'] = tasks_list
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

    def dispatch(self, request, *args, **kwargs):
        # Antes de mostrar el formulario, verificar si el usuario tiene proyectos
        success, projects_result = API.get_projects(request)
        if success:
            projects = projects_result.get('results', [])
            if not projects:
                messages.warning(request, 'Debes crear al menos un proyecto antes de poder crear tareas.')
                return redirect('projects:create')
        else:
            # Si el API falla, manejamos el error (ej: re-autenticar)
            redirect_response = handle_api_auth_error(request, projects_result)
            if redirect_response:
                return redirect_response
            messages.error(request, 'No pudimos verificar tus proyectos. Por favor, intenta de nuevo.')
            return redirect('tasks:list')
            
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # En creación no sabemos el proyecto hasta que el usuario lo elige;
        # por UX, por defecto tratamos a usuarios no-owner como "no pueden asignar".
        context['can_assign'] = True
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # Obtener proyectos del usuario para el formulario
        success, projects_result = API.get_projects(self.request)
        if success:
            kwargs['user_projects'] = projects_result.get('results', [])
        else:
            kwargs['user_projects'] = []

        # Para crear, no sabemos el proyecto aún (si no viene preseleccionado).
        # El formulario debe renderizar el select vacío o con una lista general.
        # Como mínimo, cargamos todos los usuarios para que el usuario pueda seleccionar,
        # y el backend validará pertenencia al proyecto.
        success, users_result = API.get_users(self.request)
        if success:
            kwargs['users'] = users_result if isinstance(users_result, list) else users_result.get('results', [])
        else:
            kwargs['users'] = []

        return kwargs
    
    def form_valid(self, form):
        project_id = int(form.cleaned_data['project']) if form.cleaned_data['project'] else None
        # En UI, solo el owner debería asignar. Como en la creación no sabemos si es owner
        # del proyecto hasta consultar el proyecto seleccionado, dejamos que la API decida.
        # Si quieres bloquearlo del lado web, desactiva/oculta el select en el template.
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
            return super().form_valid(form)
        
        add_form_errors(form, result)
        return self.form_invalid(form)
    
    def form_invalid(self, form):
        return super().form_invalid(form)

class TaskProjectAssigneesView(LoginRequiredMixin, View):
    """Devuelve owner+members de un proyecto para poblar el select de asignación."""

    def get(self, request, *args, **kwargs):
        project_id = kwargs.get('project_id')
        success, project = API.get_project(request, project_id)
        if not success:
            redirect_response = handle_api_auth_error(request, project)
            if redirect_response:
                return redirect_response
            return HttpResponse('{"success": false}', content_type='application/json', status=400)

        owner = project.get('owner') if isinstance(project, dict) else None
        members = project.get('members', []) if isinstance(project, dict) else []

        # Evitar duplicados usando un diccionario por ID
        unique_assignees = {}
        if owner and isinstance(owner, dict) and 'id' in owner:
            unique_assignees[owner['id']] = owner
        if isinstance(members, list):
            for m in members:
                if isinstance(m, dict) and 'id' in m:
                    unique_assignees[m['id']] = m
                    
        assignees = list(unique_assignees.values())

        # Respuesta mínima para el JS
        from django.http import JsonResponse
        data = [
            {
                'id': u.get('id'),
                'username': u.get('username'),
                'first_name': u.get('first_name'),
                'last_name': u.get('last_name'),
                'email': u.get('email'),
            }
            for u in assignees
            if isinstance(u, dict)
        ]
        return JsonResponse({'success': True, 'users': data})


class TaskDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'tasks/detail.html'
    comment_form_class = TaskCommentForm

    def get(self, request, *args, **kwargs):
        task_id = kwargs.get('pk')
        success, task = API.get_task(request, task_id)
        if not success:
            redirect_response = handle_api_auth_error(request, task)
            if redirect_response:
                return redirect_response
            messages.error(request, 'Error al cargar la tarea.')
            return self.render_to_response({'task': None})

        context = self._build_context(request, task_id, task)
        if isinstance(context, HttpResponse):
            return context
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        task_id = kwargs.get('pk')
        form = TaskCommentForm(request.POST)
        if form.is_valid():
            payload = {'content': form.cleaned_data['content']}
            success, result = API.create_task_comment(request, task_id, payload)
            if success:
                messages.success(request, 'Comentario agregado correctamente.')
                return redirect('tasks:detail', pk=task_id)
            redirect_response = handle_api_auth_error(request, result)
            if redirect_response:
                return redirect_response
            messages.error(request, result.get('error', 'No se pudo guardar el comentario.'))
        else:
            messages.error(request, 'Completa el comentario antes de enviarlo.')

        success, task = API.get_task(request, task_id)
        if not success:
            redirect_response = handle_api_auth_error(request, task)
            if redirect_response:
                return redirect_response
            messages.error(request, 'Error al recargar la tarea.')
            return redirect('tasks:list')

        context = self._build_context(request, task_id, task, comment_form=form)
        if isinstance(context, HttpResponse):
            return context
        return self.render_to_response(context)

    def _build_context(self, request, task_id, task, comment_form=None):
        context = {'task': task}

        # Flags de rol para UI
        session_user_id = request.session.get('user_data', {}).get('id')
        owner = task.get('project_detail', {}).get('owner')
        created_by = task.get('created_by')

        # Se tiene permiso "total" si es dueño del proyecto o si él mismo creó la tarea
        is_project_owner = bool(owner and owner.get('id') == session_user_id)
        is_task_creator = bool(created_by and created_by.get('id') == session_user_id)
        
        context['is_owner'] = is_project_owner or is_task_creator
        context['is_assigned'] = bool(task.get('assigned_to') and task.get('assigned_to', {}).get('id') == session_user_id)
        current_status = task.get('status')
        next_status = _get_next_status(current_status)
        context['next_status'] = next_status
        context['next_status_label'] = STATUS_LABELS.get(next_status, next_status)
        comment_form = comment_form or self.comment_form_class()
        context['comment_form'] = comment_form

        comments_context, redirect_response = self._load_comments_context(request, task_id)
        if redirect_response:
            return redirect_response
        context.update(comments_context)

        return context

    def _load_comments_context(self, request, task_id):
        success, comments_result = API.get_task_comments(request, task_id)
        if not success:
            redirect_response = handle_api_auth_error(request, comments_result)
            if redirect_response:
                return None, redirect_response
            messages.error(request, 'Error al cargar los comentarios de la tarea.')
            return {'comments': [], 'comments_count': 0}, None

        comments = comments_result.get('results', [])
        return {
            'comments': comments,
            'comments_count': comments_result.get('count', len(comments))
        }, None



class TaskUpdateView(LoginRequiredMixin, FormView):
    template_name = 'tasks/update.html'
    form_class = TaskForm

    def get_success_url(self):
        next_url = self.request.POST.get('next')
        if next_url and next_url.startswith('/'):
            return next_url
        return reverse_lazy('tasks:list')

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        task_id = kwargs.get('pk')
        success, task = API.get_task(request, task_id)
        if not success:
            redirect_response = handle_api_auth_error(request, task)
            if redirect_response:
                return redirect_response
            messages.error(request, 'Error al cargar la tarea.')
            return redirect('tasks:list')
        
        self.task = task
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        success, projects_result = API.get_projects(self.request)
        if success:
            kwargs['user_projects'] = projects_result.get('results', [])
        else:
            kwargs['user_projects'] = []

        # Mostrar solo asignables del proyecto (owner + members)
        task = self.task

        users = []
        project_detail = getattr(self, 'task', {}) or {}
        project_detail = project_detail.get('project_detail') if isinstance(project_detail, dict) else None
        project_id = project_detail.get('id') if isinstance(project_detail, dict) else None

        if project_id:
            success_p, project = API.get_project(self.request, project_id)
            if success_p and isinstance(project, dict):
                unique_users = {}
                owner = project.get('owner')
                members = project.get('members', [])
                
                if owner and isinstance(owner, dict) and 'id' in owner:
                    unique_users[owner['id']] = owner
                if isinstance(members, list):
                    for m in members:
                        if isinstance(m, dict) and 'id' in m:
                            unique_users[m['id']] = m
                            
                users = list(unique_users.values())

        # fallback si no se pudo resolver: lista vacía (evita mostrar todos)
        kwargs['users'] = users

        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        raw_due = self.task.get('due_date')  # "2026-02-14T08:37:00-06:00"
        due_local = ''
        if raw_due:
            due_local = raw_due[:16]  # "2026-02-14T08:37"

        context['task'] = self.task

        # Bandera para UI: owner del proyecto o creador de la tarea tienen permisos de edición
        session_user_id = self.request.session.get('user_data', {}).get('id')
        owner = self.task.get('project_detail', {}).get('owner')
        created_by = self.task.get('created_by')

        is_project_owner = bool(owner and owner.get('id') == session_user_id)
        is_task_creator = bool(created_by and created_by.get('id') == session_user_id)
        
        context['is_owner'] = is_project_owner or is_task_creator

        # Capturar la URL anterior (Referer) o mantener 'next' actual de GET
        next_url = self.request.GET.get('next') or self.request.META.get('HTTP_REFERER')
        if next_url and next_url.startswith('http'):
            # Seguridad básica: solo usar rutas relativas para evitar redirect abierto
            from urllib.parse import urlparse
            parsed = urlparse(next_url)
            next_url = parsed.path + ('?' + parsed.query if parsed.query else '')

        context['next_url'] = next_url

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

        task_id = self.kwargs.get('pk')
        
        owner = self.task.get('project_detail', {}).get('owner')
        created_by = self.task.get('created_by')
        session_user_id = self.request.session.get('user_data', {}).get('id')
        
        is_project_owner = bool(owner and owner.get('id') == session_user_id)
        is_task_creator = bool(created_by and created_by.get('id') == session_user_id)
        has_full_permissions = is_project_owner or is_task_creator

        # Si no tiene permisos completos, solo permitir cambio de estado (Asignados)
        if not has_full_permissions:
            task_data = {
                'status': form.cleaned_data['status'],
            }
        else:
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
