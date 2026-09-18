import codecs
with codecs.open('app.py', 'r', 'utf-8') as f:
    content = f.read()

append_code = """
import pandas as pd
from io import BytesIO
from flask import make_response

@app.route('/api/export/users')
@login_required
@admin_required
def export_users():
    fmt = request.args.get('format', 'excel')
    usuarios = leer_json('users.json')
    df = pd.DataFrame(usuarios)
    
    if fmt == 'excel':
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Usuarios')
        output.seek(0)
        resp = make_response(output.getvalue())
        resp.headers['Content-Disposition'] = 'attachment; filename=reporte_usuarios.xlsx'
        resp.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        return resp
    elif fmt == 'pdf':
        # Simple HTML to PDF for the report using xhtml2pdf (import deferred or global)
        try:
            from xhtml2pdf import pisa
        except ImportError:
            return "xhtml2pdf no está instalado", 500
            
        html = f"<html><head><style>th, td {{border: 1px solid black; padding: 5px;}} table {{border-collapse: collapse; width: 100%;}}</style></head><body><h2>Reporte de Usuarios Lycaon Security</h2>{df.to_html()}</body></html>"
        output = BytesIO()
        pisa_status = pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=output)
        if pisa_status.err:
            return "Error al generar PDF", 500
        output.seek(0)
        resp = make_response(output.getvalue())
        resp.headers['Content-Disposition'] = 'attachment; filename=reporte_usuarios.pdf'
        resp.headers['Content-Type'] = 'application/pdf'
        return resp
    
    return "Formato no soportado", 400

@app.route('/api/export/inventory')
@login_required
@admin_required
def export_inventory():
    fmt = request.args.get('format', 'excel')
    inv = leer_json('inventory.json')
    df = pd.DataFrame(inv)
    
    if fmt == 'excel':
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Inventario')
        output.seek(0)
        resp = make_response(output.getvalue())
        resp.headers['Content-Disposition'] = 'attachment; filename=reporte_inventario.xlsx'
        resp.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        return resp
    elif fmt == 'pdf':
        try:
            from xhtml2pdf import pisa
        except ImportError:
            return "xhtml2pdf no está instalado", 500
            
        html = f"<html><head><style>th, td {{border: 1px solid black; padding: 5px;}} table {{border-collapse: collapse; width: 100%;}}</style></head><body><h2>Reporte de Inventario Lycaon Security</h2>{df.to_html()}</body></html>"
        output = BytesIO()
        pisa_status = pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=output)
        if pisa_status.err:
            return "Error al generar PDF", 500
        output.seek(0)
        resp = make_response(output.getvalue())
        resp.headers['Content-Disposition'] = 'attachment; filename=reporte_inventario.pdf'
        resp.headers['Content-Type'] = 'application/pdf'
        return resp
    
    return "Formato no soportado", 400
"""

# Inject before the final if __name__ == "__main__":
if "def export_users():" not in content:
    content = content.replace("if __name__ == \"__main__\":", append_code + "\nif __name__ == \"__main__\":")
    with codecs.open('app.py', 'w', 'utf-8') as f:
        f.write(content)
