# 🛍️ Tienda Virtual Flask

Aplicación web simple de tienda virtual desarrollada con **Flask** y **SQLite**.  
Permite mostrar productos, gestionar un carrito de compras y realizar pedidos.  
Incluye sistema de usuarios con registro, login, logout y recuperación de contraseña.

---

## 🚀 Instalación

1. Clonar el repositorio:
   git clone https://github.com/usuario/tienda-04-26.git
   cd tienda-04-26

2. Crear entorno virtual (opcional pero recomendado):
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows

3. Instalar dependencias:
   pip install -r requirements.txt

---

## ▶️ Uso

1. Inicializar la base de datos y correr el servidor:
   python app.py

2. Abrir en el navegador:
   http://127.0.0.1:5000

---

## 📂 Estructura del proyecto

tienda-04-26/
│
├── app.py                  # servidor Flask, rutas principales
├── database.db             # base de datos SQLite
├── models/
│   └── db.py               # conexión y definición de tablas
├── templates/              # vistas HTML (productos, carrito, checkout, usuarios)
├── static/                 # CSS, JS, imágenes
├── requirements.txt        # dependencias
└── README.md               # instrucciones del proyecto

---

## ✨ Funcionalidades

- Catálogo de productos con imágenes y stock.
- Carrito de compras persistente en sesión.
- Checkout con registro de pedidos.
- Sistema de usuarios:
  - Registro
  - Login / Logout
  - Recuperación de contraseña

---

## ⚠️ Notas

- Cambiar `app.secret_key` en producción por una clave segura.
- La base de datos `database.db` se crea automáticamente al iniciar la aplicación.
- Se pueden agregar librerías opcionales como `flask-mail` o `bcrypt` para ampliar funcionalidades.
