import codecs
with codecs.open('app.py', 'r', 'utf-8') as f:
    content = f.read()

append_code = """
# ══════════════════════════════════════════
#  NUEVOS MÓDULOS DE ADMINISTRACIÓN
# ══════════════════════════════════════════

@app.route('/admin/promotions')
@login_required
@admin_required
def admin_promotions():
    promos = leer_json('promotions.json')
    return render_template('admin/promotions.html', usuario=session['user'], promotions=promos)

@app.route('/admin/logistics')
@login_required
@admin_required
def admin_logistics():
    shipping = leer_json('shipping.json')
    payments = leer_json('payment_methods.json')
    return render_template('admin/logistics.html', usuario=session['user'], shipping=shipping, payments=payments)

@app.route('/admin/reports')
@login_required
@admin_required
def admin_reports():
    return render_template('admin/reports.html', usuario=session['user'])

if __name__ == "__main__":
"""

if append_code not in content:
    content = content.replace("if __name__ == \"__main__\":", append_code)
    with codecs.open('app.py', 'w', 'utf-8') as f:
        f.write(content)
