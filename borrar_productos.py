import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Borro los dos productos que no querés mostrar
cursor.execute("DELETE FROM productos WHERE nombre = 'Short deportivo'")
cursor.execute("DELETE FROM productos WHERE nombre = 'Medias pack x3'")

conn.commit()
conn.close()

print("Productos eliminados correctamente.")
