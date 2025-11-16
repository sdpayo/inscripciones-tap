"""Verifica que todo esté configurado correctamente."""
import json
from pathlib import Path
from config.settings import (
    settings, SERVICE_ACCOUNT_FILE, 
    INSTRUMENTS_FILE, HAS_GS, BASE_DIR
)

print("=" * 60)
print("VERIFICACIÓN DE INSTALACIÓN")
print("=" * 60)

errors = []
warnings = []

# 1. service_account.json
print("\n1️⃣ Service Account...")
if SERVICE_ACCOUNT_FILE.exists():
    with open(SERVICE_ACCOUNT_FILE, 'r') as f:
        sa = json.load(f)
    print(f"   ✅ Encontrado")
    print(f"   📧 {sa.get('client_email')}")
    print(f"   🔑 Project: {sa.get('project_id')}")
else:
    print(f"   ❌ NO encontrado: {SERVICE_ACCOUNT_FILE}")
    errors.append("Falta service_account.json")

# 2. Google Sheets
print("\n2️⃣ Google Sheets...")
if HAS_GS:
    print("   ✅ gspread instalado")
    sheet_key = settings.get("google_sheets.sheet_key")
    if sheet_key:
        print(f"   ✅ Sheet ID configurado: {sheet_key[:20]}...")
    else:
        print("   ⚠️  Sheet ID no configurado en settings.json")
        warnings.append("Configurar sheet_key en settings.json")
else:
    print("   ❌ gspread NO instalado")
    errors.append("Instalar: pip install gspread google-auth")

# 3. instruments.json
print("\n3️⃣ Instruments...")
if INSTRUMENTS_FILE.exists():
    with open(INSTRUMENTS_FILE, 'r') as f:
        instruments = json.load(f)
    print(f"   ✅ Encontrado ({len(instruments)} materias)")
else:
    print(f"   ⚠️  NO encontrado: {INSTRUMENTS_FILE}")
    warnings.append("Crear instruments.json con tus materias")

# 4. settings.json
print("\n4️⃣ Settings...")
settings_path = BASE_DIR / "settings.json"
if settings_path.exists():
    print(f"   ✅ Encontrado")
    print(f"   Debug: {settings.get('app.debug')}")
else:
    print("   ⚠️  Se creará automáticamente")

# 5. Estructura de carpetas
print("\n5️⃣ Estructura...")
required_dirs = ['config', 'models', 'database', 'services', 'ui', 'utils']
for d in required_dirs:
    path = BASE_DIR / d
    if path.exists():
        print(f"   ✅ {d}/")
    else:
        print(f"   ❌ {d}/ NO existe")
        errors.append(f"Falta carpeta {d}/")

# Resumen
print("\n" + "=" * 60)
if errors:
    print("❌ ERRORES CRÍTICOS:")
    for e in errors:
        print(f"   • {e}")
if warnings:
    print("\n⚠️  ADVERTENCIAS:")
    for w in warnings:
        print(f"   • {w}")
if not errors and not warnings:
    print("✅ TODO PERFECTO - LISTO PARA USAR")
print("=" * 60)