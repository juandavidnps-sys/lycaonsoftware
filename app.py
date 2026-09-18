"""
╔══════════════════════════════════════════════════════════════════╗
║              LYCAON SOFTWARE — Servidor Flask Principal v2          ║
║   Stack: Python Flask + JSON + HTML/CSS/JS vanilla               ║
║   Nuevas funciones:                                              ║
║     - Tienda pública (/tienda)                                   ║
║     - Admin tienda con crear/editar productos (/admin/tienda)    ║
║     - Crear usuarios desde admin                                 ║
║     - Subir foto de perfil                                       ║
╚══════════════════════════════════════════════════════════════════╝
"""

import json
import os
import uuid
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, session,
    redirect, url_for, jsonify, send_file
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# Librerías nuevas (PDF, Correo, Pandas)
import tempfile
import pandas as pd
from xhtml2pdf import pisa
from io import BytesIO
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Cargar variables de entorno (para credenciales de correo)
load_dotenv()

# ──────────────────────────────────────────
# Configuración de la aplicación
# ──────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "lycaon_software-deep-space-secret-2026")

DATA_DIR   = os.path.join(os.path.dirname(__file__), "data")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "static", "img", "profiles")
PRODUCT_IMG_DIR = os.path.join(os.path.dirname(__file__), "static", "img", "products")
VIDEO_DIR  = os.path.join(os.path.dirname(__file__), "static", "video")

# Extensiones permitidas para fotos de perfil y productos
ALLOWED_EXT = {"png", "jpg", "jpeg", "gif", "webp"}

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PRODUCT_IMG_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR,  exist_ok=True)


# ══════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════

def leer_json(nombre_archivo):
    ruta = os.path.join(DATA_DIR, nombre_archivo)
    if not os.path.exists(ruta):
        return []
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def escribir_json(nombre_archivo, datos):
    ruta = os.path.join(DATA_DIR, nombre_archivo)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


def registrar_actividad(user_email, action, entity_type, entity_id, details=None):
    logs = leer_json("activity_log.json")
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
    logs.insert(0, nuevo_log)
    escribir_json("activity_log.json", logs)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


def video_disponible():
    """Busca cualquier video en static/video/ y devuelve su ruta relativa o None."""
    for ext in ("mp4", "webm", "ogg", "mov"):
        for nombre in os.listdir(VIDEO_DIR):
            if nombre.lower().endswith(f".{ext}"):
                return f"video/{nombre}"
    return None


# ══════════════════════════════════════════
#  DECORADORES
# ══════════════════════════════════════════

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
        if session["user"].get("role") != "administrador":
            return redirect(url_for("dashboard_general"))
        return f(*args, **kwargs)
    return wrapper


# ══════════════════════════════════════════
#  INICIALIZACIÓN
# ══════════════════════════════════════════

def inicializar_usuarios():
    usuarios = leer_json("users.json")
    modificado = False
    passwords_demo = {
        "admin@lycaonsoftware.com":          "admin123",
        "juandavidnps@gmail.com":      "cliente123",
        "santosolano1602@gmail.com":   "cliente123",
    }
    for usuario in usuarios:
        if "pbkdf2:sha256:600000$salt$hashed" in usuario.get("password_hash", ""):
            email = usuario["email"]
            password_real = passwords_demo.get(email, "changeme123")
            usuario["password_hash"] = generate_password_hash(password_real)
            modificado = True
    if modificado:
        escribir_json("users.json", usuarios)
        print("[OK] Usuarios inicializados con contrasenas reales.")


# ══════════════════════════════════════════
#  RUTAS — Páginas públicas
# ══════════════════════════════════════════

@app.route("/")
def pagina_inicio():
    video = video_disponible()
    return render_template("index.html", video=video, usuario=session.get("user"))


@app.route("/login")
def pagina_login():
    if "user" in session:
        return redirect(url_for("dashboard_general"))
    return render_template("login.html")


@app.route("/logout")
def cerrar_sesion():
    user_email = session.get("user", {}).get("email", "desconocido")
    session.clear()
    registrar_actividad(user_email, "logout", "user", user_email)
    return redirect(url_for("pagina_inicio"))


