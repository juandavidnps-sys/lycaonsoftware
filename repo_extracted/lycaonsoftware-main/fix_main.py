js_code = r'''
/* ══════════════════════════════════════════
   RECUPERADOS - Lógica de Usuarios y Admin
   ══════════════════════════════════════════ */

// ── Crear Usuario (Admin) ──
const createUserForm = document.getElementById('create-user-form');
if (createUserForm) {
  createUserForm.addEventListener('submit', async function (e) {
    e.preventDefault();
    const nombre = document.getElementById('new-user-name').value.trim();
    const email = document.getElementById('new-user-email').value.trim();
    const password = document.getElementById('new-user-password').value;
    const role = document.getElementById('new-user-role').value;
    const btn = document.getElementById('btn-create-user');
    const result = document.getElementById('create-user-result');

    btn.disabled = true;
    btn.textContent = 'Registrando...';

    try {
      const res = await fetch('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: nombre, email: email, password: password, role: role })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        result.innerHTML = '<div style="color:#10b981; font-size:.875rem; margin-bottom:.5rem;">Usuario creado exitosamente.</div>';
        setTimeout(() => location.reload(), 1000);
      } else {
        result.innerHTML = '<div style="color:#ef4444; font-size:.875rem; margin-bottom:.5rem;">Error: ' + data.error + '</div>';
        btn.disabled = false;
        btn.textContent = 'Registrar Usuario';
      }
    } catch (err) {
      result.innerHTML = '<div style="color:#ef4444; font-size:.875rem; margin-bottom:.5rem;">Error de conexión.</div>';
      btn.disabled = false;
      btn.textContent = 'Registrar Usuario';
    }
  });
}

// ── Cambiar Rol ──
async function cambiarRol(userId, newRole) {
  if (!confirm(`¿Estás seguro de cambiar el rol a ${newRole}?`)) return;
  try {
    const res = await fetch(`/api/users/${userId}/role`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role: newRole })
    });
    if (res.ok) {
      location.reload();
    } else {
      const data = await res.json();
      alert('Error: ' + data.error);
    }
  } catch (e) {
    alert('Error de conexión');
  }
}

// ── Eliminar Usuario ──
async function eliminarUsuario(userId, name) {
  if (!confirm(`¿Estás seguro de eliminar al usuario ${name}? Esta acción no se puede deshacer.`)) return;
  try {
    const res = await fetch(`/api/users/${userId}`, { method: 'DELETE' });
    if (res.ok) {
      location.reload();
    } else {
      const data = await res.json();
      alert('Error: ' + data.error);
    }
  } catch (e) {
    alert('Error de conexión');
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
      alert('¡Factura enviada por correo exitosamente!');
    } else {
      alert('Error: ' + data.error);
    }
  } catch (error) {
    alert('Error de conexión al enviar el correo.');
  }
}
'''
with open('static/js/main.js', 'a', encoding='utf-8') as f:
    f.write(js_code)
