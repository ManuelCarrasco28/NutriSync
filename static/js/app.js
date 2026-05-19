// static/js/app.js
// Funciones globales de NutriSync: modales, carga AJAX de formularios/detalles.

// ─── Modal ──────────────────────────────────────────────────────────────────

function openModal(title) {
    const overlay = document.getElementById('modal-overlay');
    const container = document.getElementById('modal-container');
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-content').innerHTML = `
        <div class="flex items-center justify-center py-12 text-slate-400">
            <i data-lucide="loader" class="w-6 h-6 animate-spin"></i>
            <span class="ml-2 text-sm">Cargando...</span>
        </div>`; // sourcery skip: javascript.browser.security.insecure-innerhtml
    overlay.classList.remove('hidden');
    overlay.classList.add('flex');
    // Animación de entrada
    requestAnimationFrame(() => {
        container.classList.remove('scale-95', 'opacity-0');
        container.classList.add('scale-100', 'opacity-100');
    });
    // Bloquear scroll del body
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    const overlay = document.getElementById('modal-overlay');
    const container = document.getElementById('modal-container');
    // Animación de salida
    container.classList.add('scale-95', 'opacity-0');
    container.classList.remove('scale-100', 'opacity-100');
    setTimeout(() => {
        overlay.classList.add('hidden');
        overlay.classList.remove('flex');
    }, 200);
    // Restaurar scroll
    document.body.style.overflow = '';
}

function setModalContent(html) {
    document.getElementById('modal-content').innerHTML = html; // sourcery skip: javascript.browser.security.insecure-innerhtml
    // Re-inicializar los iconos de Lucide para el contenido nuevo
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

// ─── Carga de formulario (Nuevo / Editar) ──────────────────────────────────

async function openModalNuevo() {
    openModal('Nuevo Paciente');
    await loadFormContent('/pacientes/nuevo/?fragment=1');
}

async function openModalEditar(pk) {
    openModal('Editar Paciente');
    await loadFormContent(`/pacientes/${pk}/editar/?fragment=1`);
}

async function loadFormContent(url) {
    try {
        const resp = await fetch(url);
        const html = await resp.text();

        // Extraer el fragmento del form del HTML
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const formContent = doc.getElementById('paciente-form-content');

        if (formContent) {
            setModalContent(formContent.outerHTML); // sourcery skip: javascript.browser.security.insecure-innerhtml
            // Guardar la URL base (sin ?fragment=1) como acción del form.
            // form.action="" fallaría a window.location.href (la lista, que no acepta POST).
            const actionUrl = url.split('?')[0];
            const form = document.getElementById('paciente-form');
            if (form) form.dataset.actionUrl = actionUrl;
            // Vincular el evento submit del formulario para envío AJAX
            bindFormSubmit();
        } else {
            setModalContent(`<p class="text-red-500">Error al cargar el formulario.</p>`);
        }
    } catch (err) {
        setModalContent(`<p class="text-red-500">Error de conexión: ${err.message}</p>`);
    }
}

function bindFormSubmit() {
    const form = document.getElementById('paciente-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<i data-lucide="loader" class="w-4 h-4 animate-spin"></i> Guardando...`; // sourcery skip: javascript.browser.security.insecure-innerhtml

        try {
            const formData = new FormData(form);
            // Usar la URL de acción guardada en data-action-url (seteada en loadFormContent).
            // form.action="" no sirve porque apunta a la página actual (lista de pacientes).
            const actionUrl = form.dataset.actionUrl;
            const resp = await fetch(actionUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
            });

            if (resp.ok) {
                const html = await resp.text();
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');

                // Si el formulario re-renderizado tiene errores, actualizar el modal
                const formContent = doc.getElementById('paciente-form-content');
                if (formContent) {
                    setModalContent(formContent.outerHTML); // sourcery skip: javascript.browser.security.insecure-innerhtml
                    bindFormSubmit();
                } else {
                    // Si no hay form, asumimos éxito — cerrar y refrescar
                    closeModal();
                    refreshListaPacientes();
                }
            } else {
                setModalContent(`<p class="text-red-500">Error del servidor (${resp.status}).</p>`);
            }
        } catch (err) {
            setModalContent(`<p class="text-red-500">Error de conexión: ${err.message}</p>`);
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    });
}

// ─── Carga de detalle ───────────────────────────────────────────────────────

async function openModalDetalle(pk) {
    openModal(`Ficha de Paciente`);
    try {
        const resp = await fetch(`/pacientes/${pk}/?fragment=1`);
        const html = await resp.text();

        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const detailContent = doc.getElementById('paciente-detail-content');

        if (detailContent) {
            setModalContent(detailContent.outerHTML); // sourcery skip: javascript.browser.security.insecure-innerhtml
        } else {
            setModalContent(`<p class="text-red-500">Error al cargar los datos del paciente.</p>`);
        }
    } catch (err) {
        setModalContent(`<p class="text-red-500">Error de conexión: ${err.message}</p>`);
    }
}

// ─── Toggle estado (desde modal o desde lista) ──────────────────────────────

async function toggleEstado(pk) {
    try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || window.CSRF_TOKEN || '';

        const resp = await fetch(`/pacientes/${pk}/toggle/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken || '',
                'X-Requested-With': 'XMLHttpRequest',
            },
        });

        if (resp.ok || resp.redirected) {
            // Recargar el contenido del modal si está abierto, o refrescar lista
            const overlay = document.getElementById('modal-overlay');
            if (!overlay.classList.contains('hidden')) {
                await openModalDetalle(pk);
            } else {
                refreshListaPacientes();
            }
        }
    } catch (err) {
        console.error('Error al cambiar estado:', err);
    }
}

// ─── Refrescar lista de pacientes (recarga la tabla sin recargar la página) ─

let refreshCounter = 0;
async function refreshListaPacientes() {
    // Guardar query params actuales de búsqueda/filtro
    const urlParams = new URLSearchParams(window.location.search);
    refreshCounter++;
    urlParams.set('_refresh', refreshCounter);
    const url = `/pacientes/?${urlParams.toString()}`;

    try {
        const resp = await fetch(url);
        const html = await resp.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');

        // Reemplazar solo la tabla y la paginación
        const newTable = doc.querySelector('#pacientes-table-body');
        const newPagination = doc.querySelector('#pacientes-pagination');
        const newCounts = doc.querySelector('#pacientes-counts');

        const oldTable = document.getElementById('pacientes-table-body');
        const oldPagination = document.getElementById('pacientes-pagination');
        const oldCounts = document.getElementById('pacientes-counts');

        if (oldTable && newTable) oldTable.outerHTML = newTable.outerHTML; // sourcery skip: javascript.browser.security.insecure-innerhtml
        if (oldPagination && newPagination) oldPagination.outerHTML = newPagination.outerHTML; // sourcery skip: javascript.browser.security.insecure-innerhtml
        if (oldCounts && newCounts) oldCounts.outerHTML = newCounts.outerHTML; // sourcery skip: javascript.browser.security.insecure-innerhtml

        if (typeof lucide !== 'undefined') lucide.createIcons();
    } catch (err) {
        console.error('Error al refrescar lista:', err);
        // Fallback: recargar página completa
        location.reload();
    }
}

// ─── Inicialización al cargar la página ─────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
});