# ──────────────────────────────────────────
# Tienda PÚBLICA (sin login)
# ──────────────────────────────────────────

@app.route("/tienda")
def tienda_publica():
    """
    Tienda pública — accesible para cualquier visitante sin login.
    Muestra los productos disponibles con opción de ir al login para comprar.
    """
    inventario = leer_json("inventory.json")
    return render_template(
        "tienda_publica.html",
        productos=inventario,
        usuario=session.get("user")
    )

@app.route("/ayuda")
def pagina_ayuda():
    """Manual de usuario de la plataforma."""
    return render_template("ayuda.html", usuario=session.get("user"))


# ══════════════════════════════════════════
#  RUTAS — Dashboard (requiere login)
# ══════════════════════════════════════════

@app.route("/dashboard")
@requiere_login
def dashboard_general():
    inventario = leer_json("inventory.json")
    tareas     = leer_json("tasks.json")
    pedidos    = leer_json("orders.json")

    total_usuarios    = len(leer_json("users.json"))
    total_productos   = len(inventario)
    valor_inventario  = sum(p["price"] * p["stock"] for p in inventario)
    tareas_pendientes = sum(1 for t in tareas if t["status"] in ("pending", "in-progress"))

    categorias = {}
    for p in inventario:
        cat = p["category"]
        categorias[cat] = categorias.get(cat, 0) + 1

    salud = {"active": 0, "low-stock": 0, "out-of-stock": 0}
    for p in inventario:
        salud[p["status"]] = salud.get(p["status"], 0) + 1

    ingresos_dias = {}
    for pedido in pedidos:
        fecha = pedido["created_at"][:10]
        ingresos_dias[fecha] = ingresos_dias.get(fecha, 0) + pedido["total"]

    return render_template(
        "dashboard/index.html",
        usuario=session["user"],
        metricas={
            "total_clientes": total_usuarios,
            "catalogo_size":    total_productos,
            "valor_inventario": f"${valor_inventario:,.2f}",
            "tareas_pendientes": tareas_pendientes,
        },
        categorias=categorias,
        salud=salud,
        tareas=tareas,
        ingresos=ingresos_dias,
    )


@app.route("/dashboard/purchases")
@requiere_login
def dashboard_compras():
    pedidos    = leer_json("orders.json")
    user_email = session["user"]["email"]
    mis_pedidos = [p for p in pedidos if p["user_email"] == user_email]
    return render_template(
        "dashboard/purchases.html",
        usuario=session["user"],
        pedidos=mis_pedidos
    )


@app.route("/dashboard/store")
@requiere_login
def dashboard_tienda():
    """Tienda para usuarios autenticados — permite comprar."""
    inventario = leer_json("inventory.json")
    return render_template(
        "dashboard/store.html",
        usuario=session["user"],
        productos=inventario
    )


# ──────────────────────────────────────────
# Tienda ADMIN — gestión de productos
# ──────────────────────────────────────────

@app.route("/admin/tienda")
@requiere_admin
def admin_tienda():
    """
    Panel de administración de la tienda.
    Permite ver, crear, y gestionar productos del catálogo.
    """
    inventario = leer_json("inventory.json")
    return render_template(
        "admin/tienda.html",
        usuario=session["user"],
        productos=inventario
    )


@app.route("/dashboard/users")
@requiere_admin
def dashboard_usuarios():
    usuarios = leer_json("users.json")
    usuarios_seguros = [
        {k: v for k, v in u.items() if k != "password_hash"}
        for u in usuarios
    ]
    return render_template(
        "dashboard/users.html",
        usuario=session["user"],
        usuarios=usuarios_seguros
    )


@app.route("/dashboard/activity")
@requiere_admin
def dashboard_actividad():
    logs   = leer_json("activity_log.json")
    filtro = request.args.get("filtro", "").lower()
    if filtro:
        logs = [l for l in logs if filtro in l.get("action", "").lower()]
    return render_template(
        "dashboard/activity.html",
        usuario=session["user"],
        logs=logs,
        filtro=filtro
    )


