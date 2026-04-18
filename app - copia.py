from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client

app = Flask(__name__)
app.secret_key = "clave_secreta_cambiame"  # cambiá esto en producción

DB = "database.db"

# ──────────────────────────────────────────────
# BASE DE DATOS
# ──────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            precio REAL NOT NULL,
            imagen TEXT,
            stock INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_cliente TEXT NOT NULL,
            email TEXT NOT NULL,
            total REAL NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedido_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER,
            producto_id INTEGER,
            cantidad INTEGER,
            precio_unitario REAL,
            FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM productos")
    if cursor.fetchone()[0] == 0:
        productos_ejemplo = [
            ("Remera básica", "100% algodón, varios colores", 4500.00, "remera.jpg", 10),
            ("Pantalón cargo", "Con bolsillos laterales", 8900.00, "pantalon.jpg", 5),
            ("Zapatillas urbanas", "Suela de goma reforzada", 15000.00, "zapatillas.jpg", 8),
        ]
        cursor.executemany(
            "INSERT INTO productos (nombre, descripcion, precio, imagen, stock) VALUES (?, ?, ?, ?, ?)",
            productos_ejemplo
        )

    conn.commit()
    conn.close()

# ──────────────────────────────────────────────
# NOTIFICACIONES (EMAIL + WHATSAPP)
# ──────────────────────────────────────────────

def enviar_email(destinatario, asunto, mensaje):
    remitente = "tuemail@gmail.com"
    password = "tu_password_app"  # contraseña de aplicación
    msg = MIMEText(mensaje, "plain", "utf-8")
    msg["Subject"] = asunto
    msg["From"] = remitente
    msg["To"] = destinatario

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(remitente, password)
        server.sendmail(remitente, [destinatario], msg.as_string())

def enviar_whatsapp(destinatario, mensaje):
    account_sid = "TU_ACCOUNT_SID"
    auth_token = "TU_AUTH_TOKEN"
    client = Client(account_sid, auth_token)

    client.messages.create(
        from_="whatsapp:+14155238886",  # número de Twilio
        body=mensaje,
        to=f"whatsapp:{destinatario}"   # ej: whatsapp:+54911XXXXXXXX
    )

# ──────────────────────────────────────────────
# HELPERS DEL CARRITO
# ──────────────────────────────────────────────

def get_carrito():
    return session.get("carrito", {})

def guardar_carrito(carrito):
    session["carrito"] = carrito

def total_carrito():
    carrito = get_carrito()
    if not carrito:
        return 0
    conn = get_db()
    total = 0
    for pid, cantidad in carrito.items():
        row = conn.execute("SELECT precio FROM productos WHERE id = ?", (pid,)).fetchone()
        if row:
            total += row["precio"] * cantidad
    conn.close()
    return total

# ──────────────────────────────────────────────
# RUTAS — TIENDA
# ──────────────────────────────────────────────

@app.route("/")
def index():
    conn = get_db()
    productos = conn.execute("SELECT * FROM productos WHERE stock > 0").fetchall()
    conn.close()
    return render_template("index.html", productos=productos)

@app.route("/producto/<int:id>")
def producto(id):
    conn = get_db()
    p = conn.execute("SELECT * FROM productos WHERE id = ?", (id,)).fetchone()
    conn.close()
    if not p:
        return "Producto no encontrado", 404
    return render_template("producto.html", producto=p)

# ──────────────────────────────────────────────
# RUTAS — CARRITO
# ──────────────────────────────────────────────

@app.route("/carrito")
def carrito():
    carrito = get_carrito()
    items = []
    conn = get_db()
    for pid, cantidad in carrito.items():
        p = conn.execute("SELECT * FROM productos WHERE id = ?", (pid,)).fetchone()
        if p:
            items.append({
                "id": p["id"],
                "nombre": p["nombre"],
                "precio": p["precio"],
                "cantidad": cantidad,
                "subtotal": p["precio"] * cantidad,
            })
    conn.close()
    return render_template("carrito.html", items=items, total=total_carrito())

@app.route("/carrito/agregar/<int:id>", methods=["POST"])
def agregar_al_carrito(id):
    carrito = get_carrito()
    cantidad = int(request.form.get("cantidad", 1))
    clave = str(id)
    carrito[clave] = carrito.get(clave, 0) + cantidad
    guardar_carrito(carrito)
    return redirect(url_for("carrito"))

@app.route("/carrito/quitar/<int:id>")
def quitar_del_carrito(id):
    carrito = get_carrito()
    carrito.pop(str(id), None)
    guardar_carrito(carrito)
    return redirect(url_for("carrito"))

@app.route("/carrito/vaciar")
def vaciar_carrito():
    session.pop("carrito", None)
    return redirect(url_for("carrito"))

# ──────────────────────────────────────────────
# RUTAS — CHECKOUT
# ──────────────────────────────────────────────

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    carrito = get_carrito()
    if not carrito:
        return redirect(url_for("carrito"))

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip()

        if not nombre or not email:
            return render_template("checkout.html", error="Completá todos los campos.", total=total_carrito())

        total = total_carrito()
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO pedidos (nombre_cliente, email, total) VALUES (?, ?, ?)",
            (nombre, email, total)
        )
        pedido_id = cursor.lastrowid

        for pid, cantidad in carrito.items():
            p = conn.execute("SELECT precio FROM productos WHERE id = ?", (pid,)).fetchone()
            if p:
                cursor.execute(
                    "INSERT INTO pedido_items (pedido_id, producto_id, cantidad, precio_unitario) VALUES (?, ?, ?, ?)",
                    (pedido_id, int(pid), cantidad, p["precio"])
                )
                conn.execute(
                    "UPDATE productos SET stock = stock - ? WHERE id = ?",
                    (cantidad, int(pid))
                )

        conn.commit()
        conn.close()
        session.pop("carrito", None)

        # ── Notificaciones ──
        mensaje = f"Hola {nombre}, gracias por tu compra.\nTu pedido #{pedido_id} fue confirmado por ${total:.2f}."
        enviar_email(email, "Confirmación de compra - MiTienda", mensaje)
        # Cambiá el número por el del cliente
        enviar_whatsapp("+54911XXXXXXXX", mensaje)

        return render_template("checkout.html", confirmado=True, nombre=nombre, pedido_id=pedido_id)

    return render_template("checkout.html", total=total_carrito())

# ──────────────────────────────────────────────
# RUTAS — USUARIOS
# ──────────────────────────────────────────────

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        conn = get_db()
        try:
            conn.execute("INSERT INTO usuarios (nombre, email, password) VALUES (?, ?, ?)",
                         (nombre, email, password))
            conn.commit()
        except sqlite3.IntegrityError:
            return render_template("registro.html", error="El email ya está registrado.")
        finally:
            conn.close()
        return redirect(url_for("login"))
    return render_template("registro.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        conn = get_db()
        user = conn.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user["password"], password):
            session["usuario"] = user["nombre"]
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Email o contraseña incorrectos.")
    return render_template("login.html")

# ──────────────────────────────────────────────
# BLOQUE DE ARRANQUE
# ──────────────────────────────────────────────
if __name__ == "__main__":
    init_db()  # inicializa la base de datos si no existe
    app.run(debug=True)
