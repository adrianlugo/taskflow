// Funciones para gestión de miembros del proyecto

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

function deleteProject(id) {
    if (confirm('¿Estás seguro de que quieres eliminar este proyecto? Esta acción no se puede deshacer.')) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/projects/${id}/delete/`;

        const csrf = document.createElement('input');
        csrf.type = 'hidden';
        csrf.name = 'csrfmiddlewaretoken';
        csrf.value = getCookie('csrftoken');
        form.appendChild(csrf);

        document.body.appendChild(form);
        form.submit();
    }
}

// Refrescar token si es necesario
async function refreshToken() {
    const refreshToken = sessionStorage.getItem('refresh') || getCookie('refresh');
    
    if (!refreshToken) {
        console.log('No hay refresh token');
        return null;
    }
    
    try {
        const response = await fetch('http://127.0.0.1:8000/api/auth/refresh/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh: refreshToken })
        });
        
        if (response.ok) {
            const data = await response.json();
            const newAccessToken = data.access;
            
            // Actualizar tokens
            sessionStorage.setItem('access', newAccessToken);
            document.cookie = `access=${newAccessToken}; path=/`;
            
            console.log('Token refrescado exitosamente');
            return newAccessToken;
        } else {
            console.error('Error refrescando token');
            return null;
        }
    } catch (error) {
        console.error('Error en refresh:', error);
        return null;
    }
}

// Cargar usuarios cuando se abre el modal
async function loadUsers(projectId) {
    try {
        console.log('Cargando usuarios para proyecto:', projectId);
        
        // Obtener el token de la sesión - EXACTAMENTE COMO EN addMember y removeMember
        let token = sessionStorage.getItem('access') || getCookie('access');
        console.log('Token encontrado:', !!token);
        console.log('Token completo:', token ? token.substring(0, 50) + '...' : 'null');
        
        if (!token) {
            console.error('No se encontró token de acceso');
            return;
        }
        
        // Intentar la llamada original
        let response = await fetch(`http://127.0.0.1:8000/api/projects/${projectId}/members/list/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token
            }
        });
        
        // Si el token expiró (401), intentar refrescarlo
        if (response.status === 401) {
            console.log('Token expirado, intentando refrescar...');
            token = await refreshToken();
            
            if (!token) {
                console.error('No se pudo refrescar el token');
                return;
            }
            
            // Reintentar con el nuevo token
            response = await fetch(`http://127.0.0.1:8000/api/projects/${projectId}/members/list/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + token
                }
            });
        }
        
        console.log('Respuesta status:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Datos recibidos:', data);
        
        if (data.success) {
            const userSelect = document.getElementById('userSelect');
            userSelect.innerHTML = '<option value="">Selecciona un usuario...</option>';
            
            if (data.users && data.users.length > 0) {
                data.users.forEach(user => {
                    const option = document.createElement('option');
                    option.value = user.id;
                    option.textContent = `${user.username} (${user.email})`;
                    userSelect.appendChild(option);
                });
                console.log('Usuarios cargados:', data.users.length);
            } else {
                console.log('No se encontraron usuarios');
                userSelect.innerHTML = '<option value="">No hay usuarios disponibles</option>';
            }
            
            // Habilitar botón cuando se selecciona un usuario
            userSelect.addEventListener('change', function() {
                const addBtn = document.getElementById('addMemberBtn');
                addBtn.disabled = !this.value;
            });
        } else {
            console.error('Error cargando usuarios:', data.error);
            const userSelect = document.getElementById('userSelect');
            userSelect.innerHTML = `<option value="">Error: ${data.error || 'Error desconocido'}</option>`;
        }
    } catch (error) {
        console.error('Error en loadUsers:', error);
        const userSelect = document.getElementById('userSelect');
        userSelect.innerHTML = '<option value="">Error de conexión</option>';
    }
}

// Filtrar usuarios
function filterUsers() {
    const filter = document.getElementById('userFilter').value.toLowerCase();
    const userSelect = document.getElementById('userSelect');
    const options = userSelect.getElementsByTagName('option');
    
    for (let option of options) {
        const text = option.textContent.toLowerCase();
        const value = option.value.toLowerCase();
        
        if (text.includes(filter) || value.includes(filter)) {
            option.style.display = '';
        } else {
            option.style.display = 'none';
        }
    }
}

// Agregar miembro al proyecto
function addMember(projectId, userId) {
    // Validar parámetros
    if (!projectId || !userId) {
        console.error('❌ Error: projectId o userId son undefined');
        console.log('projectId:', projectId, 'userId:', userId);
        alert('Error: Faltan datos para agregar el miembro');
        return;
    }
    
    console.log('=== AGREGAR MIEMBRO ===');
    console.log('Agregando miembro:', userId, 'al proyecto:', projectId);
    
    // Obtener el token de la sesión - EXACTAMENTE COMO EN LA CONSOLA
    const token = sessionStorage.getItem('access') || getCookie('access');
    console.log('Token encontrado:', !!token);
    
    if (!token) {
        console.error('No se encontró token de acceso');
        alert('Error de autenticación. Por favor inicia sesión nuevamente.');
        return;
    }
    
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    };
    
    console.log('Headers:', headers);
    
    fetch(`http://127.0.0.1:8000/api/projects/${projectId}/members/`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({ user_id: userId })
    })
    .then(response => {
        console.log('Respuesta status addMember:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Respuesta addMember data:', data);
        // La API responde con {message: '...'} en lugar de {success: true, message: '...'}
        if (data.message && data.message.includes('exitosamente')) {
            // Guardar mensaje en sessionStorage para mostrar después de la recarga
            sessionStorage.setItem('successMessage', data.message);
            
            // Recargar página inmediatamente
            console.log('✅ Recargando página inmediatamente...');
            window.location.reload();
        } else {
            // Mostrar error
            const alert = document.createElement('div');
            alert.className = 'alert alert-danger alert-dismissible fade show';
            alert.innerHTML = `
                Error: ${data.error}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            // Buscar un lugar seguro para mostrar el alert
            const targetContainer = document.querySelector('.container-fluid') || 
                                        document.querySelector('.container') || 
                                        document.querySelector('main') ||
                                        document.body;
            
            targetContainer.prepend(alert);
            console.log('Alert de error agregado a:', targetContainer.className || 'body');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al agregar miembro');
    });
}

// Eliminar miembro del proyecto
function removeMember(projectId, userId, username) {
    // Validar parámetros
    if (!projectId || !userId || !username) {
        console.error('❌ Error: Faltan parámetros');
        console.log('projectId:', projectId, 'userId:', userId, 'username:', username);
        alert('Error: Faltan datos para eliminar el miembro');
        return;
    }
    
    if (confirm(`¿Estás seguro de que quieres eliminar a ${username} del proyecto?`)) {
        console.log('=== ELIMINAR MIEMBRO ===');
        console.log('Eliminando miembro:', userId, 'del proyecto:', projectId);
        
        // Obtener el token de la sesión - EXACTAMENTE COMO EN LA CONSOLA
        const token = sessionStorage.getItem('access') || getCookie('access');
        console.log('Token para eliminar:', !!token);
        
        if (!token) {
            console.error('No se encontró token de acceso');
            alert('Error de autenticación. Por favor inicia sesión nuevamente.');
            return;
        }
        
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        };
        
        console.log('Headers para eliminar:', headers);
        
        const url = `http://127.0.0.1:8000/api/projects/${projectId}/members/${userId}/`;
        console.log('Haciendo DELETE a:', url);
        
        fetch(url, {
            method: 'DELETE',
            headers: headers
        })
        .then(response => {
            console.log('Respuesta DELETE status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Respuesta DELETE data:', data);
            // La API responde con {message: '...'} en lugar de {success: true, message: '...'}
            if (data.message && data.message.includes('exitosamente')) {
                // Guardar mensaje en sessionStorage para mostrar después de la recarga
                sessionStorage.setItem('successMessage', data.message);
                
                // Recargar página inmediatamente
                console.log('✅ Recargando página inmediatamente...');
                window.location.reload();
            } else {
                // Mostrar error
                const alert = document.createElement('div');
                alert.className = 'alert alert-danger alert-dismissible fade show';
                alert.innerHTML = `
                    Error: ${data.error}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                `;
                
                // Buscar un lugar seguro para mostrar el alert
                const targetContainer = document.querySelector('.container-fluid') || 
                                            document.querySelector('.container') || 
                                            document.querySelector('main') ||
                                            document.body;
                
                targetContainer.prepend(alert);
                console.log('Alert de error de eliminación agregado a:', targetContainer.className || 'body');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al eliminar miembro');
        });
    }
}

// Inicializar event listeners cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function () {
    // Mostrar mensaje de éxito si existe en sessionStorage (después de recarga)
    const successMessage = sessionStorage.getItem('successMessage');
    if (successMessage) {
        // Eliminar el mensaje del sessionStorage para que no aparezca de nuevo
        sessionStorage.removeItem('successMessage');
        
        // Mostrar el mensaje con el estilo de Django
        const alert = document.createElement('div');
        alert.className = 'alert alert-success alert-dismissible fade show';
        alert.setAttribute('role', 'alert');
        alert.innerHTML = `
            ${successMessage}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Buscar el contenedor de mensajes de Django o crear uno
        let messagesContainer = document.querySelector('.messages-container');
        if (!messagesContainer) {
            // Crear contenedor de mensajes si no existe
            messagesContainer = document.createElement('div');
            messagesContainer.className = 'messages-container mb-3';
            
            // Insertar después del navbar o al principio del contenido
            const navbar = document.querySelector('.navbar');
            const mainContent = document.querySelector('main') || 
                               document.querySelector('.container-fluid') ||
                               document.querySelector('.container');
            
            if (navbar && navbar.nextSibling) {
                navbar.parentNode.insertBefore(messagesContainer, navbar.nextSibling);
            } else if (mainContent && mainContent.firstChild) {
                mainContent.insertBefore(messagesContainer, mainContent.firstChild);
            } else {
                document.body.insertBefore(messagesContainer, document.body.firstChild);
            }
        }
        
        messagesContainer.appendChild(alert);
        console.log('✅ Mensaje de éxito mostrado después de la recarga');
        
        // Eliminar el mensaje automáticamente después de 5 segundos
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
                console.log('✅ Mensaje eliminado automáticamente después de 5 segundos');
            }
        }, 5000);
    }

    // Project member management
    const projectRow = document.querySelector('[data-project-id]');
    if (!projectRow) {
        console.log("No hay projectId en esta página. Script de miembros desactivado.");
        return; // Detiene el script en páginas donde no hay proyecto
    }

    const projectId = projectRow.dataset.projectId;
    console.log("projectId encontrado:", projectId);

    // Modal para agregar miembros
    const addMemberModal = document.getElementById("addMemberModal"); 
    if (addMemberModal) { 
        addMemberModal.addEventListener("show.bs.modal", function () { 
            console.log("🔥 Modal abierto correctamente"); 
            loadUsers(projectId); 
        }); 
    }

    // Botón para agregar miembro
    const addMemberBtn = document.getElementById('addMemberBtn');
    if (addMemberBtn) {
        addMemberBtn.addEventListener('click', function (event) {
            event.preventDefault(); // Evitar submit del formulario
            const userId = document.getElementById('userSelect').value;
            
            if (userId) {
                addMember(projectId, userId);
            } else {
                alert('Por favor selecciona un usuario');
            }
        });
    }

    // Event listener para el filtro
    const userFilter = document.getElementById('userFilter');
    if (userFilter) {
        userFilter.addEventListener('input', filterUsers);
    }

    // Botones para eliminar miembros
    const removeMemberBtns = document.querySelectorAll('.js-remove-member');
    removeMemberBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            const userId = btn.dataset.userId;      // ID numérico
            const username = btn.dataset.username; // Username para mostrar
            
            removeMember(projectId, userId, username);
        });
    });

    // Botón eliminar proyecto
    const btn = document.querySelector('.js-delete-project');
    if (btn) {
        btn.addEventListener('click', function () {
            deleteProject(btn.dataset.projectId);
        });
    }
});