@app.route("/dashboard/profile")
@requiere_login
def dashboard_perfil():
    # Obtener datos actualizados del usuario desde JSON
    usuarios = leer_json("users.json")
    user_data = next(
        (u for u in usuarios if u["email"] == session["user"]["email"]),
        session["user"]
    )
    return render_template(
        "dashboard/profile.html",
        usuario=session["user"],
        user_data=user_data
    )


# ══════════════════════════════════════════
#  API — Autenticación
# ══════════════════════════════════════════

@app.route("/api/auth/login", methods=["POST"])
def api_login():
    datos    = request.get_json()
    email    = datos.get("email", "").strip().lower()
    password = datos.get("password", "")

    if not email or not password:
        return jsonify({"success": False, "error": "Llena todos los campos."}), 400

    usuarios = leer_json("users.json")
    usuario  = next((u for u in usuarios if u["email"].lower() == email), None)

    if not usuario or not check_password_hash(usuario["password_hash"], password):
        return jsonify({"success": False, "error": "Credenciales invalidas."}), 401

    datos_sesion = {
        "id":     usuario["id"],
        "name":   usuario["name"],
        "email":  usuario["email"],
        "role":   usuario["role"],
        "avatar": usuario.get("avatar", "")
    }
    session["user"] = datos_sesion
    registrar_actividad(email, "login", "user", usuario["id"], {"result": "success"})
    return jsonify({"success": True, "user": datos_sesion})


@app.route("/api/auth/register", methods=["POST"])
def api_registro():
    datos    = request.get_json()
    nombre   = datos.get("name", "").strip()
    email    = datos.get("email", "").strip().lower()
    password = datos.get("password", "")
    phone    = datos.get("phone", "").strip()
    address  = datos.get("address", "").strip()

    if not nombre or not email or not password or not phone or not address:
        return jsonify({"success": False, "error": "Llena todos los campos."}), 400
    if len(password) < 6:
        return jsonify({"success": False, "error": "Contrasena minimo 6 caracteres."}), 400

    usuarios = leer_json("users.json")
    if any(u["email"].lower() == email for u in usuarios):
        return jsonify({"success": False, "error": "Este correo ya esta registrado."}), 409

    nuevo_usuario = {
        "id":            f"U{len(usuarios) + 1}",
        "name":          nombre,
        "email":         email,
        "phone":         phone,
        "address":       address,
        "password_hash": generate_password_hash(password),
        "role":          "cliente",
        "verified":      True,
        "avatar":        "",
        "created_at":    datetime.now().isoformat()
    }
    usuarios.append(nuevo_usuario)
    escribir_json("users.json", usuarios)

    datos_sesion = {
        "id":     nuevo_usuario["id"],
        "name":   nuevo_usuario["name"],
        "email":  nuevo_usuario["email"],
        "role":   nuevo_usuario["role"],
        "avatar": ""
    }
    session["user"] = datos_sesion
    registrar_actividad(email, "register", "user", nuevo_usuario["id"])
    return jsonify({"success": True, "user": datos_sesion})


# ══════════════════════════════════════════
#  API — Compras / Pedidos
# ══════════════════════════════════════════

