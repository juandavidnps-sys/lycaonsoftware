"""
==============================================================================
LYCAON SOFTWARE - SCRIPT DE MIGRACIÓN: JSON MOCKS -> MYSQL RELACIONAL
Transfiere todos los datos almacenados en archivos planos (data/*.json)
hacia las tablas oficiales de MySQL (XAMPP o Render) sin pérdida de datos.
==============================================================================
"""

import os
import json
from datetime import datetime
from database import init_db, get_db_connection, check_db_health

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def clean_datetime(val):
    """Limpia y formatea cadenas ISO a formato compatible con MySQL DATETIME."""
    if not val:
        return None
    val_str = str(val).replace("T", " ")
    if "." in val_str:
        val_str = val_str.split(".")[0]
    return val_str


def leer_archivo_json(nombre_archivo):
    ruta = os.path.join(DATA_DIR, nombre_archivo)
    if not os.path.exists(ruta):
        return []
    with open(ruta, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return []


def reparar_columnas_existentes():
    """Asegura compatibilidad de columnas DATETIME en caso de que la tabla ya exista."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    "ALTER TABLE inventory MODIFY COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;"
                )
                cursor.execute(
                    "ALTER TABLE inventory MODIFY COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP;"
                )
            except Exception:
                pass


def migrar_usuarios():
    usuarios = leer_archivo_json("users.json")
    if not usuarios:
        print("[-] No se encontraron usuarios en data/users.json")
        return 0

    sql = """
    INSERT INTO users (id, name, email, password_hash, role, verified, avatar, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        name = VALUES(name),
        password_hash = VALUES(password_hash),
        role = VALUES(role),
        verified = VALUES(verified),
        avatar = VALUES(avatar);
    """
    total = 0
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            for u in usuarios:
                cursor.execute(sql, (
                    u.get("id"),
                    u.get("name", "Usuario"),
                    u.get("email"),
                    u.get("password_hash"),
                    u.get("role", "cliente"),
                    u.get("verified", True),
                    u.get("avatar", ""),
                    clean_datetime(u.get("created_at"))
                ))
                total += 1
    print(f"[OK] {total} usuarios migrados a la tabla 'users'.")
    return total


def migrar_inventario():
    inventario = leer_archivo_json("inventory.json")
    if not inventario:
        print("[-] No se encontraron productos en data/inventory.json")
        return 0

    sql = """
    INSERT INTO inventory (id, name, category, stock, price, status, image_url, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        name = VALUES(name),
        category = VALUES(category),
        stock = VALUES(stock),
        price = VALUES(price),
        status = VALUES(status),
        image_url = VALUES(image_url),
        updated_at = VALUES(updated_at);
    """
    total = 0
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            for item in inventario:
                c_at = clean_datetime(item.get("created_at")) or clean_datetime(datetime.now())
                u_at = clean_datetime(item.get("updated_at")) or c_at
                cursor.execute(sql, (
                    item.get("id"),
                    item.get("name"),
                    item.get("category", "General"),
                    item.get("stock", 0),
                    item.get("price", 0.0),
                    item.get("status", "active"),
                    item.get("image_url", ""),
                    c_at,
                    u_at
                ))
                total += 1
    print(f"[OK] {total} productos migrados a la tabla 'inventory'.")
    return total


def migrar_pedidos():
    pedidos = leer_archivo_json("orders.json")
    if not pedidos:
        print("[-] No se encontraron pedidos en data/orders.json")
        return 0

    sql = """
    INSERT INTO orders (id, user_id, user_email, product_id, product_name, cantidad, subtotal, discount_amount, total, status, invoice_id, items_json, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        status = VALUES(status),
        total = VALUES(total);
    """
    total = 0
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            for p in pedidos:
                items_list = p.get("items", [])
                items_json_str = json.dumps(items_list, ensure_ascii=False) if items_list else None
                pid = p.get("product_id")
                if pid in ("CART-MULTI", ""):
                    pid = None
                
                # Verificar que el producto exista en inventory o dejar NULL para respetar FK
                if pid:
                    cursor.execute("SELECT id FROM inventory WHERE id = %s", (pid,))
                    if not cursor.fetchone():
                        pid = None

                cursor.execute(sql, (
                    p.get("id"),
                    p.get("user_id"),
                    p.get("user_email"),
                    pid,
                    p.get("product_name"),
                    p.get("cantidad", 1),
                    p.get("subtotal", 0.0),
                    p.get("discount_amount", 0.0),
                    p.get("total", 0.0),
                    p.get("status", "delivered"),
                    p.get("invoice_id"),
                    items_json_str,
                    clean_datetime(p.get("created_at"))
                ))
                total += 1
    print(f"[OK] {total} pedidos migrados a la tabla 'orders'.")
    return total


def migrar_logs():
    logs = leer_archivo_json("activity_log.json")
    if not logs:
        print("[-] No se encontraron logs en data/activity_log.json")
        return 0

    sql = """
    INSERT INTO activity_log (id, user_email, action, entity_type, entity_id, ip_address, details, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        action = VALUES(action);
    """
    total = 0
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            for l in logs:
                cursor.execute(sql, (
                    l.get("id"),
                    l.get("user_email", "system"),
                    l.get("action", ""),
                    l.get("entity_type", ""),
                    l.get("entity_id", ""),
                    l.get("ip_address", "127.0.0.1"),
                    l.get("details"),
                    clean_datetime(l.get("created_at"))
                ))
                total += 1
    print(f"[OK] {total} registros de auditoría migrados a 'activity_log'.")
    return total


def ejecutar_migracion():
    print("=" * 65)
    print("  INICIANDO MIGRACIÓN COMPLETA A MYSQL (MOCKS JSON -> SQL)")
    print("=" * 65)
    health = check_db_health()
    if health["status"] != "connected":
        print(f"[ERROR] No se pudo conectar a la base de datos: {health['error']}")
        print("Inicia MySQL en XAMPP antes de ejecutar la migración.")
        return

    print(f"[+] Conectado a {health['database']} en {health['host']}:{health['port']}")
    print("[+] Inicializando tablas en la base de datos...")
    init_db()
    reparar_columnas_existentes()

    print("\n[+] Migrando entidades...")
    migrar_usuarios()
    migrar_inventario()
    migrar_pedidos()
    migrar_logs()

    print("\n" + "=" * 65)
    print("  MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 65)


if __name__ == "__main__":
    ejecutar_migracion()
