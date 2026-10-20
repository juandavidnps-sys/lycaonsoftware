/**
 * ╔══════════════════════════════════════════════════════════╗
 * ║       LYCAON SOFTWARE — JavaScript Principal               ║
 * ║   Maneja toda la interactividad del frontend            ║
 * ║   Sin frameworks, solo JS limpio y comentado            ║
 * ╚══════════════════════════════════════════════════════════╝
 */

/* ══════════════════════════════════════════
   1. NAVBAR — Efecto scroll glassmorphic & menú móvil
   ══════════════════════════════════════════ */

(function initNavbar() {
  const navbar = document.getElementById('main-navbar');
  if (!navbar) return;

  // Cuando el usuario scrollea más de 40px, agrega la clase "scrolled"
  window.addEventListener('scroll', function () {
    if (window.scrollY > 40) {
      navbar.classList.add('scrolled', 'glass-nav');
    } else {
      navbar.classList.remove('scrolled', 'glass-nav');
    }
  }, { passive: true });

  // Control del menú hamburguesa en landing page
  const landingToggle = document.getElementById('landing-menu-toggle');
  const landingMenu = document.getElementById('landing-mobile-menu');
  if (landingToggle && landingMenu) {
    landingToggle.addEventListener('click', function () {
      landingMenu.classList.toggle('hidden');
    });
  }
})();

/* ══════════════════════════════════════════
   2. SIDEBAR — Gestión delegada a siam-interactions.js
   ══════════════════════════════════════════ */
// La interactividad avanzada del sidebar (colapso, persistencia y animaciones SVG)
// es administrada de forma centralizada por siam-interactions.js.

/* ══════════════════════════════════════════
   3. MODALES — Abrir / Cerrar
   ══════════════════════════════════════════ */

/**
 * Abre un modal por su ID
 * @param {string} modalId - ID del elemento .modal-overlay
 */
function abrirModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('open');
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden'; // Bloquea el scroll del fondo
    const box = modal.querySelector('.modal-box');
    if (box) {
      setTimeout(() => {
        box.classList.remove('scale-95', 'opacity-0');
        box.classList.add('scale-100', 'opacity-100');
      }, 10);
    }
  }
}

/**
 * Cierra un modal por su ID
 * @param {string} modalId - ID del elemento .modal-overlay
 */
function cerrarModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    const box = modal.querySelector('.modal-box');
    if (box) {
      box.classList.remove('scale-100', 'opacity-100');
      box.classList.add('scale-95', 'opacity-0');
    }
    modal.classList.remove('open');
    modal.classList.add('hidden');
    modal.style.display = 'none';
    document.body.style.overflow = '';
  }
}

window.abrirModal = abrirModal;
window.cerrarModal = cerrarModal;

// Cerrar modal al hacer clic en el overlay (fuera del contenido)
document.addEventListener('click', function (e) {
  if (e.target.classList.contains('modal-overlay')) {
    cerrarModal(e.target.id);
  }
});

/* ══════════════════════════════════════════
   3b. HELPERS — mostrarError & mostrarToast
   ══════════════════════════════════════════ */

/**
 * Muestra un mensaje de error en un div dado
 * @param {HTMLElement} el - Elemento donde mostrar el error
 * @param {string} msg - Mensaje de error
 */
function mostrarError(el, msg) {
  if (!el) return;
  el.textContent = msg;
  el.style.display = 'block';
  // Ocultar después de 5 segundos
  setTimeout(function () {
    el.style.display = 'none';
  }, 5000);
}

/**
 * Muestra un toast flotante con animación glassmorphic
 * @param {string} msg - Mensaje a mostrar
 * @param {boolean} isError - Si es error (rojo) o éxito (verde)
 */
function mostrarToast(msg, isError) {
  // Eliminar toast anterior si existe
  var prev = document.getElementById('toast-notification');
  if (prev) prev.remove();

  var toast = document.createElement('div');
  toast.id = 'toast-notification';
  toast.className = 'toast-notification' + (isError ? ' toast-error' : ' toast-success');
  toast.textContent = msg;
  document.body.appendChild(toast);

  // Forzar reflow para que la animación se active
  toast.offsetHeight;
  toast.classList.add('toast-visible');

  // Auto-cerrar después de 3.5 segundos
  setTimeout(function () {
    toast.classList.remove('toast-visible');
    setTimeout(function () { toast.remove(); }, 400);
  }, 3500);
}

/* ══════════════════════════════════════════
   4. AUTENTICACIÓN — Login y Registro
   ══════════════════════════════════════════ */

