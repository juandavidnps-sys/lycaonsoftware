import codecs
with codecs.open('templates/dashboard/purchases.html', 'r', 'utf-8') as f:
    content = f.read()

modal = """
<!-- Modal para Calificar Producto -->
<div class="modal-overlay" id="review-modal">
  <div class="modal-box">
    <button class="modal-close" onclick="cerrarModal('review-modal')" title="Cerrar">X</button>
    <h3 class="modal-title" style="font-size:1.25rem; font-weight:800; margin-bottom:1.5rem;">Calificar Producto</h3>
    <div id="review-result" style="margin-bottom:1rem; display:none; padding:1rem; border-radius:4px;"></div>
    <form id="review-form">
      <input type="hidden" id="rev-order-id">
      <input type="hidden" id="rev-product-id">
      <div class="form-group" style="margin-bottom:1.25rem;">
        <label style="display:block; margin-bottom:0.5rem; font-weight:bold; color:var(--text-primary);">Calificación (1 a 5)</label>
        <select id="rev-rating" class="form-input" required style="width:100%;">
          <option value="5">5 - Excelente</option>
          <option value="4">4 - Muy bueno</option>
          <option value="3">3 - Bueno</option>
          <option value="2">2 - Regular</option>
          <option value="1">1 - Malo</option>
        </select>
      </div>
      <div class="form-group" style="margin-bottom:1.25rem;">
        <label style="display:block; margin-bottom:0.5rem; font-weight:bold; color:var(--text-primary);">Comentarios</label>
        <textarea id="rev-comment" class="form-input" required rows="3" placeholder="¿Qué te pareció el producto?" style="width:100%; resize:vertical;"></textarea>
      </div>
      <button type="submit" class="btn-primary" id="btn-submit-review" style="width:100%;">Enviar Calificación</button>
    </form>
  </div>
</div>
<script>
function abrirModalReview(orderId, productId) {
  document.getElementById('rev-order-id').value = orderId;
  document.getElementById('rev-product-id').value = productId;
  document.getElementById('review-form').reset();
  document.getElementById('review-result').style.display = 'none';
  document.getElementById('review-modal').classList.add('active');
}
document.getElementById('review-form').addEventListener('submit', async function(e) {
  e.preventDefault();
  const order_id = document.getElementById('rev-order-id').value;
  const product_id = document.getElementById('rev-product-id').value;
  const rating = parseInt(document.getElementById('rev-rating').value);
  const comment = document.getElementById('rev-comment').value.trim();
  const btn = document.getElementById('btn-submit-review');
  const res = document.getElementById('review-result');
  btn.disabled = true; btn.textContent = 'Enviando...';
  try {
    const response = await fetch('/api/reviews', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ order_id, product_id, rating, comment }) });
    const data = await response.json();
    if(data.success) {
      res.style.display = 'block'; res.className = 'alert-success'; res.textContent = 'Calificación enviada correctamente. ¡Gracias!';
      setTimeout(() => cerrarModal('review-modal'), 2000);
    } else {
      res.style.display = 'block'; res.className = 'alert-error'; res.textContent = data.error || 'Error al enviar.'; btn.disabled = false; btn.textContent = 'Enviar Calificación';
    }
  } catch (err) {
    res.style.display = 'block'; res.className = 'alert-error'; res.textContent = 'Error de conexión.'; btn.disabled = false; btn.textContent = 'Enviar Calificación';
  }
});
</script>
{% endblock %}
"""

content = content.replace("{% endblock %}", modal)

with codecs.open('templates/dashboard/purchases.html', 'w', 'utf-8') as f:
    f.write(content)
