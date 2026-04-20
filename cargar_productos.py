import sqlite3

# Conectar a la base
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Insertar productos de prueba
productos = [
    ("Remera básica", "100% algodón, varios colores", 4500, "remera.jpg", 10),
    ("Pantalón jeans", "Denim azul clásico", 12000, "pantalon.jpg", 5),
    ("Zapatillas urbanas", "Cómodas y resistentes", 18000, "zapatillas.jpg", 8),
    ("Campera deportiva", "Ideal para invierno", 22000, "campera.jpg", 7),
    ("Gorra casual", "Algodón, varios colores", 3500, "gorra.jpg", 15),
    ("Buzo hoodie", "Con capucha y bolsillo frontal", 15000, "buzo.jpg", 12),
    ("Camisa formal", "Slim fit, manga larga", 17000, "camisa.jpg", 6),
    ("Short deportivo", "Secado rápido", 8000, "short.jpg", 9),
    ("Medias pack x3", "Algodón, talle único", 2500, "medias.jpg", 20),
]

cursor.executemany(
    "INSERT INTO productos (nombre, descripcion, precio, imagen, stock) VALUES (?, ?, ?, ?, ?)",
    productos
)

conn.commit()
conn.close()

print("Productos insertados correctamente.")
