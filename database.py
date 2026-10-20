

import os
import sys
from urllib.parse import urlparse
from contextlib import contextmanager
import pymysql
import pymysql.cursors
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
load_dotenv()


def get_db_config():
    """
    Resuelve los parámetros de conexión de manera híbrida:
    1. Si existe 'DATABASE_URL' o 'MYSQL_URL' (típico en Render / PaaS en la nube),
       extrae dinámicamente el host, puerto, usuario, contraseña y base de datos.
    2. Si no existe, recurre a las variables atómicas (DB_HOST, DB_USER, etc.),
       con valores por defecto calibrados para XAMPP (localhost, 3306, root, sin password).
    """
    database_url = os.environ.get("DATABASE_URL") or os.environ.get("MYSQL_URL")

    if database_url:
        # Normalizar prefijos como mysql+pymysql:// a mysql:// para urlparse
        if database_url.startswith("mysql+pymysql://"):
            database_url = "mysql://" + database_url[len("mysql+pymysql://"):]

        parsed = urlparse(database_url)
        return {
            "host": parsed.hostname or "localhost",
            "port": int(parsed.port or 3306),
            "user": parsed.username or "root",
            "password": parsed.password or "",
            "database": parsed.path.lstrip("/") if parsed.path else "lycaon_db",
            "charset": "utf8mb4",
            "source": "DATABASE_URL (Producción / Cloud)"
        }

    return {
        "host": os.environ.get("DB_HOST", "localhost"),
        "port": int(os.environ.get("DB_PORT", 3306)),
        "user": os.environ.get("DB_USER", "root"),
        "password": os.environ.get("DB_PASSWORD", ""),
        "database": os.environ.get("DB_NAME", "lycaon_db"),
        "charset": "utf8mb4",
        "source": "Variables Atómicas / XAMPP Local"
    }


@contextmanager
def get_db_connection(select_db=True):
    """
    Context manager seguro para obtener una conexión a MySQL con DictCursor.
    Garantiza:
    - Retorno de resultados como diccionarios (compatibilidad total con APIs).
    - Commit automático si el bloque termina con éxito.
    - Rollback ante cualquier excepción no controlada.
    - Cierre garantizado del socket y liberación de recursos en el bloque finally.
    
    Uso:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()
    """
    config = get_db_config()
    conn_params = {
        "host": config["host"],
        "port": config["port"],
        "user": config["user"],
        "password": config["password"],
        "charset": config["charset"],
        "cursorclass": pymysql.cursors.DictCursor,
        "autocommit": False
    }

    if select_db:
        conn_params["database"] = config["database"]

    conn = pymysql.connect(**conn_params)
    try:
        yield conn
        conn.commit()
    except Exception as exc:
        conn.rollback()
        raise exc
    finally:
        conn.close()