(function initAuthForms() {
  const loginForm    = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');
  const toggleBtns   = document.querySelectorAll('.form-toggle button');
  const loginCard    = document.getElementById('login-card');
  const registerCard = document.getElementById('register-card');

  // Alternar entre login y registro
  if (toggleBtns.length > 0 && loginCard && registerCard) {
    toggleBtns.forEach(btn => {
      btn.addEventListener('click', function () {
        const isLogin = loginCard.style.display !== 'none';
        loginCard.style.display    = isLogin ? 'none' : 'block';
        registerCard.style.display = isLogin ? 'block' : 'none';
      });
    });
  }

  // ── Manejo del formulario de Login ──
  if (loginForm) {
    loginForm.addEventListener('submit', async function (e) {
      e.preventDefault(); // Evita que la página se recargue

      const email    = document.getElementById('login-email').value.trim();
      const password = document.getElementById('login-password').value;
      const btn      = document.getElementById('login-btn');
      const errorDiv = document.getElementById('login-error');

      // Validación básica
      if (!email || !password) {
        mostrarError(errorDiv, 'Llena todos los campos.');
        return;
      }

      // Estado de carga
      btn.disabled = true;
      btn.innerHTML = '<span class="loader-spin">⟳</span> Verificando...';

      try {
        // Llamada a la API de login en Flask
        const respuesta = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });

        const datos = await respuesta.json();

        if (datos.success) {
          // Login exitoso → redirigir al dashboard
          // Flask ya creó la cookie de sesión del lado del servidor
          window.location.href = '/dashboard';
        } else {
          mostrarError(errorDiv, datos.error || 'Credenciales inválidas.');
          btn.disabled = false;
          btn.innerHTML = 'Ingresar Sistema →';
        }
      } catch (err) {
        mostrarError(errorDiv, 'Error de conexión. Intenta de nuevo.');
        btn.disabled = false;
        btn.innerHTML = 'Ingresar Sistema →';
      }
    });
  }

  // ── Manejo del formulario de Registro ──
  if (registerForm) {
    registerForm.addEventListener('submit', async function (e) {
      e.preventDefault();

      const nombre   = document.getElementById('reg-name').value.trim();
      const email    = document.getElementById('reg-email').value.trim();
      const password = document.getElementById('reg-password').value;
      const phone    = document.getElementById('reg-phone')?.value.trim() || '';
      const address  = document.getElementById('reg-address')?.value.trim() || '';
      const btn      = document.getElementById('register-btn');
      const errorDiv = document.getElementById('register-error');

      if (!nombre || !email || !password || !phone || !address) {
        mostrarError(errorDiv, 'Llena todos los campos.');
        return;
      }

      btn.disabled = true;
      btn.innerHTML = '<span>Procesando...</span>';

      try {
        const respuesta = await fetch('/api/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password, name: nombre, phone, address })
        });

        const datos = await respuesta.json();

        if (datos.success) {
          window.location.href = '/dashboard';
        } else {
          mostrarError(errorDiv, datos.error || 'Error al registrar.');
          btn.disabled = false;
          btn.innerHTML = 'Solicitar Acceso';
        }
      } catch (err) {
        mostrarError(errorDiv, 'Error de conexión.');
        btn.disabled = false;
        btn.innerHTML = 'Solicitar Acceso';
      }
    });
  }
})();

/* ══════════════════════════════════════════
   4.5. ADMIN — Crear Usuario
   ══════════════════════════════════════════ */
(function initAdminUsers() {
  const createUserForm = document.getElementById('create-user-form');
  if (createUserForm) {
    createUserForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      
      const name = document.getElementById('new-user-name').value.trim();
      const email = document.getElementById('new-user-email').value.trim();
      const password = document.getElementById('new-user-password')?.value || '';
      const role = document.getElementById('new-user-role').value;
      const btn = document.getElementById('btn-create-user');
      
      if (!name || !email || !role) {
        mostrarToast('Todos los campos son obligatorios', true);
        return;
      }
      
      btn.disabled = true;
      btn.textContent = 'Creando...';
      
      try {
        const respuesta = await fetch('/api/admin/users', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, email, role, password })
        });
        
        const datos = await respuesta.json();
        
        if (datos.success) {
          mostrarToast('Usuario creado correctamente en la base de datos', false);
          cerrarModal('new-user-modal');
          cerrarModal('modal-create-user');
          setTimeout(() => window.location.reload(), 1000);
        } else {
          mostrarToast(datos.error || 'Error al crear usuario', true);
          btn.disabled = false;
          btn.textContent = 'Generar Identidad';
        }
      } catch (err) {
        mostrarToast('Error de conexión con el servidor', true);
        btn.disabled = false;
        btn.textContent = 'Generar Identidad';
      }
    });
  }
})();

/* ══════════════════════════════════════════
   5. TIENDA — Filtros y compra de productos
   ══════════════════════════════════════════ */

