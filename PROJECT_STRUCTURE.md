# 📁 Estructura del Proyecto TaskFlow

## 🏗️ Arquitectura General

```
taskflow-main/
├── README.md                    # Documentación principal
├── setup.md                     # Guía de instalación rápida
├── .env.example                 # Plantilla de variables de entorno
├── PROJECT_STRUCTURE.md          # Este archivo
│
├── taskflow-api/                 # 🐍 API REST Backend
│   ├── manage.py                 # Gestor de Django
│   ├── requirements.txt          # Dependencias Python
│   ├── .env                      # Variables de entorno (crear)
│   ├── taskflow_api/             # Configuración principal
│   │   ├── __init__.py
│   │   ├── settings.py           # Configuración Django
│   │   ├── urls.py               # URLs principales
│   │   └── wsgi.py               # WSGI config
│   │
│   ├── authentication/           # 🔐 Sistema de autenticación
│   │   ├── __init__.py
│   │   ├── urls.py               # URLs de auth
│   │   ├── views.py              # Vistas de auth
│   │   ├── serializers.py        # Serializadores JWT
│   │   └── jwt_views.py          # Vistas personalizadas JWT
│   │
│   ├── projects/                 # 📊 Gestión de proyectos
│   │   ├── __init__.py
│   │   ├── urls.py               # URLs de proyectos
│   │   ├── views.py              # Vistas de proyectos
│   │   ├── models.py             # Modelos Project, Member
│   │   ├── serializers.py        # Serializadores
│   │   └── permissions.py        # Permisos custom
│   │
│   ├── tasks/                    # 📝 Gestión de tareas (en desarrollo)
│   │   ├── __init__.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── models.py
│   │   └── serializers.py
│   │
│   └── users/                    # 👥 Gestión de usuarios
│       ├── __init__.py
│       ├── urls.py
│       ├── views.py
│       ├── models.py
│       └── serializers.py
│
├── taskflow_web/                 # 🌐 Frontend Django
│   ├── manage.py                 # Gestor de Django
│   ├── requirements.txt          # Dependencias Python
│   ├── .env                      # Variables de entorno (crear)
│   ├── taskflow_web/             # Configuración principal
│   │   ├── __init__.py
│   │   ├── settings.py           # Configuración Django
│   │   ├── urls.py               # URLs principales
│   │   └── wsgi.py               # WSGI config
│   │
│   ├── authentication/           # 🔐 Vistas de autenticación
│   │   ├── __init__.py
│   │   ├── urls.py               # URLs de auth
│   │   ├── views.py              # LoginView, ProfileView
│   │   ├── forms.py              # Formularios Django
│   │   └── urls.py               # URLs específicas
│   │
│   ├── dashboard/                # 📊 Dashboard principal
│   │   ├── __init__.py
│   │   ├── urls.py               # URLs del dashboard
│   │   ├── views.py              # HomeView
│   │   └── templates/dashboard/  # Templates del dashboard
│   │       └── home.html         # Template principal
│   │
│   ├── projects/                 # 📊 Gestión de proyectos
│   │   ├── __init__.py
│   │   ├── urls.py               # URLs de proyectos
│   │   ├── views.py              # Vistas CRUD + miembros
│   │   ├── forms.py              # Formularios Django
│   │   └── templates/projects/    # Templates de proyectos
│   │       ├── list.html         # Lista de proyectos
│   │       ├── create.html       # Crear proyecto
│   │       ├── detail.html       # Detalle + miembros
│   │       └── update.html       # Editar proyecto
│   │
│   ├── core/                     # 🔧 Utilidades y API Service
│   │   ├── __init__.py
│   │   ├── api.py                # APIService (cliente HTTP)
│   │   ├── mixins.py             # LoginRequiredMixin
│   │   ├── utils.py              # add_form_errors
│   │   └── templates/core/       # Templates base
│   │       └── base.html         # Layout principal
│   │
│   ├── templates/                # 🎨 Templates globales
│   │   ├── base.html             # Layout principal
│   │   └── authentication/       # Templates de auth
│   │       ├── login.html        # Login form
│   │       ├── register.html     # Register form
│   │       └── profile.html      # Profile view
│   │
│   └── static/                   # 📁 Archivos estáticos
│       ├── css/                  # Estilos CSS
│       ├── js/                   # JavaScript
│       └── images/               # Imágenes
│
└── shared/                       # 📁 Recursos compartidos
    ├── media/                    # Archivos multimedia
    └── docs/                     # Documentación adicional
```