def execute_query(sql, params=None, fetch_one=False, fetch_all=False):
    """
    Helper utilitario para ejecutar sentencias SQL preparadas de forma limpia y segura contra inyecciones SQL.
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            if fetch_one:
                return cursor.fetchone()
            if fetch_all:
                return cursor.fetchall()
            return cursor.lastrowid or cursor.rowcount


def check_db_health():
    """
    Verifica el estado de la conexión a la base de datos y reporta métricas útiles.
    """
    config = get_db_config()
    try:
        with get_db_connection(select_db=False) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT VERSION() AS version, NOW() AS server_time")
                info = cursor.fetchone()
                return {
                    "status": "connected",
                    "host": config["host"],
                    "port": config["port"],
                    "user": config["user"],
                    "database": config["database"],
                    "source": config["source"],
                    "mysql_version": info["version"],
                    "server_time": str(info["server_time"]),
                    "error": None
                }
    except Exception as exc:
        return {
            "status": "disconnected",
            "host": config["host"],
            "port": config["port"],
            "user": config["user"],
            "database": config["database"],
            "source": config["source"],
            "error": str(exc)
        }


def init_db(schema_file="schema.sql"):
    """
    Lee e inicializa las tablas del esquema SQL en la base de datos MySQL configurada.
    Crea la base de datos si aún no existe.
    """
    config = get_db_config()
    db_name = config["database"]
    
    # 1. Asegurar la creación de la base de datos conectando sin especificar db
    with get_db_connection(select_db=False) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
            )
            print(f"[OK] Base de datos '{db_name}' verificada/creada con éxito.")

    # 2. Ejecutar sentencias del archivo schema.sql
    if not os.path.exists(schema_file):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        schema_file = os.path.join(base_dir, schema_file)

    if not os.path.exists(schema_file):
        raise FileNotFoundError(f"No se encontró el archivo de esquema: {schema_file}")

    with open(schema_file, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Dividir y ejecutar sentencias SQL individuales
    statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]
    with get_db_connection(select_db=True) as conn:
        with conn.cursor() as cursor:
            for stmt in statements:
                # Omitir USE y CREATE DATABASE para no generar conflictos
                if stmt.upper().startswith("USE ") or stmt.upper().startswith("CREATE DATABASE "):
                    continue
                cursor.execute(stmt)
        print(f"[OK] {len(statements)} sentencias DDL ejecutadas. Esquema relacional listo.")


# ══════════════════════════════════════════════════════════════════════════════
# REPOSITORIO DE DATOS (MÉTODOS CRUD DIRECTOS EN MYSQL)
# ══════════════════════════════════════════════════════════════════════════════

def db_get_users():
    """Obtiene todos los usuarios de la base de datos."""
    sql = "SELECT id, name, email, password_hash, role, verified, avatar, created_at FROM users ORDER BY created_at DESC"
    users = execute_query(sql, fetch_all=True) or []
    for u in users:
        if u.get("created_at"):
            u["created_at"] = str(u["created_at"])
    return users


def db_get_user_by_email(email):
    """Busca un usuario por su correo electrónico."""
    sql = "SELECT id, name, email, password_hash, role, verified, avatar, created_at FROM users WHERE LOWER(email) = LOWER(%s)"
    u = execute_query(sql, (email.strip(),), fetch_one=True)
    if u and u.get("created_at"):
        u["created_at"] = str(u["created_at"])
    return u


def db_get_user_by_id(user_id):
    """Busca un usuario por su ID primario."""
    sql = "SELECT id, name, email, password_hash, role, verified, avatar, created_at FROM users WHERE id = %s"
    u = execute_query(sql, (user_id,), fetch_one=True)
    if u and u.get("created_at"):
        u["created_at"] = str(u["created_at"])
    return u


def db_create_user(user_id, name, email, password_hash, role="cliente", verified=True, avatar=""):
    """Inserta un nuevo usuario en la base de datos MySQL."""
    sql = """
    INSERT INTO users (id, name, email, password_hash, role, verified, avatar, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
    """
    execute_query(sql, (user_id, name, email.strip().lower(), password_hash, role, verified, avatar))
    return db_get_user_by_id(user_id)


def db_update_user(user_id, name, email, role, password_hash=None):
    """Actualiza datos de un usuario existente en MySQL."""
    if password_hash:
        sql = "UPDATE users SET name = %s, email = %s, role = %s, password_hash = %s WHERE id = %s"
        execute_query(sql, (name, email.strip().lower(), role, password_hash, user_id))
    else:
        sql = "UPDATE users SET name = %s, email = %s, role = %s WHERE id = %s"
        execute_query(sql, (name, email.strip().lower(), role, user_id))
    return db_get_user_by_id(user_id)


def db_update_user_role(user_id, role):
    """Cambia el rol de un usuario en MySQL."""
    sql = "UPDATE users SET role = %s WHERE id = %s"
    execute_query(sql, (role, user_id))
    return db_get_user_by_id(user_id)


def db_delete_user(user_id):
    """Elimina un usuario por su ID en MySQL."""
    sql = "DELETE FROM users WHERE id = %s"
    return execute_query(sql, (user_id,))


def db_update_user_profile(user_id, name, password_hash=None):
    """Actualiza el nombre y opcionalmente la contraseña de un usuario en MySQL."""
    if password_hash:
        sql = "UPDATE users SET name = %s, password_hash = %s WHERE id = %s"
        execute_query(sql, (name.strip(), password_hash, user_id))
    else:
        sql = "UPDATE users SET name = %s WHERE id = %s"
        execute_query(sql, (name.strip(), user_id))
    return db_get_user_by_id(user_id)


def db_update_user_avatar(user_id, avatar_path):
    """Actualiza la ruta del archivo de avatar del usuario en MySQL."""
    sql = "UPDATE users SET avatar = %s WHERE id = %s"
    execute_query(sql, (avatar_path, user_id))
    return db_get_user_by_id(user_id)


def db_get_inventory():
    """Obtiene todo el catálogo de inventario desde MySQL."""
    sql = "SELECT id, name, category, stock, CAST(price AS DOUBLE) as price, status, image_url, created_at, updated_at FROM inventory ORDER BY name ASC"
    items = execute_query(sql, fetch_all=True) or []
    for item in items:
        if item.get("created_at"):
            item["created_at"] = str(item["created_at"])
        if item.get("updated_at"):
            item["updated_at"] = str(item["updated_at"])
    return items


def db_get_product_by_id(product_id):
    """Obtiene un producto por ID."""
    sql = "SELECT id, name, category, stock, CAST(price AS DOUBLE) as price, status, image_url, created_at, updated_at FROM inventory WHERE id = %s"
    item = execute_query(sql, (product_id,), fetch_one=True)
    if item:
        if item.get("created_at"):
            item["created_at"] = str(item["created_at"])
        if item.get("updated_at"):
            item["updated_at"] = str(item["updated_at"])
    return item


def db_create_product(product_id, name, category, stock, price, status="active", image_url=""):
    """Inserta un nuevo producto en MySQL."""
    sql = """
    INSERT INTO inventory (id, name, category, stock, price, status, image_url, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
    """
    execute_query(sql, (product_id, name, category, stock, price, status, image_url))
    return db_get_product_by_id(product_id)


def db_update_product(product_id, name, category, stock, price, status, image_url=None):
    """Actualiza un producto en MySQL."""
    if image_url:
        sql = "UPDATE inventory SET name = %s, category = %s, stock = %s, price = %s, status = %s, image_url = %s, updated_at = NOW() WHERE id = %s"
        execute_query(sql, (name, category, stock, price, status, image_url, product_id))
    else:
        sql = "UPDATE inventory SET name = %s, category = %s, stock = %s, price = %s, status = %s, updated_at = NOW() WHERE id = %s"
        execute_query(sql, (name, category, stock, price, status, product_id))
    return db_get_product_by_id(product_id)


def db_delete_product(product_id):
    """Elimina un producto de MySQL."""
    sql = "DELETE FROM inventory WHERE id = %s"
    return execute_query(sql, (product_id,))


def db_get_orders(user_email=None):
    """Obtiene los pedidos desde MySQL."""
    import json
    if user_email:
        sql = "SELECT id, user_id, user_email, product_id, product_name, cantidad, CAST(subtotal AS DOUBLE) as subtotal, CAST(discount_amount AS DOUBLE) as discount_amount, CAST(total AS DOUBLE) as total, status, invoice_id, items_json, created_at FROM orders WHERE LOWER(user_email) = LOWER(%s) ORDER BY created_at DESC"
        orders = execute_query(sql, (user_email,), fetch_all=True) or []
    else:
        sql = "SELECT id, user_id, user_email, product_id, product_name, cantidad, CAST(subtotal AS DOUBLE) as subtotal, CAST(discount_amount AS DOUBLE) as discount_amount, CAST(total AS DOUBLE) as total, status, invoice_id, items_json, created_at FROM orders ORDER BY created_at DESC"
        orders = execute_query(sql, fetch_all=True) or []

    for o in orders:
        if o.get("created_at"):
            o["created_at"] = str(o["created_at"])
        if o.get("items_json"):
            try:
                o["items"] = json.loads(o["items_json"]) if isinstance(o["items_json"], str) else o["items_json"]
            except Exception:
                o["items"] = []
        else:
            o["items"] = []
    return orders


def db_create_order(order_dict):
    """Inserta una orden y sus detalles normalizados (order_items) en MySQL con integridad referencial."""
    import json
    import uuid
    sql = """
    INSERT INTO orders (id, user_id, user_email, product_id, product_name, cantidad, subtotal, discount_amount, total, status, invoice_id, items_json, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
    """
    items_list = order_dict.get("items", [])
    items_str = json.dumps(items_list, ensure_ascii=False) if items_list else None
    order_id = order_dict.get("id")
    
    # Manejar producto nulo para compras de múltiples items
    product_id = order_dict.get("product_id")
    if product_id in ("CART-MULTI", ""):
        product_id = None

    execute_query(sql, (
        order_id,
        order_dict.get("user_id"),
        order_dict.get("user_email"),
        product_id,
        order_dict.get("product_name"),
        order_dict.get("cantidad", 1),
        order_dict.get("subtotal", 0.0),
        order_dict.get("discount_amount", 0.0),
        order_dict.get("total", 0.0),
        order_dict.get("status", "delivered"),
        order_dict.get("invoice_id"),
        items_str
    ))

    # Guardar items en tabla relacional normalizada order_items vinculada por Foreign Key
    if items_list:
        for it in items_list:
            item_pk = f"ITEM-{str(uuid.uuid4())[:8].upper()}"
            item_p_id = it.get("product_id")
            if item_p_id in ("CART-MULTI", ""):
                item_p_id = None
            sql_item = """
            INSERT INTO order_items (id, order_id, product_id, product_name, category, price, cantidad, subtotal)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            try:
                execute_query(sql_item, (
                    item_pk,
                    order_id,
                    item_p_id,
                    it.get("product_name", "Item"),
                    it.get("category", "General"),
                    it.get("price", 0.0),
                    it.get("cantidad", 1),
                    it.get("subtotal", 0.0)
                ))
            except Exception as exc:
                print(f"[DB WARN] No se pudo insertar en order_items: {exc}")


def db_create_activity_log(log_dict):
    """Inserta un registro de auditoría en MySQL."""
    sql = """
    INSERT INTO activity_log (id, user_email, action, entity_type, entity_id, ip_address, details, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
    """
    execute_query(sql, (
        log_dict.get("id"),
        log_dict.get("user_email"),
        log_dict.get("action"),
        log_dict.get("entity_type"),
        str(log_dict.get("entity_id")),
        log_dict.get("ip_address", "127.0.0.1"),
        log_dict.get("details")
    ))


def db_get_activity_logs(limit=200):
    """Obtiene los logs de auditoría más recientes."""
    sql = "SELECT id, user_email, action, entity_type, entity_id, ip_address, details, created_at FROM activity_log ORDER BY created_at DESC LIMIT %s"
    logs = execute_query(sql, (limit,), fetch_all=True) or []
    for l in logs:
        if l.get("created_at"):
            l["created_at"] = str(l["created_at"])
    return logs


if __name__ == "__main__":
    print("=" * 65)
    print("  DIAGNÓSTICO DE CONEXIÓN A BASE DE DATOS - LYCAON SOFTWARE")
    print("=" * 65)
    health = check_db_health()
    print(f"  Fuente:        {health['source']}")
    print(f"  Host:          {health['host']}:{health['port']}")
    print(f"  Usuario:       {health['user']}")
    print(f"  Base de datos: {health['database']}")
    print(f"  Estado:        {health['status'].upper()}")

    if health["status"] == "connected":
        print(f"  Versión MySQL: {health['mysql_version']}")
        print(f"  Hora Servidor: {health['server_time']}")
        print("  -> Conexión establecida correctamente.")
        if "--init" in sys.argv:
            print("\nIniciando creación de tablas...")
            init_db()
    else:
        print(f"\n  [ERROR] {health['error']}")
        print("\n  RECOMENDACIONES PARA RESOLVER:")
        print("  1. Si estás en entorno local, asegúrate de haber iniciado el módulo MySQL en XAMPP.")
        print("  2. Verifica que el puerto 3306 esté libre y habilitado.")
        print("  3. Si cambiaste la contraseña de 'root' en phpMyAdmin, colócala en tu archivo .env.")
    print("=" * 65)
