# test_google_sheets.py
from database.google_sheets import (
    test_google_sheets_connection,
    sync_from_google_sheets,
    sync_to_google_sheets
)
from config.settings import HAS_GS

if not HAS_GS:
    print("⚠️ gspread no instalado. Instala con: pip install gspread google-auth")
    exit()

# Reemplaza con tu Sheet ID real
SHEET_ID = "TU_GOOGLE_SHEET_ID_AQUI"

# Test 1: Conexión
print("Probando conexión...")
ok, msg = test_google_sheets_connection(SHEET_ID)
print(f"{'✅' if ok else '❌'} {msg}")

# Test 2: Subir datos (si hay registros locales)
if ok:
    print("\nSubiendo datos...")
    ok2, msg2 = sync_to_google_sheets(SHEET_ID)
    print(f"{'✅' if ok2 else '❌'} {msg2}")

# Test 3: Descargar datos
if ok:
    print("\nDescargando datos...")
    ok3, msg3 = sync_from_google_sheets(SHEET_ID)
    print(f"{'✅' if ok3 else '❌'} {msg3}")

print("\n🎉 Google Sheets funciona!")