## 🔄 Flujo de Comunicación

### Frontend → API
```
Frontend Django (taskflow_web)
    ↓ HTTP Requests
API REST Django (taskflow_api)
    ↓ Business Logic
Database (SQLite/PostgreSQL)
```

### Componentes Clave

#### 1. **APIService** (`taskflow_web/core/api.py`)
- Cliente HTTP para consumir API REST
- Manejo de tokens JWT
- Refresh automático de tokens
- Centralización de llamadas API

#### 2. **LoginRequiredMixin** (`taskflow_web/core/mixins.py`)
- Protección de vistas
- Verificación de tokens en sesión
- Redirect automático a login

#### 3. **JWT Views** (`taskflow-api/authentication/jwt_views.py`)
- Vista personalizada de refresh
- Documentación OpenAPI
- Manejo de errores específicos

#### 4. **Project Management**
- **API**: CRUD completo + miembros
- **Frontend**: Vistas con formularios + AJAX
- **UI**: Modales interactivos + filtros

## 🎯 Funcionalidades por Módulo

### 🔐 Autenticación
- **API**: JWT tokens, refresh, profile
- **Frontend**: Login, logout, register, profile edit
- **UI**: Forms con validación, feedback visual

### 📊 Proyectos
- **API**: CRUD, member management, permissions
- **Frontend**: List, create, detail, update views
- **UI**: Cards, modals, member selector con filtro

### 👥 Miembros
- **API**: Add/remove members con validación
- **Frontend**: AJAX endpoints, user lookup
- **UI**: Dropdown con búsqueda, filtro real-time

### 🎨 UI/UX
- **Framework**: Bootstrap 5 + Font Awesome
- **Patterns**: Modals, alerts, responsive design
- **JavaScript**: Vanilla JS, fetch API, event listeners

## 🛠️ Tecnologías por Capa

### Backend API
- **Django 5.1.4** - Framework principal
- **DRF 3.15.2** - API REST
- **Simple JWT 5.3.1** - Autenticación
- **CORS Headers** - Cross-origin
- **DRF Spectacular** - OpenAPI docs

### Frontend Web
- **Django 5.2** - Framework principal
- **Bootstrap 5** - UI Framework
- **Font Awesome** - Iconos
- **Vanilla JS** - Interactividad

### Desarrollo
- **Python 3.8+** - Lenguaje
- **Requests 2.32.5** - Cliente HTTP
- **Decouple 3.8** - Configuración
- **SQLite** - Base de datos (default)

## 🚀 Flujo de Desarrollo

### 1. **Setup del Entorno**
```bash
# API
cd taskflow-api
python manage.py runserver 8000

# Frontend
cd taskflow_web  
python manage.py runserver 9000
```

### 2. **Flujo de Autenticación**
```
1. User login → Frontend Django
2. Frontend → API (POST /auth/login/)
3. API → JWT tokens (access + refresh)
4. Frontend → Session storage
5. Requests subsiguientes con Authorization header
6. Auto-refresh cuando access expira
```

### 3. **Flujo de Proyectos**
```
1. Dashboard → Projects list
2. Create project → Form validation
3. POST to API → Project creation
4. Detail view → Member management
5. Add member → User selector + API call
6. Real-time UI update
```

## 📋 Próximos Pasos

### 🚧 En Desarrollo
- [ ] Gestión completa de tareas
- [ ] Sistema de notificaciones
- [ ] Archivos adjuntos
- [ ] Dashboard avanzado

### 🎯 Mejoras Planeadas
- [ ] Tests automatizados
- [ ] Docker containerización
- [ ] CI/CD pipeline
- [ ] API GraphQL
- [ ] App móvil React Native

---

Esta estructura proporciona una base sólida y escalable para el desarrollo continuo de TaskFlow.