(function initStore() {
  const filterBtns = document.querySelectorAll('.filter-btn');
  const productCards = document.querySelectorAll('.product-card');

  // ── Filtro por categoría ──
  filterBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      // Desactivar todos los filtros
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const categoria = (btn.dataset.categoria || 'todos').toLowerCase();
      let visibleCount = 0;

      // Mostrar/ocultar productos según la categoría seleccionada
      productCards.forEach(function (card) {
        const cardCat = (card.dataset.categoria || '').toLowerCase();
        let matches = (categoria === 'todos' || cardCat === categoria);

        // Alias inteligentes para categorías en español / sinónimos
        if (!matches) {
          if (categoria === 'choque' || categoria === 'seguridad') {
            matches = cardCat === 'hardware' || cardCat.includes('choque') || cardCat.includes('seguridad');
          } else if (categoria === 'quimico') {
            matches = cardCat === 'hardware' || cardCat.includes('quimico');
          } else if (categoria === 'monitoreo') {
            matches = cardCat === 'hardware' || cardCat === 'security' || cardCat.includes('monitoreo');
          } else if (categoria === 'seguridad') {
            matches = cardCat === 'security';
          } else if (categoria === 'redes') {
            matches = cardCat === 'network';
          } else if (categoria === 'servicios') {
            matches = cardCat === 'service';
          }
        }

        if (matches) {
          card.style.display = '';
          card.style.animation = 'siamFadeInUp 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards';
          visibleCount++;
        } else {
          card.style.display = 'none';
        }
      });

      // Manejo de estado vacío si la categoría no tiene items
      const grid = document.querySelector('.products-grid');
      let emptyMsg = document.getElementById('siam-store-empty-msg');
      if (visibleCount === 0) {
        if (!emptyMsg && grid) {
          emptyMsg = document.createElement('div');
          emptyMsg.id = 'siam-store-empty-msg';
          emptyMsg.className = 'col-span-full card-charcoal p-12 text-center my-6 flex flex-col items-center justify-center';
          emptyMsg.innerHTML = `
            <div class="w-12 h-12 rounded-full bg-gold/10 border border-gold/30 flex items-center justify-center text-gold mb-4">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path></svg>
            </div>
            <div class="text-lg font-bold text-white mb-1">Sin Equipos en esta Categoría</div>
            <p class="text-sm text-gray-400 mb-4">Actualmente no hay unidades disponibles para el filtro seleccionado.</p>
            <button class="btn-outline text-xs px-4 py-2" onclick="document.querySelector('.filter-btn[data-categoria=\\'todos\\']').click()">Restablecer Filtros</button>
          `;
          grid.appendChild(emptyMsg);
        } else if (emptyMsg) {
          emptyMsg.style.display = 'flex';
        }
      } else if (emptyMsg) {
        emptyMsg.style.display = 'none';
      }
    });
  });
})();

// Variables globales del modal de compra
let productoSeleccionado = null;

/**
 * Abre el modal de compra con los datos del producto
 * @param {string} id - ID del producto
 * @param {string} nombre - Nombre del producto
 * @param {number} precio - Precio unitario
 * @param {number} stock - Stock disponible
 */
function abrirModalCompra(id, nombre, precio, stock) {
  productoSeleccionado = { id, nombre, precio, stock };

  // Llenar el modal con los datos del producto
  document.getElementById('modal-product-name').textContent = nombre;
  document.getElementById('modal-product-price').textContent = `$${parseFloat(precio).toLocaleString('es-ES', { minimumFractionDigits: 2 })}`;

  const qtyInput = document.getElementById('modal-qty');
  qtyInput.value = 1;
  qtyInput.max   = stock;

  // Resetear mensajes
  document.getElementById('buy-result').textContent = '';
  document.getElementById('buy-result').className   = '';

  abrirModal('buy-modal');
  actualizarTotalModal();
}

/**
 * Actualiza el total mostrado en el modal según la cantidad
 */
function actualizarTotalModal() {
  if (!productoSeleccionado) return;
  const qty   = parseInt(document.getElementById('modal-qty').value) || 1;
  const total = productoSeleccionado.precio * qty;
  document.getElementById('modal-total').textContent =
    `$${total.toLocaleString('es-ES', { minimumFractionDigits: 2 })}`;
}

// Escuchar cambios en la cantidad del modal
document.addEventListener('DOMContentLoaded', function () {
  const qtyInput = document.getElementById('modal-qty');
  if (qtyInput) {
    qtyInput.addEventListener('input', actualizarTotalModal);
  }
});

/**
 * Confirma y envía la orden de compra rápida al servidor Flask
 */
async function confirmarCompra() {
  if (!productoSeleccionado) return;

  const qty    = parseInt(document.getElementById('modal-qty').value) || 1;
  const btn    = document.getElementById('confirm-buy-btn');
  const result = document.getElementById('buy-result');

  btn.disabled = true;
  btn.textContent = 'Procesando...';

  try {
    const respuesta = await fetch('/api/orders', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        product_id: productoSeleccionado.id,
        cantidad:   qty
      })
    });

    const datos = await respuesta.json();

    if (datos.success) {
      cerrarModal('buy-modal');
      mostrarFacturaExitosa(datos);
    } else {
      result.textContent = datos.error || 'Error al procesar el pedido.';
      result.className   = 'text-rose-400 p-2 rounded bg-rose-500/10 border border-rose-500/30';
      btn.disabled = false;
      btn.textContent = 'Autorizar y Facturar';
    }
  } catch (err) {
    result.textContent = 'Error de conexión con el servidor.';
    result.className   = 'text-rose-400 p-2 rounded bg-rose-500/10 border border-rose-500/30';
    btn.disabled = false;
    btn.textContent = 'Autorizar y Facturar';
  }
}

/* ══════════════════════════════════════════
   6. ACTIVIDAD — Filtro en tiempo real
   ══════════════════════════════════════════ */

(function initActivityFilter() {
  const searchInput = document.getElementById('activity-search');
  if (!searchInput) return;

  searchInput.addEventListener('input', function () {
    const termino = this.value.toLowerCase().trim();
    const items   = document.querySelectorAll('.log-item');

    items.forEach(function (item) {
      const texto = item.textContent.toLowerCase();
      item.style.display = texto.includes(termino) ? '' : 'none';
    });
  });
})();

/* ══════════════════════════════════════════
   7. USUARIOS — Cambio de rol y eliminación
   ══════════════════════════════════════════ */

