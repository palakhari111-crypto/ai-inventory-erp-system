"""
database.py — SQLite schema, seed data, and all DB helpers for NEXUS ERP
"""

import sqlite3
import hashlib
import datetime
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "nexus_erp.db")


# ─── connection ───────────────────────────────────────────────────────────────

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# ─── schema ───────────────────────────────────────────────────────────────────

def init_db():
    conn = get_conn()
    c = conn.cursor()

    # Users
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT    NOT NULL UNIQUE,
            password    TEXT    NOT NULL,
            role        TEXT    NOT NULL CHECK(role IN ('admin','cashier')),
            full_name   TEXT,
            email       TEXT,
            active      INTEGER DEFAULT 1,
            created_at  TEXT    DEFAULT (datetime('now'))
        )
    """)

    # Products / inventory
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL UNIQUE,
            category    TEXT    DEFAULT 'General',
            sku         TEXT    UNIQUE,
            quantity    INTEGER DEFAULT 0,
            unit_price  REAL    DEFAULT 0.0,
            min_stock   INTEGER DEFAULT 5,
            description TEXT,
            source      TEXT    DEFAULT 'manual',
            last_updated TEXT   DEFAULT (datetime('now')),
            created_at  TEXT    DEFAULT (datetime('now'))
        )
    """)

    # AI detection sessions
    c.execute("""
        CREATE TABLE IF NOT EXISTS ai_detections (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            image_name      TEXT,
            detected_json   TEXT,
            annotated_image TEXT,
            detected_by     TEXT,
            detection_time  TEXT    DEFAULT (datetime('now')),
            status          TEXT    DEFAULT 'pending'
                                    CHECK(status IN ('pending','approved','rejected')),
            action          TEXT    CHECK(action IN ('add','update',NULL)),
            approved_by     TEXT,
            approved_at     TEXT,
            notes           TEXT
        )
    """)

    # Sales / cashier transactions
    c.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            cashier_id   INTEGER REFERENCES users(id),
            cashier_name TEXT,
            total_amount REAL    DEFAULT 0.0,
            payment_mode TEXT    DEFAULT 'cash',
            sale_time    TEXT    DEFAULT (datetime('now')),
            notes        TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS sale_items (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id    INTEGER REFERENCES sales(id),
            product_id INTEGER REFERENCES products(id),
            product_name TEXT,
            quantity   INTEGER,
            unit_price REAL,
            subtotal   REAL
        )
    """)

    # Audit log
    c.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            actor     TEXT,
            role      TEXT,
            action    TEXT,
            details   TEXT,
            timestamp TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()

    # ── Seed default users ──
    _seed_users(conn)
    # ── Seed sample products ──
    _seed_products(conn)

    conn.close()


def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def _seed_users(conn):
    users = [
        ("admin",   _hash("admin123"),   "admin",   "Administrator",  "admin@nexus.com"),
        ("cashier1",_hash("cash123"),    "cashier", "John Cashier",   "cashier1@nexus.com"),
        ("cashier2",_hash("cash456"),    "cashier", "Sara Williams",  "cashier2@nexus.com"),
    ]
    for u in users:
        conn.execute(
            "INSERT OR IGNORE INTO users (username,password,role,full_name,email) VALUES (?,?,?,?,?)", u
        )
    conn.commit()


def _seed_products(conn):
    products = [
        ("Apple",        "Fruits",      "FRT-001", 120, 2.50,  10),
        ("Banana",       "Fruits",      "FRT-002",  80, 1.20,   8),
        ("Orange",       "Fruits",      "FRT-003",  60, 3.00,  10),
        ("Milk (1L)",    "Dairy",       "DRY-001",  45, 55.00,  5),
        ("Bread",        "Bakery",      "BKR-001",  30, 40.00,  5),
        ("Butter",       "Dairy",       "DRY-002",  25, 85.00,  3),
        ("Eggs (12pk)",  "Dairy",       "DRY-003",  40, 70.00,  5),
        ("Water Bottle", "Beverages",   "BVR-001", 100,  20.00, 10),
        ("Cola 500ml",   "Beverages",   "BVR-002",  75, 35.00, 10),
        ("Chips",        "Snacks",      "SNK-001",  90, 25.00, 15),
        ("Chocolate",    "Confection",  "CON-001",  55, 50.00,  8),
        ("Rice 1kg",     "Grains",      "GRN-001",  35, 65.00,  5),
        ("Sugar 1kg",    "Grains",      "GRN-002",  20, 45.00,  5),
        ("Soap",         "Hygiene",     "HYG-001",  60, 30.00, 10),
        ("Toothpaste",   "Hygiene",     "HYG-002",  40, 75.00,  5),
    ]
    for p in products:
        conn.execute(
            """INSERT OR IGNORE INTO products
               (name,category,sku,quantity,unit_price,min_stock)
               VALUES (?,?,?,?,?,?)""", p
        )
    conn.commit()


# ─── Auth ─────────────────────────────────────────────────────────────────────

def authenticate(username: str, password: str):
    """Returns user Row or None."""
    conn = get_conn()
    user = conn.execute(
        "SELECT * FROM users WHERE username=? AND password=? AND active=1",
        (username, _hash(password))
    ).fetchone()
    conn.close()
    return user


# ─── Products ─────────────────────────────────────────────────────────────────

def get_all_products():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM products ORDER BY category, name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_product_by_id(pid: int):
    conn = get_conn()
    row = conn.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_product_by_name(name: str):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM products WHERE LOWER(name)=LOWER(?)", (name,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def add_product(name, category, sku, quantity, unit_price, min_stock, description, actor):
    conn = get_conn()
    try:
        conn.execute(
            """INSERT INTO products (name,category,sku,quantity,unit_price,min_stock,description,source,last_updated)
               VALUES (?,?,?,?,?,?,?,'manual',datetime('now'))""",
            (name, category, sku, quantity, unit_price, min_stock, description)
        )
        conn.commit()
        audit(actor, "admin", "ADD_PRODUCT", f"Added '{name}' qty={quantity} price={unit_price}")
        return True, "Product added successfully."
    except sqlite3.IntegrityError as e:
        return False, f"Duplicate name or SKU: {e}"
    finally:
        conn.close()


def update_product(pid, name, category, sku, quantity, unit_price, min_stock, description, actor):
    conn = get_conn()
    try:
        conn.execute(
            """UPDATE products SET name=?,category=?,sku=?,quantity=?,unit_price=?,
               min_stock=?,description=?,last_updated=datetime('now') WHERE id=?""",
            (name, category, sku, quantity, unit_price, min_stock, description, pid)
        )
        conn.commit()
        audit(actor, "admin", "UPDATE_PRODUCT", f"Updated product #{pid} '{name}'")
        return True, "Product updated."
    except sqlite3.IntegrityError as e:
        return False, f"Error: {e}"
    finally:
        conn.close()


def delete_product(pid, actor):
    conn = get_conn()
    prod = conn.execute("SELECT name FROM products WHERE id=?", (pid,)).fetchone()
    if prod:
        conn.execute("DELETE FROM products WHERE id=?", (pid,))
        conn.commit()
        audit(actor, "admin", "DELETE_PRODUCT", f"Deleted product #{pid} '{prod['name']}'")
    conn.close()


def adjust_stock(pid, delta, source, actor):
    """Add delta (can be negative) to product stock."""
    conn = get_conn()
    conn.execute(
        "UPDATE products SET quantity=MAX(0,quantity+?), last_updated=datetime('now'), source=? WHERE id=?",
        (delta, source, pid)
    )
    conn.commit()
    conn.close()
    audit(actor, "admin", "STOCK_ADJUST", f"Product #{pid} delta={delta:+d} source={source}")


# ─── AI Detections ────────────────────────────────────────────────────────────

def save_detection(image_name, detected_json, annotated_b64, actor):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO ai_detections (image_name,detected_json,annotated_image,detected_by,status)
           VALUES (?,?,?,?,'pending')""",
        (image_name, json.dumps(detected_json), annotated_b64, actor)
    )
    det_id = cur.lastrowid
    conn.commit()
    conn.close()
    audit(actor, "admin", "AI_DETECT", f"Detection #{det_id} — {image_name} — {len(detected_json)} classes")
    return det_id


