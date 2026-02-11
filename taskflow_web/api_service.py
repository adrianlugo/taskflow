import requests
from datetime import date, datetime
from django.conf import settings

class APIService:
    """
    Servicio para comunicarse con la API REST de TaskFlow
    """
    
    BASE_URL = settings.API_BASE_URL

    @classmethod
    def _jsonable(cls, value):
        """Convierte valores (date/datetime) a formatos serializables por JSON."""
        if value is None:
            return None
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, dict):
            return {k: cls._jsonable(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [cls._jsonable(v) for v in value]
        return value
    
    @classmethod
    def _get_headers(cls, request):
        """Obtener headers con token de autenticación"""
        headers = {
            'Content-Type': 'application/json',
        }
        
        # Obtener token JWT de la sesión
        token = request.session.get('access_token')
        if token:
            headers['Authorization'] = f'Bearer {token}'
            
        return headers
    
    @classmethod
    def login(cls, request, username, password):
        """Iniciar sesión y obtener token JWT"""
        url = f"{cls.BASE_URL}/auth/login/"
        data = {
            'username': username,
            'password': password
        }
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            
            result = response.json()
            
            # Guardar tokens en la sesión
            request.session['access_token'] = result.get('access')
            request.session['refresh_token'] = result.get('refresh')
            request.session['user_data'] = result.get('user')
            
            # Agregar fecha de registro si no existe
            if 'date_joined' not in request.session['user_data'] and result.get('user'):
                request.session['user_data']['date_joined'] = result['user'].get('date_joined')
            
            request.session.save()
            
            return True, result
            
        except requests.exceptions.HTTPError as e:
            resp = getattr(e, 'response', None)
            if resp is not None:
                try:
                    return False, resp.json()
                except ValueError:
                    return False, {'error': resp.text}
            return False, {'error': str(e)}
        except requests.exceptions.RequestException as e:
            return False, {'error': str(e)}

    @classmethod
    def get_profile(cls, request):
        """Obtener perfil extendido (Profile) del usuario."""
        url = f"{cls.BASE_URL}/auth/profile/"
        headers = cls._get_headers(request)

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            # Cachear en sesión para precargar formularios
            request.session['profile_data'] = data
            request.session.save()

            return True, data
        except requests.exceptions.HTTPError as e:
            resp = getattr(e, 'response', None)
            if resp is not None:
                try:
                    return False, resp.json()
                except ValueError:
                    return False, {'error': resp.text}
            return False, {'error': str(e)}
        except requests.exceptions.RequestException as e:
            return False, {'error': str(e)}
    
    @classmethod
    def register(cls, request, user_data):
        """Registrar nuevo usuario"""
        url = f"{cls.BASE_URL}/auth/register/"
        
        try:
            response = requests.post(url, json=user_data)
            response.raise_for_status()
            
            return True, response.json()
            
        except requests.exceptions.HTTPError as e:
            resp = getattr(e, 'response', None)
            if resp is not None:
                try:
                    return False, resp.json()
                except ValueError:
                    return False, {'error': resp.text}
            return False, {'error': str(e)}
        except requests.exceptions.RequestException as e:
            return False, {'error': str(e)}
    
    @classmethod
    def get_user_profile(cls, request):
        """Obtener perfil del usuario"""
        url = f"{cls.BASE_URL}/auth/user/"
        headers = cls._get_headers(request)
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return True, response.json()
            
        except requests.exceptions.HTTPError as e:
            resp = getattr(e, 'response', None)
            if resp is not None:
                try:
                    return False, resp.json()
                except ValueError:
                    return False, {'error': resp.text}
            return False, {'error': str(e)}
        except requests.exceptions.RequestException as e:
            return False, {'error': str(e)}
    
    @classmethod
    def get_projects(cls, request):
        """Obtener proyectos del usuario"""
        url = f"{cls.BASE_URL}/projects/"
        headers = cls._get_headers(request)
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return True, response.json()
            
        except requests.exceptions.HTTPError as e:
            resp = getattr(e, 'response', None)
            if resp is not None:
                try:
                    return False, resp.json()
                except ValueError:
                    return False, {'error': resp.text}
            return False, {'error': str(e)}
        except requests.exceptions.RequestException as e:
            return False, {'error': str(e)}
    
    @classmethod
    def create_project(cls, request, project_data):
        """Crear nuevo proyecto"""
        url = f"{cls.BASE_URL}/projects/"
        headers = cls._get_headers(request)
        
        try:
            payload = cls._jsonable(project_data)
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            return True, response.json()
            
        except requests.exceptions.HTTPError as e:
            resp = getattr(e, 'response', None)
            if resp is not None:
                try:
                    return False, resp.json()
                except ValueError:
                    return False, {'error': resp.text}
            return False, {'error': str(e)}
        except requests.exceptions.RequestException as e:
            return False, {'error': str(e)}
    
    @classmethod
    def get_tasks(cls, request, project_id=None):
        """Obtener tareas (opcionalmente filtradas por proyecto)"""
        url = f"{cls.BASE_URL}/tasks/"
        headers = cls._get_headers(request)
        
        params = {}
        if project_id:
            params['project'] = project_id
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            return True, response.json()
            
        except requests.exceptions.HTTPError as e:
            resp = getattr(e, 'response', None)
            if resp is not None:
                try:
                    return False, resp.json()
                except ValueError:
                    return False, {'error': resp.text}
            return False, {'error': str(e)}
        except requests.exceptions.RequestException as e:
            return False, {'error': str(e)}
    
    @classmethod
    def create_task(cls, request, task_data):
        """Crear nueva tarea"""
        url = f"{cls.BASE_URL}/tasks/"
        headers = cls._get_headers(request)
        
        try:
            payload = cls._jsonable(task_data)
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            return True, response.json()
            
        except requests.exceptions.HTTPError as e:
            resp = getattr(e, 'response', None)
            if resp is not None:
                try:
                    return False, resp.json()
                except ValueError:
                    return False, {'error': resp.text}
            return False, {'error': str(e)}
        except requests.exceptions.RequestException as e:
            return False, {'error': str(e)}
    
    @classmethod
    def is_authenticated(cls, request):
        """Verificar si el usuario está autenticado"""
        return 'access_token' in request.session
    
    @classmethod
    def update_profile(cls, request, profile_data):
        """Actualizar perfil del usuario (Profile) via API."""
        url = f"{cls.BASE_URL}/auth/profile/"
        headers = cls._get_headers(request)

        try:
            payload = cls._jsonable(profile_data)
            response = requests.patch(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            # cache session
            request.session['profile_data'] = data
            request.session.save()

            return True, data
        except requests.exceptions.HTTPError as e:
            resp = getattr(e, 'response', None)
            if resp is not None:
                try:
                    return False, resp.json()
                except ValueError:
                    return False, {'error': resp.text}
            return False, {'error': str(e)}
        except requests.exceptions.RequestException as e:
            return False, {'error': str(e)}

    @classmethod
    def get_project(cls, request, project_id):
        """Obtener detalle de un proyecto."""
        url = f"{cls.BASE_URL}/projects/{project_id}/"
        headers = cls._get_headers(request)
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return True, response.json()
        except requests.exceptions.HTTPError as e:
            resp = getattr(e, 'response', None)
            if resp is not None:
                try:
                    return False, resp.json()
                except ValueError:
                    return False, {'error': resp.text}
            return False, {'error': str(e)}
        except requests.exceptions.RequestException as e:
            return False, {'error': str(e)}

    @classmethod
    def get_task(cls, request, task_id):
        """Obtener detalle de una tarea."""
        url = f"{cls.BASE_URL}/tasks/{task_id}/"
        headers = cls._get_headers(request)
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return True, response.json()
        except requests.exceptions.HTTPError as e:
            resp = getattr(e, 'response', None)
            if resp is not None:
                try:
                    return False, resp.json()
                except ValueError:
                    return False, {'error': resp.text}
            return False, {'error': str(e)}
        except requests.exceptions.RequestException as e:
            return False, {'error': str(e)}
    
    @classmethod
    def logout(cls, request):
        """Cerrar sesión"""
        # Limpiar tokens de la sesión
        request.session.pop('access_token', None)
        request.session.pop('refresh_token', None)
        request.session.pop('user_data', None)
