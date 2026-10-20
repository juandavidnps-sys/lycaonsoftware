import os
import json
import uuid
import smtplib
from io import BytesIO
from datetime import datetime
from functools import wraps
from email.message import EmailMessage

from flask import (
    Flask, render_template, request, session,
    redirect, url_for, jsonify, send_file
)
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import pandas as pd
from xhtml2pdf import pisa

from database import (
    check_db_health, execute_query,
    db_get_users, db_get_user_by_email, db_get_user_by_id, db_create_user,
    db_update_user, db_update_user_role, db_delete_user,
    db_update_user_profile, db_update_user_avatar,
    db_get_inventory, db_create_product, db_update_product, db_delete_product,
    db_get_orders, db_create_order,
    db_create_activity_log, db_get_activity_logs
)

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)
app.secret_key = os.environ.get("SECRET_KEY", "lycaon_software-deep-space-secret-2026")

DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "img", "profiles")
PRODUCT_IMG_DIR = os.path.join(BASE_DIR, "static", "img", "products")
VIDEO_DIR = os.path.join(BASE_DIR, "static", "video")
ALLOWED_EXT = {"png", "jpg", "jpeg", "gif", "webp"}

for d in (UPLOAD_DIR, PRODUCT_IMG_DIR, VIDEO_DIR):
    os.makedirs(d, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS Y DECORADORES
# ══════════════════════════════════════════════════════════════════════════════

def leer_json(archivo):
    """Consulta MySQL como fuente de verdad con fallback a /data/*.json."""
    try:
        if archivo == "users.json":
            return db_get_users() or []
        elif archivo == "inventory.json":
            return db_get_inventory() or []
        elif archivo == "orders.json":
            res = db_get_orders()
            if res: return res
        elif archivo == "activity_log.json":
            return db_get_activity_logs(limit=250) or []
    except Exception as exc:
        print(f"[DB WARN] Fallback a JSON ({archivo}): {exc}")

    ruta = os.path.join(DATA_DIR, archivo)
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def escribir_json(archivo, datos):
    """Guarda copia local de respaldo en formato JSON."""
    ruta = os.path.join(DATA_DIR, archivo)
    try:
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def registrar_actividad(user_email, action, entity_type, entity_id, details=None):
    """Registra auditoría en MySQL."""
    nuevo_log = {
        "id": f"LOG-{str(uuid.uuid4())[:8].upper()}",
        "user_email": user_email,
        "action": action,
        "entity_type": entity_type,
        "entity_id": str(entity_id),
        "ip_address": request.remote_addr or "127.0.0.1",
        "details": json.dumps(details, ensure_ascii=False) if details else None,
        "created_at": datetime.now().isoformat()
    }
    try:
        db_create_activity_log(nuevo_log)
    except Exception:
        pass


def allowed_file(fn):
    return "." in fn and fn.rsplit(".", 1)[1].lower() in ALLOWED_EXT


def video_disponible():
    if os.path.exists(VIDEO_DIR):
        for ext in ("mp4", "webm", "ogg", "mov"):
            for nombre in os.listdir(VIDEO_DIR):
                if nombre.lower().endswith(f".{ext}"):
                    return f"video/{nombre}"
    return None


def requiere_login(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("pagina_login"))
        return f(*args, **kwargs)
    return wrapper


def requiere_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("pagina_login"))
        if session["user"].get("role") not in ["administrador", "operador"]:
            return redirect(url_for("dashboard_general"))
        return f(*args, **kwargs)
    return wrapper


def inicializar_usuarios():
    usuarios = db_get_users() or leer_json("users.json")
    passwords_demo = {
        "admin@lycaonsoftware.com": "admin123",
        "juandavidnps@gmail.com":   "cliente123",
        "santosolano1602@gmail.com":"cliente123",
    }
    for u in usuarios:
        if "pbkdf2:sha256:600000$salt$hashed" in u.get("password_hash", ""):
            pwd = passwords_demo.get(u["email"], "changeme123")
            execute_query("UPDATE users SET password_hash = %s WHERE id = %s", (generate_password_hash(pwd), u["id"]))


def generar_pdf_factura(pedido, invoice_id, user):
    html = render_template('factura_pdf.html', pedido=pedido, invoice_id=invoice_id, user=user, now=datetime.now())
    stream = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=stream)
    stream.seek(0)
    return stream, pisa_status.err