def get_pending_detections():
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM ai_detections WHERE status='pending' ORDER BY detection_time DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_detections():
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM ai_detections ORDER BY detection_time DESC LIMIT 100"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def approve_detection(det_id, action, actor):
    """
    action = 'add'    → qty += detected
    action = 'update' → qty  = detected
    """
    conn = get_conn()
    det = conn.execute("SELECT * FROM ai_detections WHERE id=?", (det_id,)).fetchone()
    if not det:
        conn.close()
        return False, "Detection not found."

    objects = json.loads(det["detected_json"])
    now = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")

    for obj_name, qty in objects.items():
        existing = conn.execute(
            "SELECT id,quantity FROM products WHERE LOWER(name)=LOWER(?)", (obj_name,)
        ).fetchone()
        if existing:
            if action == "add":
                new_qty = existing["quantity"] + qty
            else:  # update
                new_qty = qty
            conn.execute(
                "UPDATE products SET quantity=?,last_updated=?,source=? WHERE id=?",
                (new_qty, now, f"ai_{action}d", existing["id"])
            )
        else:
            # Create new product from AI detection
            conn.execute(
                """INSERT INTO products (name,category,quantity,unit_price,min_stock,source,last_updated)
                   VALUES (?,?,?,0,5,?,?)""",
                (obj_name.title(), "AI Detected", qty, f"ai_{action}d", now)
            )

    conn.execute(
        """UPDATE ai_detections SET status='approved',action=?,approved_by=?,approved_at=?
           WHERE id=?""",
        (action, actor, now, det_id)
    )
    conn.commit()
    conn.close()
    audit(actor, "admin", "APPROVE_DETECT",
          f"Detection #{det_id} approved (action={action}) — {len(objects)} items")
    return True, f"Detection #{det_id} approved — {len(objects)} products {action}d."


