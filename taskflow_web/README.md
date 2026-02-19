# TaskFlow Web - Cliente Web Django

Interfaz web de TaskFlow construida con Django Templates.  
Este proyecto consume la API REST de `taskflow-api` para autenticación, proyectos, tareas y perfil.

## Caracteristicas

- Inicio de sesion y registro de usuarios.
- Gestion de perfil de usuario.
- Dashboard con resumen de proyectos y tareas.
- CRUD de proyectos.
- Gestion de miembros por proyecto.
- CRUD de tareas.
- Cambio rapido de estado de tareas (flujo por columnas).
- Mensajeria de estado con `django.contrib.messages`.

## Stack Tecnologico

- Python 3.8+
- Django 5.2
- Requests (cliente HTTP para consumir la API)
- SQLite (por defecto)

## Estructura

```text
taskflow_web/
├── authentication/        # Login, registro, perfil
├── dashboard/             # Home con resumen
├── projects/              # Vistas y formularios de proyectos
├── tasks/                 # Vistas y formularios de tareas
├── core/                  # Integracion API, mixins y utilidades
├── templates/             # Plantillas HTML
├── static/                # JS y recursos estaticos
├── taskflow_web/          # settings.py / urls.py
├── manage.py
└── requirements.txt
```

## Requisitos Previos

1. Tener la API corriendo en `http://127.0.0.1:8000`.
2. Tener Python y `pip` instalados.

## Instalacion

1. Crear y activar entorno virtual:

```bash
cd taskflow_web
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Aplicar migraciones:

```bash
python manage.py migrate
```

4. (Opcional) Crear superusuario:

```bash
python manage.py createsuperuser
```

## Configuracion

En `taskflow_web/taskflow_web/settings.py`, la URL de la API se define con:

```python
API_BASE_URL = "http://127.0.0.1:8000/api"
```

Si cambias el host/puerto de la API, ajusta ese valor.

## Ejecucion

Levanta la web en un puerto distinto al backend (recomendado `8001`):

```bash
python manage.py runserver 8001
```

Accede en:

- Web: `http://127.0.0.1:8001`
- Admin: `http://127.0.0.1:8001/admin`

## Rutas Principales

- `/` Dashboard
- `/auth/login/` Login
- `/auth/register/` Registro
- `/auth/profile/` Perfil
- `/projects/` Lista de proyectos
- `/projects/create/` Crear proyecto
- `/tasks/` Lista de tareas
- `/tasks/create/` Crear tarea

## Integracion con API

La comunicacion con el backend se centraliza en `taskflow_web/core/api.py`.

- Se usan tokens JWT almacenados en sesion.
- Si el `access token` expira, se intenta refresh automatico.
- Si falla la autenticacion, el usuario se redirige a login.

## Pruebas

Ejecutar pruebas del proyecto web:

```bash
python manage.py test
```

## Capturas

Puedes usar estas capturas para mostrar la UI en el portafolio:

- `../assets/dashboard.png`
- `../assets/projects.png`
- `../assets/tasks.png`
- `../assets/members.png`
- `../assets/profile.png`

## Decisiones Tecnicas

- Se eligio Django Templates para mantener una arquitectura MVC simple y rapida de iterar.
- La logica de consumo API se centralizo en `core/api.py` para evitar duplicacion.
- El control de acceso se resolvio con `LoginRequiredMixin` basado en token de sesion.
- Se priorizo UX de negocio con feedback inmediato via mensajes de exito/error.
