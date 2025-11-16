"""Test rápido de funcionalidad."""
from database.csv_handler import cargar_registros, guardar_registro, generar_id
from models.materias import get_materias_list, get_profesores_materia, get_comisiones_materia
from services.validators import validar_datos_inscripcion
from datetime import datetime

print("=" * 60)
print("TEST DE FUNCIONALIDAD")
print("=" * 60)

# 1. Materias
print("\n1. Materias:")
materias = get_materias_list()
print(f"   Total: {len(materias)}")
if materias:
    print(f"   Ejemplo: {materias[0]}")
    
    # Profesores
    profes = get_profesores_materia(materias[0])
    print(f"   Profesores de '{materias[0]}': {len(profes)}")
    
    if profes:
        # Comisiones
        coms = get_comisiones_materia(materias[0], profes[0])
        print(f"   Comisiones de '{profes[0]}': {len(coms)}")

# 2. Registros
print("\n2. Registros:")
registros = cargar_registros()
print(f"   Total guardados: {len(registros)}")

# 3. Validación
print("\n3. Validación:")
datos_prueba = {
    "nombre": "Juan",
    "apellido": "Pérez",
    "dni": "12345678",
    "edad": 20,
    "turno": "Mañana",
    "anio": 1,
    "materia": materias[0] if materias else "Test",
    "profesor": profes[0] if profes else "Test",
    "comision": coms[0] if coms else "A"
}

ok, msg = validar_datos_inscripcion(datos_prueba)
print(f"   Validación: {'✅ OK' if ok else '❌ ERROR'}")
print(f"   Mensaje: {msg}")

# 4. Google Sheets
print("\n4. Google Sheets:")
from database.google_sheets import test_google_sheets_connection
from config.settings import settings

sheet_key = settings.get("google_sheets.sheet_key")
if sheet_key:
    ok, msg = test_google_sheets_connection(sheet_key)
    print(f"   Conexión: {'✅' if ok else '❌'} {msg}")
else:
    print("   No configurado")

# 5. SMTP
print("\n5. Email:")
smtp_config = settings.get_section("smtp")
if smtp_config.get("username"):
    print(f"   Usuario: {smtp_config['username']}")
    print(f"   Host: {smtp_config['host']}:{smtp_config['port']}")
else:
    print("   No configurado")

print("\n" + "=" * 60)
print("TEST COMPLETADO")
print("=" * 60)