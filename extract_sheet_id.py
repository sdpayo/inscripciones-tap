"""Extrae Sheet ID de una URL de Google Sheets."""
import re
from config.settings import settings

print("=" * 60)
print("EXTRAER SHEET ID")
print("=" * 60)

url = input("\nPegá la URL completa de tu Google Sheet: ").strip()

if not url:
    print("❌ URL vacía")
    exit()

# Extraer ID con regex
patterns = [
    r'/spreadsheets/d/([a-zA-Z0-9-_]+)',
    r'key=([a-zA-Z0-9-_]+)',
    r'^([a-zA-Z0-9-_]+)$'  # Si pegaron solo el ID
]

sheet_id = None
for pattern in patterns:
    match = re.search(pattern, url)
    if match:
        sheet_id = match.group(1)
        break

if not sheet_id:
    print("❌ No se pudo extraer el ID de la URL")
    print("\nEjemplo de URL válida:")
    print("https://docs.google.com/spreadsheets/d/1ABC123xyz.../edit")
    exit()

print(f"\n✅ Sheet ID extraído:")
print(f"   {sheet_id}")

# Guardar en settings.json
print(f"\n💾 Guardando en settings.json...")
settings.set('google_sheets.sheet_key', sheet_id)

print(f"✅ Guardado!")
print(f"\n🔗 URL de tu hoja:")
print(f"   https://docs.google.com/spreadsheets/d/{sheet_id}/edit")

# Verificar que esté compartida
import json
from config.settings import SERVICE_ACCOUNT_FILE

with open(SERVICE_ACCOUNT_FILE, 'r') as f:
    sa = json.load(f)
bot_email = sa['client_email']

print(f"\n⚠️  IMPORTANTE: Asegurate de compartir la hoja con:")
print(f"   {bot_email}")
print(f"\n   Pasos:")
print(f"   1. Abrir la URL arriba ⬆️")
print(f"   2. Click 'Compartir' (botón verde)")
print(f"   3. Agregar: {bot_email}")
print(f"   4. Permisos: Editor")
print(f"   5. Desmarcar 'Notificar'")
print(f"   6. Click 'Compartir'")

input("\nPresioná ENTER cuando hayas compartido la hoja...")

# Test de conexión
print("\n🔄 Probando conexión...")
from database.google_sheets import test_google_sheets_connection

ok, msg = test_google_sheets_connection(sheet_id)
if ok:
    print(f"✅ {msg}")
    print("\n🎉 TODO CONFIGURADO CORRECTAMENTE!")
else:
    print(f"❌ {msg}")
    print("\n🔧 Verificar que:")
    print(f"   1. La hoja esté compartida con {bot_email}")
    print(f"   2. Los permisos sean 'Editor' (no 'Lector')")
    print(f"   3. Esperar 1-2 minutos (propagación de permisos)")