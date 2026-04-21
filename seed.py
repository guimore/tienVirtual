import sqlite3

def cargar_datos():
    print("🚀 Iniciando carga de productos...")
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # 1. Limpiamos solo los productos (no toca usuarios ni pedidos)
    cursor.execute("DELETE FROM productos")

    # 2. Los 9 productos para tu grilla 3x3
    productos_ejemplo = [
        ("Bici Pro Rodado 29", "Aluminio, 21 cambios", 450000.0, "bici1.jpg", 5),
        ("Casco Seguridad", "Certificado internacional", 25000.0, "casco.jpg", 10),
        ("Remera Ciclista", "Tela dry-fit", 12000.0, "remera.jpg", 15),
        ("Inflador de Mano", "Doble válvula", 8500.0, "inflador.jpg", 20),
        ("Luces LED Pack", "Delantera y trasera", 15000.0, "luces.jpg", 8),
        ("Cadena de Acero", "Anti-robo reforzada", 18000.0, "cadena.jpg", 12),
        ("Guantes Gel", "Antideslizantes", 9500.0, "guantes.jpg", 10),
        ("Bermuda Térmica", "Ciclismo urbano", 14000.0, "bermuda.jpg", 7),
        ("Caramañola 750ml", "Libre de BPA", 4500.0, "botella.jpg", 25)
    ]

    cursor.executemany(
        "INSERT INTO productos (nombre, descripcion, precio, imagen, stock) VALUES (?, ?, ?, ?, ?)",
        productos_ejemplo
    )

    conn.commit()
    conn.close()
    print("✅ ¡9 productos cargados con éxito! Ya podés ver tu grilla 3x3.")

if __name__ == "__main__":
    cargar_datos()