@app.route("/api/orders", methods=["POST"])
@requiere_login
def api_crear_pedido():
    datos      = request.get_json()
    product_id = datos.get("product_id")
    cantidad   = int(datos.get("cantidad", 1))

    if not product_id or cantidad < 1:
        return jsonify({"success": False, "error": "Datos invalidos."}), 400

    inventario = leer_json("inventory.json")
    producto   = next((p for p in inventario if p["id"] == product_id), None)

    if not producto:
        return jsonify({"success": False, "error": "Producto no encontrado."}), 404
    if producto["stock"] < cantidad:
        return jsonify({"success": False, "error": f"Stock insuficiente ({producto['stock']} disponibles)."}), 400

    total      = round(producto["price"] * cantidad, 2)
    invoice_id = f"INV-{str(uuid.uuid4())[:8].upper()}"

    nuevo_pedido = {
        "id":              f"ORD-{str(uuid.uuid4())[:8].upper()}",
        "user_id":         session["user"]["id"],
        "user_email":      session["user"]["email"],
        "product_id":      product_id,
        "product_name":    producto["name"],
        "cantidad":        cantidad,
        "subtotal":        total,
        "discount_amount": 0.00,
        "total":           total,
        "status":          "paid",
        "invoice_id":      invoice_id,
        "created_at":      datetime.now().isoformat()
    }

    pedidos = leer_json("orders.json")
    pedidos.append(nuevo_pedido)
    escribir_json("orders.json", pedidos)

    for p in inventario:
        if p["id"] == product_id:
            p["stock"] -= cantidad
            p["status"] = "out-of-stock" if p["stock"] == 0 else ("low-stock" if p["stock"] <= 3 else "active")
            break
    escribir_json("inventory.json", inventario)

    registrar_actividad(
        session["user"]["email"], "order_created", "order",
        nuevo_pedido["id"],
        {"product": producto["name"], "total": total}
    )
    return jsonify({"success": True, "order": nuevo_pedido})


@app.route("/api/invoices/<invoice_id>/download")
@requiere_login
def descargar_factura(invoice_id):
    pedidos = leer_json("orders.json")
    pedido  = next((p for p in pedidos if p.get("invoice_id") == invoice_id), None)

    if not pedido:
        return jsonify({"success": False, "error": "Factura no encontrada."}), 404

    user = session["user"]
    if pedido["user_email"] != user["email"] and user["role"] != "administrador":
        return jsonify({"success": False, "error": "No autorizado."}), 403

    # Renderizar la plantilla HTML
    html = render_template('factura_pdf.html', pedido=pedido, invoice_id=invoice_id, user=user, now=datetime.now())

    # Generar el PDF en memoria
    pdf_stream = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf_stream)
    
    if pisa_status.err:
        return jsonify({"success": False, "error": "Error al generar el PDF."}), 500

    pdf_stream.seek(0)
    return send_file(
        pdf_stream,
        as_attachment=True,
        download_name=f"Factura_{invoice_id}.pdf",
        mimetype="application/pdf"
    )

@app.route("/api/invoices/<invoice_id>/email", methods=["POST"])
@requiere_login
def enviar_factura_correo(invoice_id):
    pedidos = leer_json("orders.json")
    pedido  = next((p for p in pedidos if p.get("invoice_id") == invoice_id), None)

    if not pedido:
        return jsonify({"success": False, "error": "Factura no encontrada."}), 404

    user = session["user"]
    if pedido["user_email"] != user["email"] and user["role"] != "administrador":
        return jsonify({"success": False, "error": "No autorizado."}), 403

    # Renderizar la plantilla HTML
    html = render_template('factura_pdf.html', pedido=pedido, invoice_id=invoice_id, user=user, now=datetime.now())

    # Generar el PDF en memoria
    pdf_stream = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf_stream)
    
    if pisa_status.err:
        return jsonify({"success": False, "error": "Error al generar el PDF."}), 500
    
    # Preparar el correo
    smtp_server = os.environ.get("SMTP_SERVER")
    smtp_port = os.environ.get("SMTP_PORT")
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    
    if not smtp_server or not smtp_user or not smtp_password:
        return jsonify({"success": False, "error": "El servidor de correo no está configurado en el archivo .env."}), 500
        
    try:
        msg = EmailMessage()
        msg["Subject"] = f"Factura Lycaon Security - {invoice_id}"
        msg["From"] = smtp_user
        msg["To"] = user["email"]
        msg.set_content(f"Hola {user['name']},\n\nAdjunto encontrarás la factura de tu pedido {pedido['id']}.\n\nGracias por confiar en Lycaon Security.")
        
        # Adjuntar PDF
        msg.add_attachment(pdf_stream.getvalue(), maintype="application", subtype="pdf", filename=f"Factura_{invoice_id}.pdf")
        
        # Enviar correo
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            
        return jsonify({"success": True, "message": "Factura enviada correctamente al correo."})
    except Exception as e:
        return jsonify({"success": False, "error": f"Error al enviar correo: {str(e)}"}), 500

