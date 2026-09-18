/**
 * ╔══════════════════════════════════════════════════════════╗
 * ║       LYCAON SOFTWARE — JavaScript Principal               ║
 * ║   Maneja toda la interactividad del frontend            ║
 * ║   Sin frameworks, solo JS limpio y comentado            ║
 * ╚══════════════════════════════════════════════════════════╝
 */

/* ══════════════════════════════════════════
   1. NAVBAR — Efecto scroll glassmorphic
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
})();

/* ══════════════════════════════════════════
   2. SIDEBAR — Colapsar / Expandir
   ══════════════════════════════════════════ */

(function initSidebar() {
  const sidebar = document.getElementById('sidebar');
  const toggleBtn = document.getElementById('sidebar-toggle');
  const labels = document.querySelectorAll('.nav-label, .sidebar-brand, .user-info-text, .sidebar-menu-label, .logout-label');

  if (!sidebar || !toggleBtn) return;

  let collapsed = false;

  toggleBtn.addEventListener('click', function () {
    collapsed = !collapsed;
    sidebar.classList.toggle('collapsed', collapsed);

    // Cambia el ícono del botón ← / →
    toggleBtn.textContent = collapsed ? '›' : '‹';

    // Oculta los textos del nav cuando está colapsado
    labels.forEach(function (el) {
      el.style.display = collapsed ? 'none' : '';
    });
  });
})();

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
    if (modal.parentNode !== document.body) {
      document.body.appendChild(modal);
    }
    modal.classList.add('open');
    document.body.style.overflow = 'hidden'; // Bloquea el scroll del fondo
  }
}

/**
 * Cierra un modal por su ID
 * @param {string} modalId - ID del elemento .modal-overlay
 */
function cerrarModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('open');
    document.body.style.overflow = '';
  }
}

// Cerrar modal al hacer clic en el overlay (fuera del contenido)
document.addEventListener('click', function (e) {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('open');
    document.body.style.overflow = '';
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
  const toggleBtn    = document.getElementById('auth-toggle-btn');
  const loginCard    = document.getElementById('login-card');
  const registerCard = document.getElementById('register-card');

  // Alternar entre login y registro
  if (toggleBtn && loginCard && registerCard) {
    toggleBtn.addEventListener('click', function () {
      const isLogin = loginCard.style.display !== 'none';
      loginCard.style.display    = isLogin ? 'none' : 'block';
      registerCard.style.display = isLogin ? 'block' : 'none';
      toggleBtn.textContent = isLogin
        ? 'Ya soy cliente. Iniciar sesión'
        : '¿No tienes cuenta? Solicitar acceso';
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
      const btn      = document.getElementById('register-btn');
      const errorDiv = document.getElementById('register-error');

      if (!nombre || !email || !password) {
        mostrarError(errorDiv, 'Llena todos los campos.');
        return;
      }

      btn.disabled = true;
      btn.innerHTML = '<span>Procesando...</span>';

      try {
        const respuesta = await fetch('/api/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: nombre, email, password })
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

      const categoria = btn.dataset.categoria;

      // Mostrar/ocultar productos según la categoría seleccionada
      productCards.forEach(function (card) {
        if (categoria === 'todos' || card.dataset.categoria === categoria) {
          card.style.display = '';
          card.style.animation = 'fade-up 0.4s ease forwards';
        } else {
          card.style.display = 'none';
        }
      });
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
 * Confirma y envía la orden de compra al servidor Flask
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
      result.textContent = '✓ Pedido realizado exitosamente.';
      result.className   = 'alert-success';

      // Cerrar el modal y recargar la página después de 1.5 segundos
      setTimeout(function () {
        cerrarModal('buy-modal');
        window.location.reload();
      }, 1500);
    } else {
      result.textContent = datos.error || 'Error al procesar el pedido.';
      result.className   = 'alert-error';
      btn.disabled = false;
      btn.textContent = 'Confirmar Compra';
    }
  } catch (err) {
    result.textContent = 'Error de conexión.';
    result.className   = 'alert-error';
    btn.disabled = false;
    btn.textContent = 'Confirmar Compra';
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
      mostrarToast('✓ Rol actualizado correctamente.');
      setTimeout(() => window.location.reload(), 1000);
    } else {
      mostrarToast('⚠ ' + (datos.error || 'Error al cambiar rol.'), true);
    }
  } catch {
    mostrarToast('⚠ Error de conexión.', true);
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
      mostrarToast('✓ Usuario eliminado.');
      // Eliminar la fila de la tabla sin recargar la página
      const fila = document.getElementById(`user-row-${userId}`);
      if (fila) fila.remove();
    } else {
      mostrarToast('⚠ ' + (datos.error || 'Error al eliminar.'), true);
    }
  } catch {
    mostrarToast('⚠ Error de conexión.', true);
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
        mostrarToast('✓ Usuario actualizado.');
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
        borderColor: '#38bdf8',
        borderWidth: 2,
        fill: true,
        // Degradado bajo la línea
        backgroundColor: function (context) {
          const chart = context.chart;
          const { ctx, chartArea } = chart;
          if (!chartArea) return 'rgba(56,189,248,0.1)';
          const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
          gradient.addColorStop(0, 'rgba(56,189,248,0.25)');
          gradient.addColorStop(1, 'rgba(56,189,248,0)');
          return gradient;
        },
        tension: 0.4,       // Suavizado de la curva
        pointRadius: 0,     // Sin puntos para un look limpio
        pointHoverRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(9,9,14,0.9)',
          borderColor: 'rgba(255,255,255,0.08)',
          borderWidth: 1,
          titleColor: 'rgba(255,255,255,0.4)',
          bodyColor: '#38bdf8',
          callbacks: {
            label: ctx => ` $${ctx.parsed.y.toLocaleString('es-ES', { minimumFractionDigits: 2 })}`
          }
        }
      },
      scales: {
        x: {
          grid:   { color: 'rgba(255,255,255,0.03)' },
          ticks:  { color: 'rgba(255,255,255,0.3)', font: { size: 10 } }
        },
        y: {
          grid:   { color: 'rgba(255,255,255,0.03)' },
          ticks:  {
            color: 'rgba(255,255,255,0.3)', font: { size: 10 },
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
      
      mostrarToast('✓ Producto creado exitosamente.');
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
      mostrarToast('✓ Producto eliminado.');
      const fila = document.getElementById(`admin-prod-${productId}`);
      if (fila) fila.remove();
    } else {
      mostrarToast('⚠ ' + (data.error || 'Error al eliminar.'), true);
    }
  } catch {
    mostrarToast('⚠ Error de conexión.', true);
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
      mostrarToast('✓ ¡Factura enviada por correo exitosamente!');
    } else {
      mostrarToast('⚠ Error: ' + data.error, true);
    }
  } catch (error) {
    mostrarToast('⚠ Error de conexión al enviar el correo.', true);
  }
}