# ══════════════════════════════════════════════════════════════════════════════
# VISTAS — Páginas Públicas y Dashboard
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def pagina_inicio():
    return render_template("index.html", video=video_disponible(), usuario=session.get("user"))


@app.route("/login", methods=["GET", "POST"])
def pagina_login():
    if "user" in session:
        rol = session["user"].get("role")
        return redirect(url_for("dashboard_general" if rol in ("administrador", "operador") else "dashboard_tienda"))
    return render_template("login.html")


@app.route("/logout")
def cerrar_sesion():
    email = session.get("user", {}).get("email", "desconocido")
    session.clear()
    registrar_actividad(email, "logout", "user", email)
    return redirect(url_for("pagina_inicio"))


@app.route("/tienda")
def tienda_publica():
    return render_template("tienda_publica.html", productos=leer_json("inventory.json"), usuario=session.get("user"))


@app.route("/ayuda")
def pagina_ayuda():
    return render_template("ayuda.html", usuario=session.get("user"))


@app.route("/dashboard")
@requiere_login
def dashboard_general():
    inv = leer_json("inventory.json")
    tareas = leer_json("tasks.json")
    pedidos = leer_json("orders.json")
    user_email = session["user"].get("email", "")

    categorias, salud, ingresos = {}, {"active": 0, "low-stock": 0, "out-of-stock": 0}, {}
    for p in inv:
        cat = p.get("category", "General")
        categorias[cat] = categorias.get(cat, 0) + 1
        st = p.get("status", "active")
        salud[st] = salud.get(st, 0) + 1

    for p in pedidos:
        f = p.get("created_at", "")[:10]
        ingresos[f] = ingresos.get(f, 0) + p.get("total", 0.0)

    return render_template(
        "dashboard/index.html",
        usuario=session["user"],
        metricas={
            "total_clientes": len(leer_json("users.json")),
            "catalogo_size": len(inv),
            "valor_inventario": f"${sum(p['price'] * p['stock'] for p in inv):,.2f}",
            "tareas_pendientes": sum(1 for t in tareas if t.get("status") in ("pending", "in-progress")),
        },
        categorias=categorias, salud=salud, tareas=tareas, ingresos=ingresos,
        mis_pedidos=[p for p in pedidos if p.get("user_email") == user_email],
        productos_destacados=[p for p in inv if p.get("status") == "active"][:6]
    )


@app.route("/dashboard/purchases")
@requiere_login
def dashboard_compras():
    pedidos = [p for p in leer_json("orders.json") if p.get("user_email") == session["user"]["email"]]
    return render_template("dashboard/purchases.html", usuario=session["user"], pedidos=pedidos)


@app.route("/dashboard/store")
@requiere_login
def dashboard_tienda():
    return render_template("dashboard/store.html", usuario=session["user"], productos=leer_json("inventory.json"))


@app.route("/admin/tienda")
@requiere_admin
def admin_tienda():
    return render_template("admin/tienda.html", usuario=session["user"], productos=leer_json("inventory.json"))


@app.route("/dashboard/users")
@requiere_admin
def dashboard_usuarios():
    usuarios = [{k: v for k, v in u.items() if k != "password_hash"} for u in leer_json("users.json")]
    return render_template("dashboard/users.html", usuario=session["user"], usuarios=usuarios)


@app.route("/dashboard/activity")
@requiere_admin
def dashboard_actividad():
    logs = leer_json("activity_log.json")
    f = request.args.get("filtro", "").lower()
    if f: logs = [l for l in logs if f in l.get("action", "").lower()]
    return render_template("dashboard/activity.html", usuario=session["user"], logs=logs, filtro=f)


@app.route("/dashboard/profile")
@requiere_login
def dashboard_perfil():
    user = db_get_user_by_id(session["user"]["id"]) or session["user"]
    session["user"]["name"] = user.get("name", session["user"]["name"])
    session["user"]["avatar"] = user.get("avatar", session["user"].get("avatar", ""))
    session.modified = True
    return render_template("dashboard/profile.html", usuario=session["user"], user_data=user)


@app.route("/dashboard/suggestions")
@requiere_login
def dash_suggestions():
    return render_template("dashboard/suggestions.html", usuario=session["user"])


@app.route("/admin/promotions")
@requiere_admin
def admin_promotions():
    return render_template("admin/promotions.html", usuario=session["user"], promotions=leer_json("promotions.json"))


@app.route("/admin/logistics")
@requiere_admin
def admin_logistics():
    return render_template("admin/logistics.html", usuario=session["user"], shipping=leer_json("shipping.json"), payments=leer_json("payment_methods.json"))