@app.route("/api/export/inventory")
@requiere_admin
def exportar_inventario():
    inventario = leer_json("inventory.json")
    if not inventario:
        return jsonify({"success": False, "error": "No hay inventario para exportar."}), 404
        
    df = pd.DataFrame(inventario)
    
    # Reordenar columnas para mejor lectura
    cols = ['id', 'name', 'category', 'price', 'stock', 'status', 'created_at']
    df = df[[c for c in cols if c in df.columns]]
    
    csv_stream = BytesIO()
    df.to_csv(csv_stream, index=False, encoding="utf-8-sig")
    csv_stream.seek(0)
    
    return send_file(
        csv_stream,
        as_attachment=True,
        download_name="Inventario_LycaonSoftware.csv",
        mimetype="text/csv"
    )

@app.route("/api/export/users")
@requiere_admin
def exportar_usuarios():
    usuarios = leer_json("users.json")
    if not usuarios:
        return jsonify({"success": False, "error": "No hay usuarios para exportar."}), 404
        
    df = pd.DataFrame(usuarios)
    
    # Quitar contraseñas (el campo real se llama password_hash)
    if 'password_hash' in df.columns:
        df = df.drop(columns=['password_hash'])
        
    csv_stream = BytesIO()
    df.to_csv(csv_stream, index=False, encoding="utf-8-sig")
    csv_stream.seek(0)
    
    return send_file(
        csv_stream,
        as_attachment=True,
        download_name="Usuarios_LycaonSoftware.csv",
        mimetype="text/csv"
    )


# ══════════════════════════════════════════
#  API — Usuarios (Admin)
# ══════════════════════════════════════════

@app.route("/api/users", methods=["POST"])
@requiere_admin
def api_crear_usuario():
    """
    POST /api/users
    Body JSON: { "name": "...", "email": "...", "password": "...", "role": "cliente"|"administrador" }
    Crea un nuevo usuario desde el panel de administración.
    """
    datos    = request.get_json()
    nombre   = datos.get("name", "").strip()
    email    = datos.get("email", "").strip().lower()
    password = datos.get("password", "")
    rol      = datos.get("role", "cliente")

    if not nombre or not email or not password:
        return jsonify({"success": False, "error": "Llena todos los campos."}), 400
    if len(password) < 6:
        return jsonify({"success": False, "error": "Contrasena minimo 6 caracteres."}), 400
    if rol not in ("administrador", "cliente"):
        return jsonify({"success": False, "error": "Rol invalido."}), 400

    usuarios = leer_json("users.json")
    if any(u["email"].lower() == email for u in usuarios):
        return jsonify({"success": False, "error": "Este correo ya esta registrado."}), 409

    nuevo = {
        "id":            f"U{str(uuid.uuid4())[:6].upper()}",
        "name":          nombre,
        "email":         email,
        "password_hash": generate_password_hash(password),
        "role":          rol,
        "verified":      True,
        "avatar":        "",
        "created_at":    datetime.now().isoformat()
    }
    usuarios.append(nuevo)
    escribir_json("users.json", usuarios)

    registrar_actividad(
        session["user"]["email"], "user_created", "user",
        nuevo["id"], {"name": nombre, "role": rol}
    )
    return jsonify({"success": True, "user": {k: v for k, v in nuevo.items() if k != "password_hash"}})

