# test_database.py
from database.csv_handler import (
    ensure_csv, cargar_registros, upsert_registro, 
    eliminar_registro_por_legajo
)
from datetime import datetime

# 1. Crear CSV
ensure_csv()
print("✅ CSV creado")

# 2. Insertar registro
registro = {
    "id": "TEST001",
    "legajo": "TEST001",
    "nombre": "Juan",
    "apellido": "Pérez",
    "fecha_inscripcion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "materia": "Piano"
}
upsert_registro(registro)
print("✅ Registro insertado")

# 3. Leer
registros = cargar_registros()
assert len(registros) == 1
assert registros[0]["nombre"] == "Juan"
print("✅ Lectura OK")

# 4. Actualizar
registro["nombre"] = "Carlos"
upsert_registro(registro)
registros = cargar_registros()
assert registros[0]["nombre"] == "Carlos"
print("✅ Actualización OK")

# 5. Eliminar
eliminar_registro_por_legajo("TEST001")
registros = cargar_registros()
assert len(registros) == 0
print("✅ Eliminación OK")

print("\n🎉 Database funciona perfectamente!")