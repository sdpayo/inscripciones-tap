"""Verifica qué APIs están habilitadas."""
import json
from config.settings import SERVICE_ACCOUNT_FILE

with open(SERVICE_ACCOUNT_FILE, 'r') as f:
    sa = json.load(f)

project_id = sa['project_id']
project_number = sa.get('project_number', 'N/A')

print("=" * 60)
print("VERIFICAR APIs HABILITADAS")
print("=" * 60)
print(f"\n🔑 Proyecto: {project_id}")
print(f"📊 Project Number: {project_number}")

print("\n📋 APIs necesarias:")
apis = [
    ("Google Sheets API", f"https://console.developers.google.com/apis/api/sheets.googleapis.com/overview?project={project_id}"),
    ("Google Drive API", f"https://console.developers.google.com/apis/api/drive.googleapis.com/overview?project={project_id}")
]

for name, url in apis:
    print(f"\n   • {name}")
    print(f"     {url}")

print("\n" + "=" * 60)
print("🔧 INSTRUCCIONES:")
print("=" * 60)
print("\n1. Abrir AMBOS links arriba ⬆️")
print("2. En cada uno, verificar que diga 'API habilitada'")
print("3. Si dice 'HABILITAR', hacer click")
print("4. Esperar 30 segundos después de habilitar")
print("\n" + "=" * 60)

input("\nPresioná ENTER cuando hayas habilitado ambas APIs...")

# Test básico
print("\n🧪 Probando conexión básica...")
try:
    from config.settings import HAS_GS
    if not HAS_GS:
        print("❌ gspread no instalado")
        exit()
    
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
    
    print("✅ Autenticación OK")
    
    # Intentar listar hojas (usa Drive API)
    try:
        sheets = gc.openall()
        print(f"✅ Google Drive API OK ({len(sheets)} hojas accesibles)")
    except Exception as e:
        if "accessNotConfigured" in str(e) or "SERVICE_DISABLED" in str(e):
            print("❌ Google Drive API aún deshabilitada")
            print("   Esperar 1-2 minutos y reintentar")
        else:
            print(f"⚠️  Error: {e}")
    
except Exception as e:
    print(f"❌ Error: {e}")