@app.route("/api/users/<user_id>/edit", methods=["POST"])
@requiere_admin
def api_editar_usuario(user_id):
    """
    POST /api/users/<user_id>/edit
    Edita un usuario existente.
    """
    datos    = request.get_json()
    nombre   = datos.get("name", "").strip()
    email    = datos.get("email", "").strip().lower()
    password = datos.get("password", "")
    rol      = datos.get("role", "")

    if not nombre or not email or not rol:
        return jsonify({"success": False, "error": "Faltan campos obligatorios."}), 400
    if rol not in ("administrador", "cliente"):
        return jsonify({"success": False, "error": "Rol invalido."}), 400

    usuarios = leer_json("users.json")
    
    # Check if email is used by another user
    if any(u["email"].lower() == email and u["id"] != user_id for u in usuarios):
        return jsonify({"success": False, "error": "Este correo ya esta registrado por otro usuario."}), 409

    for usuario in usuarios:
        if usuario["id"] == user_id:
            usuario["name"] = nombre
            usuario["email"] = email
            usuario["role"] = rol
            if password:
                if len(password) < 6:
                    return jsonify({"success": False, "error": "Contrasena minimo 6 caracteres."}), 400
                usuario["password_hash"] = generate_password_hash(password)
            
            escribir_json("users.json", usuarios)
            registrar_actividad(
                session["user"]["email"], "user_edited", "user",
                user_id, {"name": nombre, "role": rol}
            )
            return jsonify({"success": True, "user": {k: v for k, v in usuario.items() if k != "password_hash"}})

    return jsonify({"success": False, "error": "Usuario no encontrado."}), 404


@app.route("/api/users/<user_id>/role", methods=["PATCH"])
@requiere_admin
def api_cambiar_rol(user_id):
    datos     = request.get_json()
    nuevo_rol = datos.get("role")

    if nuevo_rol not in ("administrador", "cliente"):
        return jsonify({"success": False, "error": "Rol invalido."}), 400

    usuarios = leer_json("users.json")
    for usuario in usuarios:
        if usuario["id"] == user_id:
            old_role = usuario["role"]
            usuario["role"] = nuevo_rol
            escribir_json("users.json", usuarios)
            registrar_actividad(
                session["user"]["email"], "role_change", "user", user_id,
                {"old_role": old_role, "new_role": nuevo_rol}
            )
            return jsonify({"success": True})

    return jsonify({"success": False, "error": "Usuario no encontrado."}), 404


@app.route("/api/users/<user_id>", methods=["DELETE"])
@requiere_admin
def api_eliminar_usuario(user_id):
    if user_id == session["user"]["id"]:
        return jsonify({"success": False, "error": "No puedes eliminarte a ti mismo."}), 400

    usuarios  = leer_json("users.json")
    filtrados = [u for u in usuarios if u["id"] != user_id]

    if len(filtrados) == len(usuarios):
        return jsonify({"success": False, "error": "Usuario no encontrado."}), 404

    escribir_json("users.json", filtrados)
    registrar_actividad(session["user"]["email"], "user_deleted", "user", user_id)
    return jsonify({"success": True})


# ══════════════════════════════════════════
#  API — Foto de Perfil
# ══════════════════════════════════════════

@app.route("/api/profile/avatar", methods=["POST"])
@requiere_login
def api_subir_avatar():
    """
    POST /api/profile/avatar  (multipart/form-data)
    Campo: "avatar" — archivo de imagen
    Sube la imagen, la guarda en static/img/profiles/ y actualiza users.json
    """
    if "avatar" not in request.files:
        return jsonify({"success": False, "error": "No se encontro el archivo."}), 400

    archivo = request.files["avatar"]
    if archivo.filename == "":
        return jsonify({"success": False, "error": "Archivo sin nombre."}), 400
    if not allowed_file(archivo.filename):
        return jsonify({"success": False, "error": "Tipo de archivo no permitido (usa jpg, png, webp)."}), 400

    # Nombre seguro y único para evitar colisiones
    ext      = archivo.filename.rsplit(".", 1)[1].lower()
    user_id  = session["user"]["id"]
    nombre   = f"avatar_{user_id}.{ext}"
    ruta     = os.path.join(UPLOAD_DIR, nombre)

    archivo.save(ruta)

    # Actualizar en users.json
    ruta_relativa = f"img/profiles/{nombre}"
    usuarios = leer_json("users.json")
    for u in usuarios:
        if u["id"] == user_id:
            u["avatar"] = ruta_relativa
            break
    escribir_json("users.json", usuarios)

    # Actualizar la sesión activa
    session["user"]["avatar"] = ruta_relativa

    registrar_actividad(
        session["user"]["email"], "avatar_updated", "user", user_id
    )
    return jsonify({"success": True, "avatar_url": url_for("static", filename=ruta_relativa)})


