# test_validators.py
from services.validators import validar_campos_y_mostrar, validar_dni, validar_legajo

# Test campos completos
campos_ok = {
    "nombre": "Juan",
    "apellido": "Pérez",
    "legajo": "12345",
    "mail": "juan@example.com",
    "materia": "Piano",
    "anio": "1",
    "turno": "Mañana"
}
errores = validar_campos_y_mostrar(campos_ok)
assert len(errores) == 0, f"No debería haber errores: {errores}"
print("✅ Validación completa OK")

# Test campos incompletos
campos_mal = {
    "nombre": "",
    "apellido": "Pérez",
    "legajo": "12345"
}
errores = validar_campos_y_mostrar(campos_mal)
assert len(errores) > 0
print(f"✅ Detectó {len(errores)} errores correctamente")

# Test DNI
assert validar_dni("12.345.678") == True
assert validar_dni("12345678") == True
assert validar_dni("ABC123") == False
print("✅ Validación DNI OK")

# Test legajo
assert validar_legajo("LEG123") == True
assert validar_legajo("12345") == True
assert validar_legajo("LEG-123") == False
print("✅ Validación legajo OK")

print("\n🎉 Validators funcionan!")