@app.route("/admin/reports")
@requiere_admin
def admin_reports():
    return render_template("admin/reports.html", usuario=session["user"])


# ══════════════════════════════════════════════════════════════════════════════
# API — Autenticación y Perfil
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/api/auth/login", methods=["POST"])
def api_login():
    d = request.get_json() or {}
    email, pwd = d.get("email", "").strip().lower(), d.get("password", "")
    if not email or not pwd:
        return jsonify({"success": False, "error": "Llena todos los campos."}), 400

    u = db_get_user_by_email(email)
    if not u or not check_password_hash(u["password_hash"], pwd):
        return jsonify({"success": False, "error": "Credenciales inválidas."}), 401

    session["user"] = {"id": u["id"], "name": u["name"], "email": u["email"], "role": u["role"], "avatar": u.get("avatar", "")}
    registrar_actividad(email, "login", "user", u["id"], {"result": "success"})
    return jsonify({"success": True, "user": session["user"]})


@app.route("/api/auth/register", methods=["POST"])
def api_registro():
    d = request.get_json() or {}
    nombre, email, pwd = d.get("name", "").strip(), d.get("email", "").strip().lower(), d.get("password", "")
    if not nombre or not email or len(pwd) < 6:
        return jsonify({"success": False, "error": "Nombre requerido y clave mínimo 6 caracteres."}), 400

    if db_get_user_by_email(email):
        return jsonify({"success": False, "error": "Este correo ya está registrado."}), 409

    uid = f"U{str(uuid.uuid4())[:6].upper()}"
    db_create_user(uid, nombre, email, generate_password_hash(pwd), role="cliente")
    session["user"] = {"id": uid, "name": nombre, "email": email, "role": "cliente", "avatar": ""}
    registrar_actividad(email, "register", "user", uid)
    return jsonify({"success": True, "user": session["user"]})


@app.route("/api/profile/update", methods=["POST", "PUT"])
@requiere_login
def api_actualizar_perfil():
    d = request.get_json() or {}
    nombre = d.get("name", "").strip()
    nueva_clave = d.get("password", "").strip() if d.get("password") else None
    if not nombre or len(nombre) < 2:
        return jsonify({"success": False, "error": "Nombre mínimo 2 caracteres."}), 400

    p_hash = generate_password_hash(nueva_clave) if nueva_clave and len(nueva_clave) >= 6 else None
    db_update_user_profile(session["user"]["id"], nombre, p_hash)
    session["user"]["name"] = nombre
    session.modified = True
    registrar_actividad(session["user"]["email"], "profile_updated", "user", session["user"]["id"])
    return jsonify({"success": True, "message": "Perfil actualizado exitosamente.", "user": session["user"]})


@app.route("/api/profile/avatar", methods=["POST"])
@requiere_login
def api_subir_avatar():
    f = request.files.get("avatar")
    if not f or f.filename == "" or not allowed_file(f.filename):
        return jsonify({"success": False, "error": "Archivo no válido (usa jpg, png, webp)."}), 400

    ext = f.filename.rsplit(".", 1)[1].lower()
    nombre = f"avatar_{session['user']['id']}.{ext}"
    f.save(os.path.join(UPLOAD_DIR, nombre))
    ruta_rel = f"img/profiles/{nombre}"

    db_update_user_avatar(session["user"]["id"], ruta_rel)
    session["user"]["avatar"] = ruta_rel
    session.modified = True
    registrar_actividad(session["user"]["email"], "avatar_updated", "user", session["user"]["id"])
    return jsonify({"success": True, "avatar_url": url_for("static", filename=ruta_rel)})