# ══════════════════════════════════════════
#  API — Tareas del Planner
# ══════════════════════════════════════════

@app.route("/api/tasks", methods=["GET"])
@requiere_login
def api_listar_tareas():
    tareas = leer_json("tasks.json")
    return jsonify({"success": True, "data": tareas})


@app.route("/api/tasks", methods=["POST"])
@requiere_admin
def api_crear_tarea():
    datos       = request.get_json()
    titulo      = datos.get("title", "").strip()
    employee_id = datos.get("employee_id", "")
    time_window = datos.get("time_window", "")
    priority    = datos.get("priority", "medium")

    if not titulo or not employee_id:
        return jsonify({"success": False, "error": "Titulo y empleado son requeridos."}), 400

    usuarios = leer_json("users.json")
    empleado = next((u for u in usuarios if u["id"] == employee_id), None)

    tareas = leer_json("tasks.json")
    nueva_tarea = {
        "id":            f"T{str(uuid.uuid4())[:6].upper()}",
        "employee_id":   employee_id,
        "employee_name": empleado["name"] if empleado else "Desconocido",
        "title":         titulo,
        "time_window":   time_window,
        "status":        "pending",
        "priority":      priority,
        "created_at":    datetime.now().isoformat()
    }
    tareas.append(nueva_tarea)
    escribir_json("tasks.json", tareas)
    return jsonify({"success": True, "task": nueva_tarea})


@app.route("/api/tasks/<task_id>/status", methods=["PATCH"])
@requiere_login
def api_cambiar_estado_tarea(task_id):
    datos        = request.get_json()
    nuevo_estado = datos.get("status")

    if nuevo_estado not in ("pending", "in-progress", "completed", "issue"):
        return jsonify({"success": False, "error": "Estado invalido."}), 400

    tareas = leer_json("tasks.json")
    for tarea in tareas:
        if tarea["id"] == task_id:
            tarea["status"] = nuevo_estado
            escribir_json("tasks.json", tareas)
            return jsonify({"success": True})

    return jsonify({"success": False, "error": "Tarea no encontrada."}), 404


# ══════════════════════════════════════════
#  API — Inventario / Productos (Admin)
# ══════════════════════════════════════════

@app.route("/api/products", methods=["POST"])
@requiere_admin
def api_crear_producto():
    """
    POST /api/products
    Body JSON: { "name": "...", "category": "...", "price": 1200.00, "stock": 10 }
    Crea un nuevo producto en el catálogo y lo guarda en inventory.json.
    """
    datos     = request.get_json()
    nombre    = datos.get("name", "").strip()
    categoria = datos.get("category", "").strip()
    precio    = datos.get("price")
    stock     = datos.get("stock", 0)

    if not nombre or not categoria or precio is None:
        return jsonify({"success": False, "error": "Nombre, categoria y precio son requeridos."}), 400

    categorias_validas = ("Security", "Software", "Hardware", "Network", "Service")
    if categoria not in categorias_validas:
        return jsonify({"success": False, "error": f"Categoria debe ser una de: {', '.join(categorias_validas)}"}), 400

    try:
        precio = float(precio)
        stock  = int(stock)
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Precio y stock deben ser numeros."}), 400

    inventario = leer_json("inventory.json")
    nuevo_id   = f"P{len(inventario) + 1}"

    # Verificar que el ID no colisione
    ids_existentes = {p["id"] for p in inventario}
    while nuevo_id in ids_existentes:
        nuevo_id = f"P{str(uuid.uuid4())[:4].upper()}"

    # Determinar estado según stock
    if stock == 0:
        estado = "out-of-stock"
    elif stock <= 3:
        estado = "low-stock"
    else:
        estado = "active"

    nuevo_producto = {
        "id":         nuevo_id,
        "name":       nombre,
        "category":   categoria,
        "stock":      stock,
        "price":      precio,
        "status":     estado,
        "image_url":  "/static/img/placeholder.svg",
        "created_at": datetime.now().isoformat()
    }

    inventario.append(nuevo_producto)
    escribir_json("inventory.json", inventario)

    registrar_actividad(
        session["user"]["email"], "product_created", "product",
        nuevo_id, {"name": nombre, "price": precio, "stock": stock}
    )
    return jsonify({"success": True, "product": nuevo_producto})


