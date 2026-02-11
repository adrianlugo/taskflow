# 🚀 Guía Rápida de Instalación - TaskFlow

## ⚡ Instalación Automática (Recomendado)

### 1. Clonar y configurar
```bash
git clone <repository-url>
cd taskflow-main
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### 2. Instalar dependencias
```bash
# API Backend
cd taskflow-api
pip install -r requirements.txt

# Frontend Web
cd ../taskflow_web
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
```bash
# Crear archivo .env en taskflow-api/
echo "DEBUG=True
SECRET_KEY=tu-secret-key-api-aqui
ALLOWED_HOSTS=localhost,127.0.0.1" > taskflow-api/.env

# Crear archivo .env en taskflow_web/
echo "DEBUG=True
SECRET_KEY=tu-secret-key-web-aqui
API_BASE_URL=http://localhost:8000/api
ALLOWED_HOSTS=localhost,127.0.0.1" > taskflow_web/.env
```

### 4. Migraciones y superusuario
```bash
# API
cd taskflow-api
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Web
cd ../taskflow_web
python manage.py makemigrations
python manage.py migrate
```

### 5. Iniciar servidores
```bash
# Terminal 1 - API
cd taskflow-api
python manage.py runserver 8000

# Terminal 2 - Web
cd taskflow_web
python manage.py runserver 9000
```

## 🌐 Acceso a la Aplicación

- **Frontend**: http://localhost:9000
- **API**: http://localhost:8000/api
- **Admin API**: http://localhost:8000/admin
- **Admin Web**: http://localhost:9000/admin
- **Documentación API**: http://localhost:8000/api/docs/

## 🧪 Usuarios de Prueba

Por defecto, el sistema incluye estos usuarios para pruebas:

- **admin@taskflow.com** (ID: 1) - Administrador
- **lugo@taskflow.com** (ID: 7) - Usuario regular

## ⚠️ Troubleshooting

### Problemas Comunes

1. **Error CORS**: Asegúrate que la API esté corriendo en el puerto 8000
2. **Error 404**: Verifica que `API_BASE_URL` esté configurado correctamente
3. **Error de autenticación**: Reinicia los servidores después de configurar .env

### Comandos Útiles

```bash
# Verificar instalación
python --version
pip list

# Limpiar migraciones
python manage.py makemigrations --empty
python manage.py migrate --fake

# Crear superusuario sin prompts
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@taskflow.com', 'admin123')" | python manage.py shell
```

## 🎯 Primeros Pasos

1. **Regístrate** en http://localhost:9000/auth/register/
2. **Inicia sesión** en http://localhost:9000/auth/login/
3. **Crea un proyecto** desde el dashboard
4. **Agrega miembros** usando el selector de usuarios
5. **Explora las funcionalidades** disponibles

¡Listo! 🚀 Tu TaskFlow está funcionando.
