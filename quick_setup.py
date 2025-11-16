"""Setup rápido con hoja existente."""
import json
from config.settings import settings, SERVICE_ACCOUNT_FILE

print("=" * 60)
print("SETUP RÁPIDO - USAR HOJA EXISTENTE")
print("=" * 60)

# Leer bot email
with open(SERVICE_ACCOUNT_FILE, 'r') as f:
    sa = json.load(f)
bot_email = sa['client_email']
project = sa['project_id']

print(f"\n🔑 Proyecto: {project}")
print(f"📧 Email del bot: {bot_email}")

# ID de tu hoja (el que pusiste antes)
sheet_id = "1ZONKz7Hg54YuGRFNJ24DD-ZCIeFmhwuWbaeO_LvwTkw"

print(f"\n📊 Usando hoja existente")
print(f"   ID: {sheet_id}")
print(f"   URL: https://docs.google.com/spreadsheets/d/{sheet_id}/edit")

# Guardar en settings
settings.set('google_sheets.sheet_key', sheet_id)
print(f"\n✅ ID guardado en settings.json")

# Instrucciones para compartir
print("\n" + "=" * 60)
print("🔧 AHORA COMPARTIR LA HOJA CON EL BOT:")
print("=" * 60)
print(f"\n1. Abrir: https://docs.google.com/spreadsheets/d/{sheet_id}/edit")
print(f"2. Click 'Compartir' (botón verde)")
print(f"3. Agregar este email:")
print(f"   {bot_email}")
print(f"4. Cambiar permisos a: Editor")
print(f"5. Desmarcar 'Notificar a las personas'")
print(f"6. Click 'Compartir'")

input("\n✋ Presioná ENTER cuando hayas compartido la hoja...")

# Test de conexión
print("\n🔄 Probando conexión...")
from database.google_sheets import test_google_sheets_connection

ok, msg = test_google_sheets_connection(sheet_id)

if ok:
    print(f"\n✅ {msg}")
    print("\n🎉 TODO CONFIGURADO CORRECTAMENTE!")
    print("=" * 60)
else:
    print(f"\n❌ {msg}")
    print("\n🔍 Verificar:")
    print(f"   • La hoja esté compartida con: {bot_email}")
    print(f"   • Permisos sean 'Editor' (no 'Lector')")
    print(f"   • Esperar 1-2 minutos después de compartir")