/**
 * Cambia el rol de un usuario (admin ↔ cliente)
 * @param {string} userId - ID del usuario
 * @param {string} nuevoRol - "administrador" o "cliente"
 */
async function cambiarRol(userId, nuevoRol) {
  if (!confirm(`¿Cambiar rol a "${nuevoRol}"?`)) return;

  try {
    const res = await fetch(`/api/users/${userId}/role`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role: nuevoRol })
    });
    const datos = await res.json();

    if (datos.success) {
      mostrarToast('Rol actualizado correctamente.');
      setTimeout(() => window.location.reload(), 1000);
    } else {
      mostrarToast('' + (datos.error || 'Error al cambiar rol.'), true);
    }
  } catch {
    mostrarToast('Error de conexión.', true);
  }
}

/**
 * Elimina un usuario del sistema
 * @param {string} userId - ID del usuario a eliminar
 * @param {string} nombre - Nombre para confirmar
 */
async function eliminarUsuario(userId, nombre) {
  if (!confirm(`¿Eliminar al usuario "${nombre}"? Esta acción no se puede deshacer.`)) return;

  try {
    const res = await fetch(`/api/users/${userId}`, { method: 'DELETE' });
    const datos = await res.json();

    if (datos.success) {
      mostrarToast('Usuario eliminado.');
      // Eliminar la fila de la tabla sin recargar la página
      const fila = document.getElementById(`user-row-${userId}`);
      if (fila) fila.remove();
    } else {
      mostrarToast('' + (datos.error || 'Error al eliminar.'), true);
    }
  } catch {
    mostrarToast('Error de conexión.', true);
  }
}

/**
 * Abre el modal para editar un usuario y llena los datos
 */
function abrirModalEditarUsuario(id, nombre, email, rol) {
  document.getElementById('edit-user-id').value = id;
  document.getElementById('edit-user-name').value = nombre;
  document.getElementById('edit-user-email').value = email;
  document.getElementById('edit-user-password').value = ''; // En blanco por defecto
  document.getElementById('edit-user-role').value = rol;
  
  const resultDiv = document.getElementById('edit-user-result');
  if (resultDiv) {
    resultDiv.textContent = '';
    resultDiv.style.display = 'none';
  }
  
  abrirModal('edit-user-modal');
}