# ══════════════════════════════════════════════════════════════════════════════
# API — Órdenes y Facturación
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/api/orders", methods=["POST"])
@requiere_login
def api_crear_pedido():
    d = request.get_json() or {}
    items_raw = d.get("items") or [{"product_id": d.get("product_id"), "cantidad": int(d.get("cantidad", 1))}]
    inv = leer_json("inventory.json")

    items, total = [], 0.0
    for it in items_raw:
        pid = it.get("product_id") or it.get("id")
        cant = int(it.get("cantidad") or it.get("quantity") or 1)
        prod = next((p for p in inv if p["id"] == pid), None)
        if not prod or prod["stock"] < cant:
            return jsonify({"success": False, "error": f"Stock insuficiente para {pid}."}), 400
        sub = round(prod["price"] * cant, 2)
        total += sub
        items.append({"product_id": pid, "product_name": prod["name"], "category": prod.get("category", "General"), "price": prod["price"], "cantidad": cant, "subtotal": sub})

    total = round(total, 2)
    inv_id = f"INV-{str(uuid.uuid4())[:8].upper()}"
    nombres = ", ".join(i["product_name"] for i in items)[:60]
    pedido = {
        "id": f"ORD-{str(uuid.uuid4())[:8].upper()}",
        "user_id": session["user"]["id"],
        "user_email": session["user"]["email"],
        "product_id": items[0]["product_id"] if len(items) == 1 else None,
        "product_name": nombres,
        "items": items,
        "cantidad": sum(i["cantidad"] for i in items),
        "subtotal": total, "discount_amount": 0.0, "total": total,
        "status": "paid", "invoice_id": inv_id, "created_at": datetime.now().isoformat()
    }

    db_create_order(pedido)
    for it in items:
        execute_query("UPDATE inventory SET stock = GREATEST(0, stock - %s) WHERE id = %s", (it["cantidad"], it["product_id"]))

    registrar_actividad(session["user"]["email"], "order_created", "order", pedido["id"], {"total": total, "invoice_id": inv_id})
    return jsonify({"success": True, "order": pedido, "invoice_id": inv_id, "message": "Compra y facturación completada exitosamente."})


@app.route("/api/invoices/<invoice_id>/download")
@requiere_login
def descargar_factura(invoice_id):
    p = next((o for o in leer_json("orders.json") if o.get("invoice_id") == invoice_id), None)
    if not p or (p.get("user_email") != session["user"]["email"] and session["user"].get("role") != "administrador"):
        return jsonify({"success": False, "error": "No encontrado o no autorizado."}), 404

    stream, err = generar_pdf_factura(p, invoice_id, session["user"])
    if err: return jsonify({"success": False, "error": "Error generando PDF."}), 500
    return send_file(stream, as_attachment=True, download_name=f"Factura_{invoice_id}.pdf", mimetype="application/pdf")


@app.route("/api/invoices/<invoice_id>/email", methods=["POST"])
@app.route("/api/invoices/<invoice_id>/send", methods=["POST"])
@requiere_login
def enviar_factura_correo(invoice_id):
    p = next((o for o in leer_json("orders.json") if o.get("invoice_id") == invoice_id), None)
    if not p: return jsonify({"success": False, "error": "Factura no encontrada."}), 404

    smtp_s, smtp_u, smtp_p = os.environ.get("SMTP_SERVER"), os.environ.get("SMTP_USER"), os.environ.get("SMTP_PASSWORD")
    if not smtp_s or not smtp_u or not smtp_p:
        registrar_actividad(session["user"]["email"], "invoice_email_simulated", "invoice", invoice_id)
        return jsonify({"success": True, "simulated": True, "message": f"Factura {invoice_id} enviada virtualmente a {session['user']['email']}."})

    try:
        stream, _ = generar_pdf_factura(p, invoice_id, session["user"])
        msg = EmailMessage()
        msg["Subject"] = f"Factura Comercial Lycaon Security — {invoice_id}"
        msg["From"] = smtp_u
        msg["To"] = session["user"]["email"]
        msg.set_content(f"Estimado(a) {session['user']['name']},\n\nAdjunto comprobante de compra {p['id']}.\nTotal: ${p['total']:,.2f} USD")
        msg.add_attachment(stream.getvalue(), maintype="application", subtype="pdf", filename=f"Factura_{invoice_id}.pdf")
        with smtplib.SMTP(smtp_s, int(os.environ.get("SMTP_PORT", 587))) as s:
            s.starttls()
            s.login(smtp_u, smtp_p)
            s.send_message(msg)
        return jsonify({"success": True, "message": "Factura despachada por correo."})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


# ══════════════════════════════════════════════════════════════════════════════
# API — Gestión de Usuarios y Productos (Admin)
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/api/users", methods=["POST"])
@app.route("/api/admin/users", methods=["POST"])
@requiere_admin
def api_crear_usuario():
    d = request.get_json() or {}
    nombre, email, pwd = d.get("name", "").strip(), d.get("email", "").strip().lower(), d.get("password") or "Temporal123!"
    rol = "operador" if d.get("role") == "trabajador" else d.get("role", "cliente")
    if not nombre or not email or len(pwd) < 6:
        return jsonify({"success": False, "error": "Datos incompletos o clave corta."}), 400

    if db_get_user_by_email(email):
        return jsonify({"success": False, "error": "Correo ya registrado."}), 409

    uid = f"U{str(uuid.uuid4())[:6].upper()}"
    db_create_user(uid, nombre, email, generate_password_hash(pwd), role=rol)
    registrar_actividad(session["user"]["email"], "user_created", "user", uid)
    return jsonify({"success": True, "user": {"id": uid, "name": nombre, "email": email, "role": rol}})


