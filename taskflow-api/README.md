# TaskFlow API - Gestor de Tareas Colaborativo

🚀 **API REST profesional para gestión de tareas colaborativas tipo Trello/Asana con documentación completa en español**

## 📋 Tabla de Contenido

- [Características](#-características)
- [Tecnologías](#-tecnologías)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso de la API](#-uso-de-la-api)
- [Documentación](#-documentación)
- [Endpoints](#-endpoints)
- [Autenticación](#-autenticación)
- [Ejemplos](#-ejemplos)
- [Contribución](#-contribución)

## ✨ Características

### 🔐 **Autenticación Avanzada**
- **JWT Tokens** con refresh automático
- **Access Token:** 60 minutos de validez
- **Refresh Token:** 7 días de validez
- **Rotación de tokens** para mayor seguridad

### 👥 **Gestión de Usuarios**
- Registro y login de usuarios
- Perfiles extendidos personalizados
- Gestión de datos de usuario

### 📋 **Gestión de Proyectos**
- Crear, leer, actualizar y eliminar proyectos
- Sistema de propietarios y miembros
- Control de permisos granular

### ✅ **Gestión de Tareas**
- CRUD completo de tareas
- Asignación de tareas a usuarios
- Estados y prioridades configurables
- Fechas de entrega y seguimiento

### 💬 **Sistema de Comentarios**
- Comentarios en tareas
- Notificaciones de actividad
- Historial de cambios

### 📚 **Documentación Profesional**
- **Swagger UI** interactivo en español
- **ReDoc** documentación técnica
- **Ejemplos** y guías de uso
- **Operation IDs** únicos y consistentes

## 🛠️ Tecnologías

- **Backend:** Django 5.1.4
- **API:** Django REST Framework 3.15.2
- **Autenticación:** djangorestframework-simplejwt 5.3.1
- **Documentación:** drf-spectacular 0.29.0
- **Base de datos:** SQLite (configurable a PostgreSQL/MySQL)

## 🚀 Instalación

### Prerrequisitos
- Python 3.8+
- pip
- Virtualenv (recomendado)

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/taskflow-api.git
cd taskflow-api
```

### 2. Crear entorno virtual
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Crear superusuario (opcional)
```bash
python manage.py createsuperuser
```

### 6. Iniciar servidor
```bash
python manage.py runserver
```

## ⚙️ Configuración

### Variables de Entorno
```bash
# settings.py
SECRET_KEY='tu-secret-key-aqui'
DEBUG=False  # En producción
ALLOWED_HOSTS=['tu-dominio.com']
```

### Configuración JWT
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}
```

## 🌐 Uso de la API

### Documentación Interactiva
- **Swagger UI:** `http://127.0.0.1:8000/api/docs/`
- **ReDoc:** `http://127.0.0.1:8000/api/redoc/`
- **Schema JSON:** `http://127.0.0.1:8000/api/schema/`

### Health Check
```bash
curl http://127.0.0.1:8000/health/
```

## 📚 Documentación

### 🎯 Características de la Documentación

- **100% en español** - Toda la documentación está en español
- **Operation IDs únicos** - Facilita la integración
- **Tags organizadas** - Agrupación lógica de endpoints
- **Ejemplos detallados** - Para cada request/response
- **Guías de uso** - Paso a paso para cada flujo
- **Manejo de errores** - Documentación completa de errores

### 📖 Estructura de Documentación

#### 🔐 Autenticación
- `POST /api/auth/register/` - Registrar usuario
- `POST /api/auth/login/` - Iniciar sesión
- `POST /api/auth/refresh/` - Refrescar token
- `GET/PUT/PATCH /api/auth/profile/` - Gestionar perfil
- `GET /api/auth/user/` - Datos del usuario actual

#### 📋 Proyectos
- `GET/POST /api/projects/` - Listar/Crear proyectos
- `GET/PUT/PATCH/DELETE /api/projects/{id}/` - Gestión de proyecto
- `POST /api/projects/{id}/members/` - Agregar miembro
- `DELETE /api/projects/{id}/members/{user_id}/` - Eliminar miembro

#### ✅ Tareas
- `GET/POST /api/tasks/` - Listar/Crear tareas
- `GET/PUT/PATCH/DELETE /api/tasks/{id}/` - Gestión de tarea
- `GET/POST /api/tasks/{id}/comments/` - Comentarios
- `POST /api/tasks/{id}/assign/` - Asignar tarea

## 🔐 Autenticación

### Flujo de Autenticación

1. **Registrar usuario**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario",
    "email": "usuario@ejemplo.com",
    "password": "contraseña123",
    "password_confirm": "contraseña123"
  }'
```

2. **Iniciar sesión**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario",
    "password": "contraseña123"
  }'
```

3. **Usar token en endpoints protegidos**
```bash
curl -X GET http://127.0.0.1:8000/api/projects/ \
  -H "Authorization: Bearer tu_access_token_aqui"
```

4. **Refrescar token**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "tu_refresh_token_aqui"
  }'
```

## 📊 Ejemplos de Uso

### Crear Proyecto
```bash
curl -X POST http://127.0.0.1:8000/api/projects/ \
  -H "Authorization: Bearer tu_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mi Proyecto",
    "description": "Descripción del proyecto"
  }'
```

### Crear Tarea
```bash
curl -X POST http://127.0.0.1:8000/api/tasks/ \
  -H "Authorization: Bearer tu_token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Nueva Tarea",
    "description": "Descripción de la tarea",
    "project": 1,
    "assigned_to": 2,
    "status": "todo",
    "priority": "medium"
  }'
```

### Agregar Comentario
```bash
curl -X POST http://127.0.0.1:8000/api/tasks/1/comments/ \
  -H "Authorization: Bearer tu_token" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Este es un comentario en la tarea"
  }'
```

## 🏗️ Arquitectura

### Estructura del Proyecto
```
taskflow-api/
├── taskflow/
│   ├── settings.py          # Configuración principal
│   ├── urls.py              # URLs principales
│   └── views.py             # Vistas de bienvenida
├── authentication/
│   ├── models.py            # Modelos de usuario y perfil
│   ├── views.py             # Vistas de autenticación
│   ├── serializers.py       # Serializadores
│   └── urls.py              # URLs de autenticación
├── projects/
│   ├── models.py            # Modelos de proyectos
│   ├── views.py             # Vistas de proyectos
│   ├── serializers.py       # Serializadores
│   └── urls.py              # URLs de proyectos
├── tasks/
│   ├── models.py            # Modelos de tareas y comentarios
│   ├── views.py             # Vistas de tareas
│   ├── serializers.py       # Serializadores
│   └── urls.py              # URLs de tareas
└── requirements.txt         # Dependencias
```

## 🚀 Despliegue

### Docker
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### Environment Variables
```bash
export SECRET_KEY='tu-secret-key'
export DEBUG=False
export ALLOWED_HOSTS='tu-dominio.com'
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 📞 Soporte

- 📧 Email:  adrianlugofrontela@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/adrianlugo/taskflow-api/)
- 📖 Documentación: [Documentación Completa](http://127.0.0.1:8000/api/docs/)

## 🎉 ¡Gracias por usar TaskFlow API!

Con esta API tienes todo lo necesario para construir una aplicación de gestión de tareas colaborativas profesional y escalable.

---

**Hecho con ❤️ y Django**
