"""Crea hoja de Google Sheets nueva y la configura."""
import json
from config.settings import SERVICE_ACCOUNT_FILE, HAS_GS, CSV_FIELDS

if not HAS_GS:
    print("❌ Instalar: pip install gspread google-auth")
    exit()

if not SERVICE_ACCOUNT_FILE.exists():
    print(f"❌ Falta: {SERVICE_ACCOUNT_FILE}")
    exit()

# Leer service account email
with open(SERVICE_ACCOUNT_FILE, 'r') as f:
    sa_data = json.load(f)
    sa_email = sa_data['client_email']

print(f"📧 Service Account: {sa_email}")

import gspread
from google.oauth2.service_account import Credentials

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_file(
    str(SERVICE_ACCOUNT_FILE),
    scopes=scopes
)
gc = gspread.authorize(creds)

# Crear hoja
print("\n📊 Creando hoja...")
sh = gc.create("Inscripciones ESM - 2025")

# Compartir contigo
your_email = input("Ingresá tu email personal para acceso: ")
sh.share(your_email, perm_type='user', role='writer')

print(f"\n✅ Hoja creada: {sh.title}")
print(f"   URL: {sh.url}")
print(f"   ID: {sh.id}")

# Agregar headers
ws = sh.sheet1
ws.update([CSV_FIELDS], value_input_option='RAW')
print(f"\n✅ Headers configurados")

# Guardar ID en settings.json
from config.settings import settings
settings.set("google_sheets.sheet_key", sh.id)
print(f"\n✅ ID guardado en settings.json")

print(f"\n🎉 Todo listo! Abrí: {sh.url}")