@app.route("/api/users/<user_id>/edit", methods=["POST"])
@requiere_admin
def api_editar_usuario(user_id):
    d = request.get_json() or {}
    nombre, email, pwd = d.get("name", "").strip(), d.get("email", "").strip().lower(), d.get("password", "")
    rol = "operador" if d.get("role") == "trabajador" else d.get("role", "")
    p_hash = generate_password_hash(pwd) if pwd and len(pwd) >= 6 else None
    db_update_user(user_id, nombre, email, rol, p_hash)
    registrar_actividad(session["user"]["email"], "user_edited", "user", user_id)
    return jsonify({"success": True})


@app.route("/api/users/<user_id>/role", methods=["PATCH"])
@requiere_admin
def api_cambiar_rol(user_id):
    rol = "operador" if request.get_json().get("role") == "trabajador" else request.get_json().get("role")
    db_update_user_role(user_id, rol)
    registrar_actividad(session["user"]["email"], "role_change", "user", user_id, {"role": rol})
    return jsonify({"success": True})


@app.route("/api/users/<user_id>", methods=["DELETE"])
@requiere_admin
def api_eliminar_usuario(user_id):
    if user_id == session["user"]["id"]:
        return jsonify({"success": False, "error": "No puedes eliminar tu propia cuenta."}), 400
    db_delete_user(user_id)
    registrar_actividad(session["user"]["email"], "user_deleted", "user", user_id)
    return jsonify({"success": True})


@app.route("/api/products", methods=["POST"])
@requiere_admin
def api_crear_producto():
    d = request.get_json() or {}
    nombre, cat, precio, stock = d.get("name", "").strip(), d.get("category", "").strip(), float(d.get("price", 0)), int(d.get("stock", 0))
    if not nombre or not cat:
        return jsonify({"success": False, "error": "Nombre y categoría son requeridos."}), 400

    pid = f"P{str(uuid.uuid4())[:5].upper()}"
    st = "out-of-stock" if stock == 0 else ("low-stock" if stock <= 3 else "active")
    db_create_product(pid, nombre, cat, stock, precio, st, "/static/img/placeholder.svg")
    registrar_actividad(session["user"]["email"], "product_created", "product", pid)
    return jsonify({"success": True, "product": {"id": pid, "name": nombre, "price": precio, "stock": stock}})


@app.route("/api/products/<product_id>", methods=["PUT", "PATCH", "POST"])
@requiere_admin
def api_actualizar_producto(product_id):
    d = request.get_json() or {}
    inv = leer_json("inventory.json")
    p = next((item for item in inv if item["id"] == product_id), None)
    if not p: return jsonify({"success": False, "error": "Producto no encontrado."}), 404

    nombre = str(d.get("name", p["name"])).strip()
    cat = str(d.get("category", p["category"])).strip()
    precio = float(d.get("price", p["price"]))
    stock = int(d.get("stock", p["stock"]))
    st = "out-of-stock" if stock == 0 else ("low-stock" if stock <= 3 else "active")

    db_update_product(product_id, nombre, cat, stock, precio, st, p.get("image_url"))
    registrar_actividad(session["user"]["email"], "product_updated", "product", product_id)
    return jsonify({"success": True, "product": {"id": product_id, "name": nombre, "price": precio, "stock": stock}})


@app.route("/api/products/<product_id>", methods=["DELETE"])
@requiere_admin
def api_eliminar_producto(product_id):
    db_delete_product(product_id)
    registrar_actividad(session["user"]["email"], "product_deleted", "product", product_id)
    return jsonify({"success": True})


