/**
 * ══════════════════════════════════════════════════════════════════════════════
 * LYCAON SECURITY — SIAM DATASENA INTERACTION SYSTEM (JS COMPLEMENTARIO)
 * Microinteracciones, animación de entrada, sidebar interactivo y toasts prémium
 * ══════════════════════════════════════════════════════════════════════════════
 */

(function () {
  'use strict';

  /* ── 1. GESTIÓN FLUIDA DEL SIDEBAR (COLAPSO / EXPANSIÓN / MÓVIL) ── */
  function setupSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (!sidebar) return;

    // Verificar si ya existe un botón de toggle; si no, inyectar el botón estilizado
    let toggleBtn = document.getElementById('sidebar-toggle');
    const header = sidebar.querySelector('.h-20') || sidebar.querySelector('.sidebar-header');

    if (!toggleBtn && header) {
      toggleBtn = document.createElement('button');
      toggleBtn.id = 'sidebar-toggle';
      toggleBtn.className = 'sidebar-toggle-btn';
      toggleBtn.setAttribute('type', 'button');
      toggleBtn.setAttribute('aria-label', 'Colapsar menú lateral');
      toggleBtn.setAttribute('title', 'Alternar panel de navegación');
      toggleBtn.innerHTML = `
        <svg class="w-4 h-4 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
        </svg>
      `;
      header.appendChild(toggleBtn);
    }

    // Backdrop para dispositivos móviles
    let backdrop = document.querySelector('.siam-sidebar-backdrop');
    if (!backdrop) {
      backdrop = document.createElement('div');
      backdrop.className = 'siam-sidebar-backdrop';
      document.body.appendChild(backdrop);
      backdrop.addEventListener('click', () => {
        sidebar.classList.remove('mobile-open');
        backdrop.classList.remove('active');
      });
    }

    // Restaurar estado guardado en localStorage (en escritorio)
    const savedState = localStorage.getItem('lycaon_sidebar_collapsed');
    if (window.innerWidth >= 1024 && savedState === 'true') {
      sidebar.classList.add('collapsed');
      if (toggleBtn) {
        toggleBtn.querySelector('svg').style.transform = 'rotate(180deg)';
      }
    }

    if (toggleBtn) {
      toggleBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        if (window.innerWidth < 1024) {
          sidebar.classList.toggle('mobile-open');
          backdrop.classList.toggle('active', sidebar.classList.contains('mobile-open'));
        } else {
          const isCollapsed = sidebar.classList.toggle('collapsed');
          localStorage.setItem('lycaon_sidebar_collapsed', isCollapsed ? 'true' : 'false');
          const svg = toggleBtn.querySelector('svg');
          if (svg) {
            svg.style.transform = isCollapsed ? 'rotate(180deg)' : 'rotate(0deg)';
          }
        }
      });
    }

    // Normalizar enlaces del sidebar (envolver texto y aislar iconos para evitar rotura visual)
    const navLinks = sidebar.querySelectorAll('nav a, .sidebar-footer a');
    navLinks.forEach(link => {
      // Envolver nodos de texto directo
      Array.from(link.childNodes).forEach(node => {
        if (node.nodeType === Node.TEXT_NODE && node.textContent.trim().length > 0) {
          const span = document.createElement('span');
          span.className = 'sidebar-text truncate';
          span.textContent = node.textContent.trim();
          node.replaceWith(span);
        }
      });

      // Asegurar contenedor .sidebar-icon para los SVG
      const svg = link.querySelector('svg');
      if (svg && !svg.closest('.sidebar-icon')) {
        const iconSpan = document.createElement('span');
        iconSpan.className = 'sidebar-icon flex-shrink-0 flex items-center justify-center w-8 h-8 rounded-lg bg-black/40 border border-translucent';
        svg.parentNode.insertBefore(iconSpan, svg);
        iconSpan.appendChild(svg);
      }

      // Configurar Tooltips en enlaces del sidebar cuando está colapsado
      const titleSpan = link.querySelector('.sidebar-text');
      const text = titleSpan ? titleSpan.textContent.trim() : (link.getAttribute('title') || '');
      if (text) {
        link.setAttribute('data-title', text);
        link.addEventListener('mouseenter', function () {
          if (sidebar.classList.contains('collapsed') && window.innerWidth >= 1024) {
            showFloatingTooltip(link, text);
          }
        });
        link.addEventListener('mouseleave', hideFloatingTooltip);
      }
    });
  }

  // Tooltip Flotante para el sidebar colapsado
  let activeTooltip = null;
  function showFloatingTooltip(targetEl, text) {
    hideFloatingTooltip();
    const rect = targetEl.getBoundingClientRect();
    const tooltip = document.createElement('div');
    tooltip.className = 'siam-floating-tooltip';
    tooltip.textContent = text;
    Object.assign(tooltip.style, {
      position: 'fixed',
      left: `${rect.right + 12}px`,
      top: `${rect.top + (rect.height / 2) - 14}px`,
      background: '#18181F',
      color: '#F4F4F5',
      border: '1px solid rgba(212, 175, 55, 0.35)',
      padding: '5px 12px',
      borderRadius: '8px',
      fontSize: '12px',
      fontWeight: '600',
      letterSpacing: '0.04em',
      boxShadow: '0 8px 24px rgba(0,0,0,0.6), 0 0 12px rgba(212, 175, 55, 0.15)',
      zIndex: '9999',
      pointerEvents: 'none',
      whiteSpace: 'nowrap',
      opacity: '0',
      transform: 'translateX(-6px)',
      transition: 'all 0.2s cubic-bezier(0.16, 1, 0.3, 1)'
    });
    document.body.appendChild(tooltip);
    activeTooltip = tooltip;
    requestAnimationFrame(() => {
      tooltip.style.opacity = '1';
      tooltip.style.transform = 'translateX(0)';
    });
  }

  function hideFloatingTooltip() {
    if (activeTooltip) {
      activeTooltip.remove();
      activeTooltip = null;
    }
  }

  /* ── 2. TOPBAR CON BREADCRUMBS & BALIZA DE SEGURIDAD TIPO SIAM ── */
  function setupTopbar() {
    // Enlace del botón móvil de la topbar (sea estática o inyectada)
    const mobileBtn = document.getElementById('siam-mobile-menu-btn');
    const sidebar = document.getElementById('sidebar');
    const backdrop = document.querySelector('.siam-sidebar-backdrop');
    if (mobileBtn && sidebar && !mobileBtn.dataset.bound) {
      mobileBtn.dataset.bound = 'true';
      mobileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        sidebar.classList.toggle('mobile-open');
        if (backdrop) backdrop.classList.toggle('active', sidebar.classList.contains('mobile-open'));
      });
    }

    const mainArea = document.querySelector('main');
    if (!mainArea || document.getElementById('siam-injected-topbar')) return;

    // Solo inyectar si estamos en el dashboard (donde no hay navbar pública)
    if (!document.getElementById('main-navbar')) {
      const topbar = document.createElement('header');
      topbar.id = 'siam-injected-topbar';
      topbar.className = 'siam-topbar flex items-center justify-between px-6 lg:px-10 flex-shrink-0';
      topbar.style.height = '64px';

      // Breadcrumbs dinámicos basados en la URL
      const path = window.location.pathname;
      let sectionName = 'Telemetría';
      let parentName = 'Operaciones';

      if (path.includes('/dashboard/store')) {
        sectionName = 'Catálogo Autorizado';
        parentName = 'Cliente';
      } else if (path.includes('/dashboard/purchases')) {
        sectionName = 'Mis Operaciones';
        parentName = 'Cliente';
      } else if (path.includes('/admin/tienda')) {
        sectionName = 'Arsenal / Inventario';
        parentName = 'Administración';
      } else if (path.includes('/dashboard/users')) {
        sectionName = 'Personal Registrado';
        parentName = 'Administración';
      } else if (path.includes('/dashboard/activity')) {
        sectionName = 'Auditoría de Actividad';
        parentName = 'Administración';
      } else if (path.includes('/dashboard/profile')) {
        sectionName = 'Credenciales e Identidad';
        parentName = 'General';
      } else if (path.includes('/admin/reports')) {
        sectionName = 'Reportes Profesionales';
        parentName = 'Administración';
      } else if (path.includes('/admin/logistics')) {
        sectionName = 'Logística y Finanzas';
        parentName = 'Administración';
      }

      topbar.innerHTML = `
        <div class="flex items-center gap-4">
          <!-- Botón móvil para abrir el menú lateral -->
          <button id="siam-mobile-menu-btn" class="lg:hidden p-2 rounded-lg bg-black/40 border border-translucent text-gray-400 hover:text-gold transition-colors" aria-label="Abrir menú lateral">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <nav class="siam-breadcrumbs" aria-label="Ruta de navegación">
            <a href="/" class="hover:text-gold transition-colors">Lycaon</a>
            <span class="separator">/</span>
            <span class="text-gray-400">${parentName}</span>
            <span class="separator">/</span>
            <span class="current text-gold">${sectionName}</span>
          </nav>
        </div>

        <div class="flex items-center gap-4">
          <!-- Baliza de Estado de Red / Servidor -->
          <div class="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-green-500/10 border border-green-500/30 text-green-400 text-xs font-bold uppercase tracking-wider shadow-sm">
            <span class="w-2 h-2 rounded-full bg-green-500 siam-beacon"></span>
            <span>Sistema Seguro</span>
          </div>

          <!-- Acceso directo a documentación / ayuda -->
          <a href="/ayuda" class="px-3 py-1.5 rounded-lg text-xs font-bold uppercase tracking-widest text-gray-400 hover:text-gold hover:bg-gold/5 transition-colors border border-translucent" title="Manual de Operación">
            Docs
          </a>
        </div>
      `;

      mainArea.insertBefore(topbar, mainArea.firstChild);

      // Evento para el botón móvil
      const mobileBtn = document.getElementById('siam-mobile-menu-btn');
      const sidebar = document.getElementById('sidebar');
      const backdrop = document.querySelector('.siam-sidebar-backdrop');
      if (mobileBtn && sidebar) {
        mobileBtn.addEventListener('click', () => {
          sidebar.classList.toggle('mobile-open');
          if (backdrop) backdrop.classList.toggle('active', sidebar.classList.contains('mobile-open'));
        });
      }
    }
  }

  /* ── 3. ANIMACIONES ESCALONADAS DE ENTRADA (FADE-IN / SLIDE-UP) ── */
  function applyEntryAnimations() {
    // Seleccionar tarjetas, elementos de KPI y filas de tablas
    const cards = document.querySelectorAll('.card-charcoal, .kpi-card, .product-card, .feature-card');
    cards.forEach((card, index) => {
      card.classList.add('siam-animate-entry');
      card.style.animationDelay = `${Math.min(index * 0.05, 0.4)}s`;
    });

    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach((row, index) => {
      row.style.opacity = '0';
      row.classList.add('siam-animate-entry');
      row.style.animationDelay = `${0.1 + Math.min(index * 0.03, 0.5)}s`;
    });
  }

  /* ── 4. SISTEMA DE TOASTS EN ESQUINA SUPERIOR DERECHA (SIAM NOTIFICATIONS) ── */
  function getToastContainer() {
    let container = document.getElementById('siam-toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'siam-toast-container';
      document.body.appendChild(container);
    }
    return container;
  }

  /**
   * Muestra un toast visual elegante en la esquina superior derecha
   * @param {string} msg - Mensaje principal
   * @param {boolean} isError - true para error, false para éxito
   * @param {string} [title] - Título opcional
   */
  window.mostrarToastSiam = function (msg, isError, title) {
    const container = getToastContainer();
    const defaultTitle = isError ? 'Alerta del Sistema' : 'Operación Confirmada';
    const finalTitle = title || defaultTitle;

    const toast = document.createElement('div');
    toast.className = `siam-toast ${isError ? 'siam-toast-error' : 'siam-toast-success'}`;
    toast.style.cssText = `
      position: relative !important;
      display: flex;
      align-items: flex-start;
      gap: 12px;
      padding: 14px 18px;
      background: rgba(18, 18, 22, 0.95);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid ${isError ? 'rgba(239, 68, 68, 0.4)' : 'rgba(212, 175, 55, 0.35)'};
      border-left: 4px solid ${isError ? '#EF4444' : '#10B981'} !important;
      border-radius: 12px;
      box-shadow: 0 16px 40px rgba(0, 0, 0, 0.8), 0 0 20px ${isError ? 'rgba(239, 68, 68, 0.2)' : 'rgba(212, 175, 55, 0.15)'};
      color: #F4F4F5;
      font-size: 13px;
      line-height: 1.45;
      pointer-events: auto;
      opacity: 0;
      transform: translateX(40px);
      transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
      overflow: hidden;
    `;

    // Ícono SVG semántico
    const iconSvg = isError
      ? `<svg class="w-5 h-5 flex-shrink-0 text-red-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>`
      : `<svg class="w-5 h-5 flex-shrink-0 text-green-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`;

    toast.innerHTML = `
      ${iconSvg}
      <div class="flex-1 min-w-0 pr-2">
        <div class="font-bold text-xs uppercase tracking-wider mb-0.5 ${isError ? 'text-red-400' : 'text-gold'}">${finalTitle}</div>
        <div class="text-gray-300 text-xs">${msg}</div>
      </div>
      <button type="button" class="text-gray-500 hover:text-white transition-colors text-sm font-bold p-1 leading-none" aria-label="Cerrar">✕</button>
      <div class="siam-toast-progress" style="
        position: absolute;
        bottom: 0;
        left: 0;
        height: 2px;
        background: ${isError ? '#EF4444' : '#D4AF37'};
        width: 100%;
        transition: width 4s linear;
      "></div>
    `;

    container.appendChild(toast);

    // Animación de entrada
    requestAnimationFrame(() => {
      toast.style.opacity = '1';
      toast.style.transform = 'translateX(0)';
      const progress = toast.querySelector('.siam-toast-progress');
      if (progress) {
        requestAnimationFrame(() => { progress.style.width = '0%'; });
      }
    });

    // Cerrar manualmente
    const closeBtn = toast.querySelector('button');
    let autoCloseTimer;

    function dismissToast() {
      clearTimeout(autoCloseTimer);
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(40px)';
      setTimeout(() => { toast.remove(); }, 350);
    }

    closeBtn.addEventListener('click', dismissToast);

    // Auto-cierre tras 4 segundos
    autoCloseTimer = setTimeout(dismissToast, 4000);
  };

  // Re-enlazar la función global 'mostrarToast' para usar el nuevo diseño
  const oldMostrarToast = window.mostrarToast;
  window.mostrarToast = function (msg, isError) {
    window.mostrarToastSiam(msg, isError);
    if (typeof oldMostrarToast === 'function') {
      try { oldMostrarToast(msg, isError); } catch (e) {}
    }
  };

  /* ── 5. MICROINTERACCIÓN DE ONDA (RIPPLE EFFECT) EN BOTONES ── */
  function setupButtonRipples() {
    const buttons = document.querySelectorAll('.btn-gold, .btn-primary, .btn-buy, .btn-login, #login-btn, #register-btn, #btn-create-user, #btn-create-product, #confirm-buy-btn');
    buttons.forEach(button => {
      button.addEventListener('click', function (e) {
        const rect = button.getBoundingClientRect();
        const circle = document.createElement('span');
        const diameter = Math.max(rect.width, rect.height);
        const radius = diameter / 2;

        circle.style.width = circle.style.height = `${diameter}px`;
        circle.style.left = `${e.clientX - rect.left - radius}px`;
        circle.style.top = `${e.clientY - rect.top - radius}px`;
        circle.style.position = 'absolute';
        circle.style.borderRadius = '50%';
        circle.style.background = 'rgba(255, 255, 255, 0.35)';
        circle.style.transform = 'scale(0)';
        circle.style.animation = 'siamRipple 0.6s linear';
        circle.style.pointerEvents = 'none';

        const existing = button.querySelector('.siam-ripple-span');
        if (existing) existing.remove();

        circle.className = 'siam-ripple-span';
        button.appendChild(circle);

        setTimeout(() => circle.remove(), 600);
      });
    });

    // Inyectar keyframe para ripple si no existe
    if (!document.getElementById('siam-ripple-style')) {
      const style = document.createElement('style');
      style.id = 'siam-ripple-style';
      style.textContent = `
        @keyframes siamRipple {
          to {
            transform: scale(3.5);
            opacity: 0;
          }
        }
      `;
      document.head.appendChild(style);
    }
  }

  /* ── 6. ACCESIBILIDAD Y TECLA ESCAPE PARA MODALES ── */
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      const openModals = document.querySelectorAll('.modal-overlay.open, .modal-overlay:not(.hidden)');
      openModals.forEach(modal => {
        if (typeof window.cerrarModal === 'function') {
          window.cerrarModal(modal.id);
        } else {
          modal.classList.remove('open');
          modal.classList.add('hidden');
          modal.style.display = 'none';
          document.body.style.overflow = '';
        }
      });
      if (typeof window.cerrarFacturaModal === 'function') {
        window.cerrarFacturaModal();
      }
    }
  });

  /* ── INICIALIZACIÓN GLOBAL ── */
  function initAll() {
    setupSidebar();
    setupTopbar();
    applyEntryAnimations();
    setupButtonRipples();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAll);
  } else {
    initAll();
  }
})();