def reject_detection(det_id, actor, notes=""):
    conn = get_conn()
    now = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
    conn.execute(
        """UPDATE ai_detections SET status='rejected',approved_by=?,approved_at=?,notes=?
           WHERE id=?""",
        (actor, now, notes, det_id)
    )
    conn.commit()
    conn.close()
    audit(actor, "admin", "REJECT_DETECT", f"Detection #{det_id} rejected. Notes: {notes}")


# ─── Sales ────────────────────────────────────────────────────────────────────

def create_sale(cashier_id, cashier_name, items, payment_mode, notes=""):
    """
    items: list of dicts {product_id, product_name, quantity, unit_price}
    Returns (sale_id, total)
    """
    conn = get_conn()
    total = sum(i["quantity"] * i["unit_price"] for i in items)
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO sales (cashier_id,cashier_name,total_amount,payment_mode,notes)
           VALUES (?,?,?,?,?)""",
        (cashier_id, cashier_name, total, payment_mode, notes)
    )
    sale_id = cur.lastrowid
    for item in items:
        subtotal = item["quantity"] * item["unit_price"]
        conn.execute(
            """INSERT INTO sale_items (sale_id,product_id,product_name,quantity,unit_price,subtotal)
               VALUES (?,?,?,?,?,?)""",
            (sale_id, item["product_id"], item["product_name"],
             item["quantity"], item["unit_price"], subtotal)
        )
        # Deduct stock
        conn.execute(
            "UPDATE products SET quantity=MAX(0,quantity-?) WHERE id=?",
            (item["quantity"], item["product_id"])
        )
    conn.commit()
    conn.close()
    audit(cashier_name, "cashier", "SALE",
          f"Sale #{sale_id} total=₹{total:.2f} items={len(items)}")
    return sale_id, total


def get_sales_summary():
    conn = get_conn()
    rows = conn.execute("""
        SELECT s.id, s.cashier_name, s.total_amount, s.payment_mode, s.sale_time,
               COUNT(si.id) as item_count
        FROM sales s
        LEFT JOIN sale_items si ON si.sale_id=s.id
        GROUP BY s.id
        ORDER BY s.sale_time DESC
        LIMIT 100
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_sale_items(sale_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM sale_items WHERE sale_id=?", (sale_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Audit ────────────────────────────────────────────────────────────────────

def audit(actor, role, action, details):
    conn = get_conn()
    conn.execute(
        "INSERT INTO audit_log (actor,role,action,details) VALUES (?,?,?,?)",
        (actor, role, action, details)
    )
    conn.commit()
    conn.close()


def get_audit_log(limit=200):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Dashboard stats ──────────────────────────────────────────────────────────

def get_dashboard_stats():
    conn = get_conn()
    stats = {}
    stats["total_products"]  = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    stats["total_stock"]     = conn.execute("SELECT COALESCE(SUM(quantity),0) FROM products").fetchone()[0]
    stats["low_stock"]       = conn.execute(
        "SELECT COUNT(*) FROM products WHERE quantity <= min_stock"
    ).fetchone()[0]
    stats["total_sales"]     = conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
    stats["revenue_today"]   = conn.execute(
        "SELECT COALESCE(SUM(total_amount),0) FROM sales WHERE date(sale_time)=date('now')"
    ).fetchone()[0]
    stats["revenue_total"]   = conn.execute(
        "SELECT COALESCE(SUM(total_amount),0) FROM sales"
    ).fetchone()[0]
    stats["pending_approvals"] = conn.execute(
        "SELECT COUNT(*) FROM ai_detections WHERE status='pending'"
    ).fetchone()[0]
    stats["ai_detections"]   = conn.execute("SELECT COUNT(*) FROM ai_detections").fetchone()[0]

    # Category breakdown
    cats = conn.execute(
        "SELECT category, SUM(quantity) as total FROM products GROUP BY category"
    ).fetchall()
    stats["category_stock"] = {r["category"]: r["total"] for r in cats}

    # Sales last 7 days
    sales7 = conn.execute("""
        SELECT date(sale_time) as day, SUM(total_amount) as rev
        FROM sales
        WHERE sale_time >= date('now','-6 days')
        GROUP BY day ORDER BY day
    """).fetchall()
    stats["sales_7d"] = [dict(r) for r in sales7]

    # Source breakdown
    src = conn.execute(
        "SELECT source, COUNT(*) as cnt, SUM(quantity) as qty FROM products GROUP BY source"
    ).fetchall()
    stats["source_breakdown"] = [dict(r) for r in src]

    conn.close()
    return stats
