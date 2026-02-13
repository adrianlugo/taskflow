// Funciones para gestion de miembros del proyecto

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
    return null;
}

async function parseJsonSafe(response) {
    try {
        return await response.json();
    } catch (error) {
        return null;
    }
}

function showProjectMessage(type, text) {
    let container = document.getElementById("projectMessages");
    if (!container) {
        container = document.createElement("div");
        container.id = "projectMessages";
        const projectRow = document.querySelector("[data-project-id]");
        if (projectRow && projectRow.parentNode) {
            projectRow.parentNode.insertBefore(container, projectRow);
        } else {
            document.body.prepend(container);
        }
    }

    const alert = document.createElement("div");
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.setAttribute("role", "alert");
    alert.innerHTML = `
        ${text}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    container.prepend(alert);
}

function deleteProject(id) {
    if (confirm("Estas seguro de que quieres eliminar este proyecto? Esta accion no se puede deshacer.")) {
        const form = document.createElement("form");
        form.method = "POST";
        form.action = `/projects/${id}/delete/`;

        const csrf = document.createElement("input");
        csrf.type = "hidden";
        csrf.name = "csrfmiddlewaretoken";
        csrf.value = getCookie("csrftoken");
        form.appendChild(csrf);

        document.body.appendChild(form);
        form.submit();
    }
}

// Cargar usuarios cuando se abre el modal
async function loadUsers(projectId) {
    const userSelect = document.getElementById("userSelect");
    const addBtn = document.getElementById("addMemberBtn");
    if (!userSelect) return;

    userSelect.innerHTML = '<option value="">Cargando usuarios...</option>';
    userSelect.disabled = true;
    if (addBtn) addBtn.disabled = true;

    try {
        const response = await fetch(`/projects/${projectId}/members/`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
            },
        });

        const data = await parseJsonSafe(response);
        if (!response.ok || !data) {
            throw new Error(`HTTP error ${response.status}`);
        }

        if (!data.success) {
            userSelect.innerHTML = `<option value="">Error: ${data.error || "Error desconocido"}</option>`;
            return;
        }

        userSelect.innerHTML = '<option value="">Selecciona un usuario...</option>';

        if (Array.isArray(data.users) && data.users.length > 0) {
            data.users.forEach((user) => {
                const option = document.createElement("option");
                option.value = user.id;
                option.textContent = `${user.username} (${user.email})`;
                userSelect.appendChild(option);
            });
            userSelect.disabled = false;
        } else {
            userSelect.innerHTML = '<option value="">No hay usuarios disponibles</option>';
        }

        // Evitar listeners duplicados cada vez que se abre el modal.
        userSelect.onchange = function () {
            if (addBtn) addBtn.disabled = !this.value;
        };
    } catch (error) {
        console.error("Error en loadUsers:", error);
        userSelect.innerHTML = '<option value="">Error de conexion</option>';
    }
}

// Filtrar usuarios
function filterUsers() {
    const filterInput = document.getElementById("userFilter");
    const userSelect = document.getElementById("userSelect");
    if (!filterInput || !userSelect) return;

    const filter = filterInput.value.toLowerCase();
    const options = userSelect.getElementsByTagName("option");

    for (const option of options) {
        const text = option.textContent.toLowerCase();
        const value = option.value.toLowerCase();
        option.style.display = text.includes(filter) || value.includes(filter) ? "" : "none";
    }
}

// Agregar miembro al proyecto
function addMember(projectId, userId) {
    if (!projectId || !userId) {
        showProjectMessage("danger", "Error: Faltan datos para agregar el miembro.");
        return;
    }

    if (!confirm("Agregar este miembro al proyecto?")) {
        return;
    }

    const formData = new FormData();
    formData.append("user_id", userId);
    formData.append(
        "csrfmiddlewaretoken",
        getCookie("csrftoken") || document.querySelector('[name="csrfmiddlewaretoken"]')?.value
    );

    fetch(`/projects/${projectId}/members/`, {
        method: "POST",
        body: formData,
    })
        .then(async (response) => {
            const data = await parseJsonSafe(response);
            return {
                ok: response.ok,
                data: data || {},
            };
        })
        .then(({ ok, data }) => {
            // En ambos casos (ok/error) el backend deja messages de Django.
            // Recargamos para mostrarlos en el mismo bloque de mensajes de la web.
            if (ok && data?.success) {
                window.location.reload();
                return;
            }
            window.location.reload();
        })
        .catch((error) => {
            console.error("Error:", error);
            showProjectMessage("danger", `Error al agregar miembro: ${error.message}`);
        });
}

// Eliminar miembro del proyecto
function removeMember(projectId, userId, username) {
    if (!projectId || !userId || !username) {
        showProjectMessage("danger", "Error: Faltan datos para eliminar el miembro.");
        return;
    }

    if (!confirm(`Estas seguro de que quieres eliminar a ${username} del proyecto?`)) {
        return;
    }

    const formData = new FormData();
    formData.append(
        "csrfmiddlewaretoken",
        getCookie("csrftoken") || document.querySelector('[name="csrfmiddlewaretoken"]')?.value
    );

    fetch(`/projects/${projectId}/members/${userId}/`, {
        method: "POST",
        body: formData,
    })
        .then(async (response) => {
            const data = await parseJsonSafe(response);
            return {
                ok: response.ok,
                data: data || {},
            };
        })
        .then(({ ok, data }) => {
            // En ambos casos (ok/error) el backend deja messages de Django.
            // Recargamos para mostrarlos en el mismo bloque de mensajes de la web.
            if (ok && data?.success) {
                window.location.reload();
                return;
            }
            window.location.reload();
        })
        .catch((error) => {
            console.error("Error:", error);
            showProjectMessage("danger", `Error al eliminar miembro: ${error.message}`);
        });
}

// Inicializar event listeners cuando el DOM este listo
document.addEventListener("DOMContentLoaded", function () {
    const projectRow = document.querySelector("[data-project-id]");
    if (!projectRow) {
        return;
    }

    const projectId = projectRow.dataset.projectId;

    const addMemberModal = document.getElementById("addMemberModal");
    if (addMemberModal) {
        addMemberModal.addEventListener("show.bs.modal", function () {
            loadUsers(projectId);
        });
    }

    const addMemberBtn = document.getElementById("addMemberBtn");
    if (addMemberBtn) {
        addMemberBtn.addEventListener("click", function (event) {
            event.preventDefault();
            const userId = document.getElementById("userSelect")?.value;

            if (userId) {
                addMember(projectId, userId);
            } else {
                showProjectMessage("warning", "Por favor selecciona un usuario.");
            }
        });
    }

    const userFilter = document.getElementById("userFilter");
    if (userFilter) {
        userFilter.addEventListener("input", filterUsers);
    }

    const removeMemberBtns = document.querySelectorAll(".js-remove-member");
    removeMemberBtns.forEach((btn) => {
        btn.addEventListener("click", function () {
            const userId = btn.dataset.userId;
            const username = btn.dataset.username;
            removeMember(projectId, userId, username);
        });
    });

    const deleteBtn = document.querySelector(".js-delete-project");
    if (deleteBtn) {
        deleteBtn.addEventListener("click", function () {
            deleteProject(deleteBtn.dataset.projectId);
        });
    }
});
