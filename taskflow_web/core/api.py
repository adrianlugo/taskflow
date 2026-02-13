import requests
from datetime import date, datetime
from django.conf import settings

__all__ = ['API']

class API:
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
    def _refresh_token(cls, request):
        """Intenta refrescar el token de acceso usando el refresh token."""
        refresh_token = request.session.get('refresh')
        
        if not refresh_token:
            return False
        
        url = f"{cls.BASE_URL}/auth/refresh/"
        data = {'refresh': refresh_token}
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            
            # Actualizar tokens en sesión (nombres correctos)
            request.session['access'] = result.get('access')
            if result.get('refresh'):
                request.session['refresh'] = result.get('refresh')
            request.session.save()
            return True
        except requests.exceptions.HTTPError:
            # Si el refresh token también expiró, limpiar sesión
            request.session.pop('access', None)
            request.session.pop('refresh', None)
            request.session.pop('user_data', None)
            request.session.save()
            return False
        except requests.exceptions.RequestException:
            return False
    
    @classmethod
    def _make_request(cls, request, method, url, **kwargs):
        """Método centralizado para hacer requests con manejo de token expirado."""
        headers = cls._get_headers(request)
        final_headers = headers.copy()
        if 'headers' in kwargs and kwargs['headers']:
            final_headers.update(kwargs['headers'])
        kwargs['headers'] = final_headers
        
        try:
            response = requests.request(method, url, **kwargs)
            
            # Si el token expiró, intentar refrescarlo
            if (response.status_code == 401 and 
                'Token is expired' in response.text and
                request.session.get('refresh')):
                
                if cls._refresh_token(request):
                    # Reintentar la petición con el nuevo token
                    headers = cls._get_headers(request)
                    final_headers = headers.copy()
                    if 'headers' in kwargs and kwargs['headers']:
                        final_headers.update(kwargs['headers'])
                    kwargs['headers'] = final_headers
                    response = requests.request(method, url, **kwargs)
            
            return response
        except requests.exceptions.RequestException as e:
            raise e

    @classmethod
    def _get_headers(cls, request):
        """Obtener headers con token de autenticación"""
        headers = {
            'Content-Type': 'application/json',
        }
        
        # Obtener token JWT de la sesión
        token = request.session.get('access')
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
            
            # Guardar tokens en la sesión (nombres correctos)
            access_token = result.get('access')
            refresh_token = result.get('refresh')
            
            
            # Guardar tokens en la sesión
            request.session['access'] = access_token
            request.session['refresh'] = refresh_token
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
        return 'access' in request.session
    
    @classmethod
    def update_profile(cls, request, profile_data):
        """Actualizar perfil del usuario (Profile) via API."""
        url = f"{cls.BASE_URL}/auth/profile/"
        
        try:
            payload = cls._jsonable(profile_data)
            response = cls._make_request(request, 'PATCH', url, json=payload)
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
        
        try:
            response = cls._make_request(request, 'GET', url)
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
    def update_project(cls, request, project_id, project_data):
        """Actualizar un proyecto existente."""
        url = f"{cls.BASE_URL}/projects/{project_id}/"
        
        try:
            payload = cls._jsonable(project_data)
            response = cls._make_request(request, 'PATCH', url, json=payload)
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
    def get_users(cls, request):
        """Obtener lista de todos los usuarios."""
        # Si no hay token, no intentes llamar a la API
        if not request.session.get('access'):
            print("DEBUG API: No hay token en sesión, no se puede obtener usuarios.")
            return False, {'error': 'No autenticado'}
        
        url = f"{cls.BASE_URL}/auth/users/"
        print(f"DEBUG API: Llamando a {url}")
        
        # Verificar headers que se enviarán
        headers = cls._get_headers(request)
        print(f"DEBUG API: Headers: {headers}")
        
        try:
            print(f"DEBUG API: Haciendo request GET...")
            response = cls._make_request(request, 'GET', url)
            print(f"DEBUG API: Response status: {response.status_code}")
            print(f"DEBUG API: Response headers: {dict(response.headers)}")
            print(f"DEBUG API: Response text: {response.text[:200]}...")
            
            response.raise_for_status()
            result = response.json()
            print(f"DEBUG API: Response JSON: {result}")
            
            # Devolver solo la lista de resultados
            if 'results' in result:
                print(f"DEBUG API: Devolviendo {len(result['results'])} usuarios")
                return True, result['results']
            else:
                print(f"DEBUG API: Devolviendo resultado directo: {len(result) if isinstance(result, list) else 'No es lista'}")
                return True, result
                
        except requests.exceptions.RequestException as e:
            print(f"DEBUG API: Error en request: {str(e)}")
            print(f"DEBUG API: Tipo de error: {type(e)}")
            return False, {'error': f'Error obteniendo usuarios: {str(e)}'}

    @classmethod
    def search_users(cls, request, query):
        """Buscar usuarios por username o email."""
        url = f"{cls.BASE_URL}/auth/users/search/?q={query}"
        
        try:
            response = cls._make_request(request, 'GET', url)
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
    def add_project_member(cls, request, project_id, data):
        """Agregar un miembro al proyecto usando  user_id."""
       
        # Ahora agregar el miembro usando el ID
        url = f"{cls.BASE_URL}/projects/{project_id}/members/"
        
        try:
            response = cls._make_request(request, 'POST', url, json=data)
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
    def remove_project_member(cls, request, project_id, user_id):
        """Eliminar un miembro del proyecto."""
        url = f"{cls.BASE_URL}/projects/{project_id}/members/{user_id}/"
        
        try:
            response = cls._make_request(request, 'DELETE', url)
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
    def delete_project(cls, request, project_id):
        """Eliminar un proyecto."""
        url = f"{cls.BASE_URL}/projects/{project_id}/"
        
        try:
            response = cls._make_request(request, 'DELETE', url)
            response.raise_for_status()
            if response.text:
                try:
                    return True, response.json()
                except ValueError:
                    return True, {'detail': response.text}
            return True, {}
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
        # Limpiar tokens de la sesión (nombres correctos)
        request.session.pop('access', None)
        request.session.pop('refresh', None)
        request.session.pop('user_data', None)
        request.session.save()
        return True, {'message': 'Sesión cerrada correctamente'}