@app.route("/api/products/<product_id>/image", methods=["POST"])
@requiere_admin
def api_subir_imagen_producto(product_id):
    f = request.files.get("image")
    if not f or not allowed_file(f.filename):
        return jsonify({"success": False, "error": "Imagen no permitida."}), 400

    ext = f.filename.rsplit(".", 1)[1].lower()
    fn = f"prod_{product_id}_{str(uuid.uuid4())[:6]}.{ext}"
    f.save(os.path.join(PRODUCT_IMG_DIR, fn))
    ruta_rel = f"/static/img/products/{fn}"

    execute_query("UPDATE inventory SET image_url = %s, updated_at = NOW() WHERE id = %s", (ruta_rel, product_id))
    registrar_actividad(session["user"]["email"], "product_image_updated", "product", product_id)
    return jsonify({"success": True, "image_url": ruta_rel})


# ══════════════════════════════════════════════════════════════════════════════
# API — Exportaciones, Tareas, Sugerencias y Reseñas
# ══════════════════════════════════════════════════════════════════════════════

def _exportar_dataframe(df, nombre, fmt):
    if fmt == "pdf":
        html = f"<html><body><h2>Reporte: {nombre}</h2>{df.to_html()}</body></html>"
        s = BytesIO()
        pisa.CreatePDF(BytesIO(html.encode("utf-8")), dest=s)
        s.seek(0)
        return send_file(s, as_attachment=True, download_name=f"{nombre}.pdf", mimetype="application/pdf")
    s = BytesIO()
    df.to_csv(s, index=False, encoding="utf-8-sig")
    s.seek(0)
    return send_file(s, as_attachment=True, download_name=f"{nombre}.csv", mimetype="text/csv")


@app.route("/api/export/inventory")
@requiere_admin
def exportar_inventario():
    inv = leer_json("inventory.json")
    df = pd.DataFrame(inv)[['id', 'name', 'category', 'price', 'stock', 'status', 'created_at']] if inv else pd.DataFrame()
    return _exportar_dataframe(df, "Inventario_Lycaon", request.args.get("format", "csv"))


@app.route("/api/export/users")
@requiere_admin
def exportar_usuarios():
    users = leer_json("users.json")
    df = pd.DataFrame(users).drop(columns=['password_hash'], errors='ignore') if users else pd.DataFrame()
    return _exportar_dataframe(df, "Usuarios_Lycaon", request.args.get("format", "csv"))


@app.route("/api/tasks", methods=["GET", "POST"])
@requiere_login
def api_tareas():
    if request.method == "POST":
        d = request.get_json() or {}
        emp = db_get_user_by_id(d.get("employee_id"))
        t = {"id": f"T{str(uuid.uuid4())[:6].upper()}", "employee_id": d.get("employee_id"), "employee_name": emp["name"] if emp else "Operador", "title": d.get("title"), "time_window": d.get("time_window", ""), "status": "pending", "priority": d.get("priority", "medium"), "created_at": datetime.now().isoformat()}
        ts = leer_json("tasks.json")
        ts.append(t)
        escribir_json("tasks.json", ts)
        return jsonify({"success": True, "task": t})
    return jsonify({"success": True, "data": leer_json("tasks.json")})


@app.route("/api/tasks/<task_id>/status", methods=["PATCH"])
@requiere_login
def api_cambiar_estado_tarea(task_id):
    st = (request.get_json() or {}).get("status")
    ts = leer_json("tasks.json")
    for t in ts:
        if t["id"] == task_id:
            t["status"] = st
            escribir_json("tasks.json", ts)
            return jsonify({"success": True})
    return jsonify({"success": False, "error": "No encontrada."}), 404


@app.route('/api/suggestions', methods=['POST'])
@requiere_login
def api_suggestions():
    d = request.get_json() or {}
    s = leer_json('suggestions.json')
    s.append({'id': f'S{len(s)+1}', 'user_id': session['user']['id'], 'type': d.get('type'), 'message': d.get('message'), 'date': datetime.now().isoformat()})
    escribir_json('suggestions.json', s)
    return jsonify({'success': True})


@app.route('/api/reviews', methods=['POST'])
@requiere_login
def api_reviews():
    d = request.get_json() or {}
    r = leer_json('reviews.json')
    r.append({'id': f'R{len(r)+1}', 'user_id': session['user']['id'], 'order_id': d.get('order_id'), 'product_id': d.get('product_id'), 'rating': d.get('rating'), 'comment': d.get('comment'), 'date': datetime.now().isoformat()})
    escribir_json('reviews.json', r)
    return jsonify({'success': True})


# ══════════════════════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    inicializar_usuarios()
    db = check_db_health()
    print(f"\n[LYCAON SECURITY] Servidor activo en http://localhost:5000 | MySQL: {db['status'].upper()} ({db['host']}:{db['port']})\n")
    app.run(debug=True, port=5000)