// Escuchar envío del formulario de editar usuario
(function initEditUserForm() {
  const form = document.getElementById('edit-user-form');
  if (!form) return;

  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const id = document.getElementById('edit-user-id').value;
    const name = document.getElementById('edit-user-name').value.trim();
    const email = document.getElementById('edit-user-email').value.trim();
    const password = document.getElementById('edit-user-password').value;
    const role = document.getElementById('edit-user-role').value;
    
    const btn = document.getElementById('btn-edit-user');
    const resultDiv = document.getElementById('edit-user-result');
    
    btn.disabled = true;
    btn.textContent = 'Guardando...';
    
    try {
      const res = await fetch(`/api/users/${id}/edit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password, role })
      });
      
      const data = await res.json();
      
      if (data.success) {
        mostrarToast('Usuario actualizado.');
        setTimeout(() => window.location.reload(), 1000);
      } else {
        mostrarError(resultDiv, data.error || 'Error al actualizar.');
        btn.disabled = false;
        btn.textContent = 'Guardar Cambios';
      }
    } catch (err) {
      mostrarError(resultDiv, 'Error de conexión.');
      btn.disabled = false;
      btn.textContent = 'Guardar Cambios';
    }
  });
})();

/* ══════════════════════════════════════════
   8. GRÁFICA DE INGRESOS — Chart.js
   ══════════════════════════════════════════ */

/**
 * Inicializa el gráfico de área de ingresos con Chart.js
 * El elemento canvas debe tener id="revenue-chart"
 * Los datos se pasan mediante el atributo data-ingresos en JSON
 */
(function initRevenueChart() {
  const canvas = document.getElementById('revenue-chart');
  if (!canvas) return;

  // Leer los datos del atributo data-ingresos (se inyectan desde Flask/Jinja2)
  let ingresos = {};
  try {
    ingresos = JSON.parse(canvas.dataset.ingresos || '{}');
  } catch (e) {
    console.warn('No se pudieron parsear los datos del gráfico.');
    return;
  }

  // Si no hay datos reales, crear datos de ejemplo
  if (Object.keys(ingresos).length === 0) {
    const hoy = new Date();
    for (let i = 13; i >= 0; i--) {
      const d = new Date(hoy);
      d.setDate(hoy.getDate() - i);
      const key = d.toISOString().slice(0, 10);
      ingresos[key] = Math.random() * 5000 + 500;
    }
  }

  const etiquetas = Object.keys(ingresos).sort();
  const valores   = etiquetas.map(k => ingresos[k]);

  // Actualizar el total mostrado
  const totalEl = document.getElementById('revenue-total');
  if (totalEl) {
    const suma = valores.reduce((a, b) => a + b, 0);
    totalEl.textContent = `$${suma.toLocaleString('es-ES', { minimumFractionDigits: 2 })}`;
  }

  // Crear el gráfico con Chart.js (cargado desde CDN en el HTML)
  new Chart(canvas.getContext('2d'), {
    type: 'line',
    data: {
      labels: etiquetas,
      datasets: [{
        label: 'Ingresos',
        data: valores,
        borderColor: '#D4AF37',
        borderWidth: 2.5,
        fill: true,
        // Degradado dorado bajo la línea
        backgroundColor: function (context) {
          const chart = context.chart;
          const { ctx, chartArea } = chart;
          if (!chartArea) return 'rgba(212,175,55,0.1)';
          const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
          gradient.addColorStop(0, 'rgba(212,175,55,0.25)');
          gradient.addColorStop(1, 'rgba(212,175,55,0)');
          return gradient;
        },
        tension: 0.4,       // Suavizado de la curva
        pointRadius: 0,     // Sin puntos para un look limpio
        pointHoverRadius: 5,
        pointBackgroundColor: '#F5D77F'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(18,18,22,0.95)',
          borderColor: 'rgba(212,175,55,0.3)',
          borderWidth: 1,
          titleColor: 'rgba(244,244,245,0.8)',
          bodyColor: '#F5D77F',
          callbacks: {
            label: ctx => ` $${ctx.parsed.y.toLocaleString('es-ES', { minimumFractionDigits: 2 })}`
          }
        }
      },
      scales: {
        x: {
          grid:   { color: 'rgba(0,0,0,0.05)' },
          ticks:  { color: 'rgba(0,0,0,0.4)', font: { size: 10 } }
        },
        y: {
          grid:   { color: 'rgba(0,0,0,0.05)' },
          ticks:  {
            color: 'rgba(0,0,0,0.4)', font: { size: 10 },
            callback: v => `$${v.toLocaleString()}`
          }
        }
      }
    }
  });
})();

/* ══════════════════════════════════════════
   9. BARRAS DE PROGRESO — Animación
   ══════════════════════════════════════════ */

/**
 * Anima las barras de progreso del inventario cuando se hacen visibles.
 * Usa IntersectionObserver para disparar la animación solo al scrollear.
 */
(function initProgressBars() {
  const barras = document.querySelectorAll('.progress-fill[data-pct]');
  if (!barras.length) return;

  const observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        const barra = entry.target;
        const pct   = barra.dataset.pct;
        barra.style.width = pct + '%';
        observer.unobserve(barra);
      }
    });
  }, { threshold: 0.2 });

  barras.forEach(b => observer.observe(b));
})();

/* ══════════════════════════════════════════
   10. ANIMACIONES ON SCROLL — fade-up
   ══════════════════════════════════════════ */

(function initScrollAnimations() {
  const elementos = document.querySelectorAll('.anim-on-scroll');
  if (!elementos.length) return;

  const observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('anim-fade-up');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '-50px' });

  elementos.forEach(el => observer.observe(el));
})();

/* ══════════════════════════════════════════
   11. CREACIÓN DE PRODUCTOS (ADMIN)
   ══════════════════════════════════════════ */

(function initProductCreation() {
  const form = document.getElementById('create-product-form');
  if (!form) return;

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    
    const nombre = document.getElementById('prod-name').value.trim();
    const categoria = document.getElementById('prod-category').value;
    const precio = document.getElementById('prod-price').value;
    const stock = document.getElementById('prod-stock').value;
    const imageInput = document.getElementById('prod-image');
    
    const btn = document.getElementById('btn-create-product');
    const result = document.getElementById('product-result');
    
    btn.disabled = true;
    btn.textContent = 'Creando...';
    
    try {
      // 1. Crear el producto
      const res = await fetch('/api/products', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: nombre, category: categoria, price: precio, stock: stock })
      });
      
      const data = await res.json();
      
      if (!data.success) {
        mostrarError(result, data.error);
        btn.disabled = false;
        btn.textContent = 'Crear Producto';
        return;
      }
      
      const productId = data.product.id;
      
      // 2. Subir imagen si se seleccionó una
      if (imageInput.files.length > 0) {
        const formData = new FormData();
        formData.append('image', imageInput.files[0]);
        
        btn.textContent = 'Subiendo imagen...';
        
        await fetch(`/api/products/${productId}/image`, {
          method: 'POST',
          body: formData
        });
      }
      
      mostrarToast('Producto creado exitosamente.');
      setTimeout(() => window.location.reload(), 1500);
      
    } catch (err) {
      mostrarError(result, 'Error de conexión.');
      btn.disabled = false;
      btn.textContent = 'Crear Producto';
    }
  });
})();

/**
 * Elimina un producto del catálogo (Admin)
 */
async function eliminarProducto(productId, nombre) {
  if (!confirm(`¿Eliminar el producto "${nombre}"?`)) return;
  
  try {
    const res = await fetch(`/api/products/${productId}`, { method: 'DELETE' });
    const data = await res.json();
    
    if (data.success) {
      mostrarToast('Producto eliminado.');
      const fila = document.getElementById(`admin-prod-${productId}`);
      if (fila) fila.remove();
    } else {
      mostrarToast('' + (data.error || 'Error al eliminar.'), true);
    }
  } catch {
    mostrarToast('Error de conexión.', true);
  }
}


// ── Enviar Correo Factura ──
async function enviarCorreoFactura(invoiceId) {
  try {
    const res = await fetch(`/api/invoices/${invoiceId}/email`, {
      method: 'POST'
    });
    const data = await res.json();
    if (data.success) {
      mostrarToast('¡Factura enviada por correo exitosamente!');
    } else {
      mostrarToast('Error: ' + data.error, true);
    }
  } catch (error) {
    mostrarToast('Error de conexión al enviar el correo.', true);
  }
}

/* ══════════════════════════════════════════
   12. SOLICITAR AUDITORÍA — Formulario
   ══════════════════════════════════════════ */

(function initAuditForm() {
  const form = document.getElementById('audit-request-form');
  if (!form) return;

  form.addEventListener('submit', async function (e) {
    e.preventDefault();

    const name        = document.getElementById('audit-name').value.trim();
    const email       = document.getElementById('audit-email').value.trim();
    const company     = document.getElementById('audit-company').value.trim();
    const audit_type  = document.getElementById('audit-type').value;
    const description = document.getElementById('audit-description').value.trim();

    const btn       = document.getElementById('btn-audit-submit');
    const resultDiv = document.getElementById('audit-result');

    if (!name || !email || !company || !audit_type || !description) {
      mostrarError(resultDiv, 'Todos los campos son obligatorios.');
      return;
    }

    btn.disabled = true;
    btn.textContent = 'Enviando solicitud...';

    try {
      const res = await fetch('/api/audit-request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, company, audit_type, description })
      });

      const data = await res.json();

      if (data.success) {
        resultDiv.textContent = '' + data.message + ' (ID: ' + data.request_id + ')';
        resultDiv.className = 'alert-success';
        resultDiv.style.display = 'block';
        resultDiv.style.padding = '1rem';
        form.reset();
        mostrarToast('Solicitud de auditoría registrada.');
      } else {
        mostrarError(resultDiv, data.error || 'Error al enviar la solicitud.');
      }

      btn.disabled = false;
      btn.textContent = 'Enviar Solicitud';
    } catch (err) {
      mostrarError(resultDiv, 'Error de conexión.');
      btn.disabled = false;
      btn.textContent = 'Enviar Solicitud';
    }
  });
})();

/* ══════════════════════════════════════════
   13. SUBIR AVATAR — Foto de Perfil
   ══════════════════════════════════════════ */

async function subirAvatar(event) {
  const archivo = event.target.files[0];
  if (!archivo) return;

  const formData = new FormData();
  formData.append('avatar', archivo);

  try {
    const res = await fetch('/api/profile/avatar', {
      method: 'POST',
      body: formData
    });

    const data = await res.json();

    if (data.success) {
      // Actualizar la previsualización de la imagen en la página
      const preview = document.getElementById('profile-img-preview');
      const fallback = document.getElementById('profile-img-fallback');

      if (preview) {
        preview.src = data.avatar_url;
        preview.style.display = '';
      }
      if (fallback) {
        fallback.style.display = 'none';
      }

      mostrarToast('Foto de perfil actualizada.');
    } else {
      mostrarToast('Error: ' + (data.error || 'No se pudo subir la imagen.'), true);
    }
  } catch (err) {
    mostrarToast('Error de conexión al subir la imagen.', true);
  }
}

/* ════════════════════════════════════════════════════════════════
   14. SISTEMA COMPLETO DE CARRO DE COMPRAS Y FACTURACIÓN DIGITAL
   ════════════════════════════════════════════════════════════════ */

const CART_STORAGE_KEY = 'lycaon_security_cart_v1';
let ultimaFacturaId = null;

function getCart() {
  try {
    const raw = localStorage.getItem(CART_STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    return [];
  }
}

function saveCart(cart) {
  try {
    localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cart));
  } catch (e) {}
  renderCartUI();
}

function agregarAlCarro(id, nombre, precio, stock, img, categoria) {
  if (stock <= 0) {
    mostrarToast('Este producto no tiene existencias disponibles.', true);
    return;
  }

  const cart = getCart();
  const existingIndex = cart.findIndex(item => item.id === id);

  if (existingIndex >= 0) {
    if (cart[existingIndex].cantidad < stock) {
      cart[existingIndex].cantidad += 1;
      mostrarToast(`+1 ${nombre} en el carro.`);
    } else {
      mostrarToast(`Stock máximo alcanzado (${stock} u.)`, true);
      return;
    }
  } else {
    cart.push({
      id: id,
      nombre: nombre,
      precio: parseFloat(precio),
      stock: parseInt(stock),
      cantidad: 1,
      image_url: img || '',
      categoria: categoria || 'General'
    });
    mostrarToast(`${nombre} agregado al carro de compras.`);
  }

  saveCart(cart);
  abrirCarro();
}

function modificarCantidadCarro(id, delta) {
  const cart = getCart();
  const item = cart.find(i => i.id === id);
  if (!item) return;

  const nuevaCant = item.cantidad + delta;
  if (nuevaCant <= 0) {
    eliminarDelCarro(id);
    return;
  }
  if (nuevaCant > item.stock) {
    mostrarToast(`Stock máximo disponible: ${item.stock} u.`, true);
    return;
  }

  item.cantidad = nuevaCant;
  saveCart(cart);
}

function eliminarDelCarro(id) {
  let cart = getCart();
  cart = cart.filter(i => i.id !== id);
  saveCart(cart);
}

function vaciarCarro() {
  saveCart([]);
}

function abrirCarro() {
  const drawer = document.getElementById('cart-drawer');
  const backdrop = document.getElementById('cart-drawer-backdrop');
  if (drawer) drawer.classList.remove('translate-x-full');
  if (backdrop) backdrop.classList.remove('hidden');
}

function cerrarCarro() {
  const drawer = document.getElementById('cart-drawer');
  const backdrop = document.getElementById('cart-drawer-backdrop');
  if (drawer) drawer.classList.add('translate-x-full');
  if (backdrop) backdrop.classList.add('hidden');
}

function renderCartUI() {
  const cart = getCart();
  const totalCount = cart.reduce((sum, it) => sum + it.cantidad, 0);
  const subtotal = cart.reduce((sum, it) => sum + (it.precio * it.cantidad), 0);
  const fmt = (num) => `$${num.toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  // 1. Badges y contadores numéricos
  const badgeTop = document.getElementById('cart-badge');
  if (badgeTop) {
    badgeTop.textContent = totalCount;
    if (totalCount > 0) {
      badgeTop.classList.remove('hidden');
      badgeTop.classList.add('flex');
    } else {
      badgeTop.classList.add('hidden');
      badgeTop.classList.remove('flex');
    }
  }

  const storeCounter = document.getElementById('store-cart-counter');
  if (storeCounter) storeCounter.textContent = totalCount;

  const floatingBadge = document.getElementById('floating-cart-badge');
  if (floatingBadge) floatingBadge.textContent = totalCount;

  const drawerCount = document.getElementById('cart-drawer-count');
  if (drawerCount) drawerCount.textContent = totalCount;

  // 2. Subtotales
  const subEl = document.getElementById('cart-subtotal');
  const totEl = document.getElementById('cart-total');

  if (subEl) subEl.textContent = fmt(subtotal);
  if (totEl) totEl.textContent = fmt(subtotal);

  // 3. Renderizado de ítems
  const container = document.getElementById('cart-items-container');
  if (!container) return;

  if (cart.length === 0) {
    container.innerHTML = `
      <div class="h-full min-h-[220px] flex flex-col items-center justify-center text-center p-6 text-zinc-500">
        <div class="w-14 h-14 rounded-2xl bg-black/60 border border-white/10 flex items-center justify-center text-zinc-600 mb-3 shadow-inner">
          <svg class="w-7 h-7 text-gold/60" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/></svg>
        </div>
        <div class="text-xs font-mono font-bold text-white uppercase tracking-wider mb-1">Carro Vacío</div>
        <p class="text-[11px] text-zinc-400 mb-4 max-w-xs leading-relaxed">Selecciona equipamiento perimetral o licencias de seguridad para agregarlas.</p>
        <a href="/dashboard/store" onclick="cerrarCarro()" class="btn-outline text-xs uppercase tracking-wider py-2 px-4 border-white/15 hover:border-gold hover:text-gold font-mono">
          Explorar Catálogo →
        </a>
      </div>
    `;
    const btnCheckout = document.getElementById('btn-checkout-carro');
    if (btnCheckout) {
      btnCheckout.disabled = true;
      btnCheckout.classList.add('opacity-40', 'cursor-not-allowed');
    }
    return;
  }

  const btnCheckout = document.getElementById('btn-checkout-carro');
  if (btnCheckout) {
    btnCheckout.disabled = false;
    btnCheckout.classList.remove('opacity-40', 'cursor-not-allowed');
  }

  let html = '';
  cart.forEach(item => {
    const itemTotal = item.precio * item.cantidad;
    html += `
      <div class="p-3 rounded-xl bg-black/60 border border-white/10 flex items-center gap-3 group hover:border-gold/30 transition-colors">
        <div class="w-11 h-11 rounded-lg bg-black border border-white/10 flex-shrink-0 flex items-center justify-center overflow-hidden">
          ${item.image_url && item.image_url !== '/static/img/placeholder.svg' 
            ? `<img src="${item.image_url}" alt="${item.nombre}" class="w-full h-full object-cover" onerror="this.onerror=null; this.src='/static/img/placeholder.svg';">`
            : `<span class="text-[10px] font-mono font-bold text-gold">${(item.categoria || 'SEC').substring(0, 3).toUpperCase()}</span>`
          }
        </div>
        <div class="flex-1 min-w-0">
          <div class="text-xs font-bold text-white truncate">${item.nombre}</div>
          <div class="text-[11px] font-mono text-gold">${fmt(item.precio)} c/u</div>
          <div class="flex items-center gap-2 mt-1.5">
            <div class="inline-flex items-center rounded-lg bg-black/90 border border-white/10 overflow-hidden">
              <button onclick="modificarCantidadCarro('${item.id}', -1)" class="w-6 h-5 flex items-center justify-center text-zinc-400 hover:text-white transition-colors text-xs font-bold">-</button>
              <span class="w-6 text-center font-mono text-[11px] font-bold text-white">${item.cantidad}</span>
              <button onclick="modificarCantidadCarro('${item.id}', 1)" class="w-6 h-5 flex items-center justify-center text-zinc-400 hover:text-white transition-colors text-xs font-bold">+</button>
            </div>
            <span class="text-[10px] font-mono text-zinc-400">= ${fmt(itemTotal)}</span>
          </div>
        </div>
        <button onclick="eliminarDelCarro('${item.id}')" class="p-1.5 rounded-lg text-zinc-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors" title="Quitar ítem">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
        </button>
      </div>
    `;
  });

  container.innerHTML = html;
}

async function procesarCompraCarro() {
  const cart = getCart();
  if (cart.length === 0) {
    mostrarToast('El carro está vacío.', true);
    return;
  }

  const btn = document.getElementById('btn-checkout-carro');
  const errorEl = document.getElementById('cart-checkout-error');
  if (errorEl) errorEl.classList.add('hidden');

  btn.disabled = true;
  btn.innerHTML = `<svg class="w-4 h-4 animate-spin inline-block mr-1" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg> Facturando...`;

  try {
    const payload = {
      items: cart.map(i => ({
        product_id: i.id,
        cantidad: i.cantidad
      }))
    };

    const res = await fetch('/api/orders', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (data.success) {
      saveCart([]);
      cerrarCarro();
      mostrarFacturaExitosa(data);
    } else {
      if (errorEl) {
        errorEl.textContent = data.error || 'Error al procesar el carro.';
        errorEl.classList.remove('hidden');
      } else {
        mostrarToast(data.error || 'Error al procesar la compra.', true);
      }
    }
  } catch (err) {
    if (errorEl) {
      errorEl.textContent = 'Error de conexión con el servidor.';
      errorEl.classList.remove('hidden');
    } else {
      mostrarToast('Error de conexión.', true);
    }
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<span>Autorizar Compra y Facturar →</span>`;
  }
}

function mostrarFacturaExitosa(datos) {
  ultimaFacturaId = datos.invoice_id || (datos.order && datos.order.invoice_id);
  const modalBackdrop = document.getElementById('invoice-modal-backdrop');
  if (!modalBackdrop) {
    mostrarToast('Compra autorizada con éxito. Factura: ' + ultimaFacturaId);
    setTimeout(() => window.location.reload(), 1500);
    return;
  }

  document.getElementById('inv-modal-id').textContent = ultimaFacturaId || 'N/A';
  document.getElementById('inv-modal-order').textContent = (datos.order && datos.order.id) || 'N/A';
  const total = (datos.order && datos.order.total) ? datos.order.total : 0;
  document.getElementById('inv-modal-total').textContent = `$${parseFloat(total).toLocaleString('es-ES', { minimumFractionDigits: 2 })} USD`;

  const feedback = document.getElementById('inv-email-feedback');
  if (feedback) {
    feedback.className = 'hidden';
    feedback.textContent = '';
  }

  modalBackdrop.classList.remove('hidden');
  modalBackdrop.classList.add('flex');

  // Enviar factura al correo automáticamente
  if (ultimaFacturaId) {
    enviarFacturaActualCorreo(true);
  }
}

function descargarFacturaActual() {
  if (!ultimaFacturaId) return;
  window.location.href = `/api/invoices/${ultimaFacturaId}/download`;
}

async function enviarFacturaActualCorreo(isSilent = false) {
  if (!ultimaFacturaId) return;
  const feedback = document.getElementById('inv-email-feedback');
  const btn = document.getElementById('inv-btn-email');

  if (btn && !isSilent) {
    btn.disabled = true;
    btn.innerHTML = 'Despachando...';
  }

  try {
    const res = await fetch(`/api/invoices/${ultimaFacturaId}/email`, { method: 'POST' });
    const data = await res.json();
    if (feedback) {
      feedback.classList.remove('hidden');
      if (data.success) {
        feedback.className = 'corp-invoice-notice corp-notice-success';
        feedback.innerHTML = `
          <svg class="corp-notice-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          <span class="corp-notice-text">${data.message || 'Comprobante despachado al correo corporativo.'}</span>
        `;
      } else {
        feedback.className = 'corp-invoice-notice corp-notice-warning';
        feedback.innerHTML = `
          <svg class="corp-notice-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span class="corp-notice-text">${data.error || 'Aviso sobre el servicio de despacho por correo.'}</span>
        `;
      }
    }
  } catch (e) {
    if (feedback && !isSilent) {
      feedback.classList.remove('hidden');
      feedback.className = 'corp-invoice-notice corp-notice-error';
      feedback.innerHTML = `
        <svg class="corp-notice-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span class="corp-notice-text">Disponibilidad limitada en el servicio de correo institucional.</span>
      `;
    }
  } finally {
    if (btn && !isSilent) {
      btn.disabled = false;
      btn.innerHTML = `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg> Reenviar al Correo`;
    }
  }
}

function cerrarFacturaModal() {
  const modalBackdrop = document.getElementById('invoice-modal-backdrop');
  if (modalBackdrop) {
    modalBackdrop.classList.add('hidden');
    modalBackdrop.classList.remove('flex');
  }
  window.location.reload();
}

// Inicializar el carrito y carruseles Bootstrap al cargar cualquier página
document.addEventListener('DOMContentLoaded', function () {
  renderCartUI();

  // Inicializar carruseles Bootstrap (Equipos Destacados / Vitrinas)
  if (typeof bootstrap !== 'undefined' && bootstrap.Carousel) {
    document.querySelectorAll('.carousel').forEach(carouselEl => {
      try {
        const interval = parseInt(carouselEl.getAttribute('data-bs-interval') || '4500', 10);
        new bootstrap.Carousel(carouselEl, {
          interval: interval,
          ride: 'carousel',
          wrap: true,
          touch: true
        });
      } catch (err) {
        console.warn('Bootstrap Carousel init:', err);
      }
    });
  }
});