@app.route("/api/products/<product_id>", methods=["DELETE"])
@requiere_admin
def api_eliminar_producto(product_id):
    """DELETE /api/products/<product_id> — Elimina un producto del catálogo."""
    inventario  = leer_json("inventory.json")
    filtrados   = [p for p in inventario if p["id"] != product_id]

    if len(filtrados) == len(inventario):
        return jsonify({"success": False, "error": "Producto no encontrado."}), 404

    escribir_json("inventory.json", filtrados)
    registrar_actividad(session["user"]["email"], "product_deleted", "product", product_id)
    return jsonify({"success": True})


# ══════════════════════════════════════════
#  API — Foto de Producto
# ══════════════════════════════════════════

@app.route("/api/products/<product_id>/image", methods=["POST"])
@requiere_admin
def api_subir_imagen_producto(product_id):
    """
    POST /api/products/<product_id>/image  (multipart/form-data)
    Campo: "image" — archivo de imagen
    """
    if "image" not in request.files:
        return jsonify({"success": False, "error": "No se encontro el archivo."}), 400

    archivo = request.files["image"]
    if archivo.filename == "":
        return jsonify({"success": False, "error": "Archivo sin nombre."}), 400
    if not allowed_file(archivo.filename):
        return jsonify({"success": False, "error": "Tipo de archivo no permitido (usa jpg, png, webp)."}), 400

    inventario = leer_json("inventory.json")
    producto = next((p for p in inventario if p["id"] == product_id), None)
    if not producto:
        return jsonify({"success": False, "error": "Producto no encontrado."}), 404

    ext = archivo.filename.rsplit(".", 1)[1].lower()
    nombre = f"prod_{product_id}_{str(uuid.uuid4())[:6]}.{ext}"
    ruta = os.path.join(PRODUCT_IMG_DIR, nombre)

    archivo.save(ruta)

    ruta_relativa = f"/static/img/products/{nombre}"
    producto["image_url"] = ruta_relativa
    escribir_json("inventory.json", inventario)

    registrar_actividad(
        session["user"]["email"], "product_image_updated", "product", product_id
    )
    return jsonify({"success": True, "image_url": ruta_relativa})


# ══════════════════════════════════════════
#  Punto de entrada
# ══════════════════════════════════════════

@app.route('/dashboard/suggestions')
@login_required
def dash_suggestions():
    return render_template('dashboard/suggestions.html', usuario=session['user'])

@app.route('/api/suggestions', methods=['POST'])
@login_required
def api_suggestions():
    d = request.get_json()
    s = leer_json('suggestions.json')
    s.append({
        'id': f'S{len(s)+1}',
        'user_id': session['user']['id'],
        'type': d.get('type'),
        'message': d.get('message'),
        'date': datetime.now().isoformat()
    })
    escribir_json('suggestions.json', s)
    return jsonify({'success': True})

@app.route('/api/reviews', methods=['POST'])
@login_required
def api_reviews():
    d = request.get_json()
    r = leer_json('reviews.json')
    r.append({
        'id': f'R{len(r)+1}',
        'user_id': session['user']['id'],
        'order_id': d.get('order_id'),
        'product_id': d.get('product_id'),
        'rating': d.get('rating'),
        'comment': d.get('comment'),
        'date': datetime.now().isoformat()
    })
    escribir_json('reviews.json', r)
    return jsonify({'success': True})


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

if __name__ == "__main__":

    inicializar_usuarios()
    print("=" * 50)
    print("  LYCAON SOFTWARE v2 -- Flask Server")
    print("  http://localhost:5000")
    print("")
    print("  Usuarios de ejemplo:")
    print("  admin@lycaonsoftware.com     / admin123")
    print("  juandavidnps@gmail.com / cliente123")
    print("=" * 50)
    app.run(debug=True, port=5000)
