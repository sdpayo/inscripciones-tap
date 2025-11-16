"""Verifica estructura de archivos."""
from pathlib import Path

print("Verificando estructura...\n")

base = Path(".")
required_files = [
    "data/instruments.json",
    "data/inscripciones.csv",
    "main.py",
    "ui/app.py",
    "ui/form_tab.py",
    "ui/config_tab.py",
    "ui/listados_tab.py",
    "ui/historial_tab.py",
]

for file in required_files:
    path = base / file
    status = "✅" if path.exists() else "❌"
    print(f"{status} {file}")

print("\nBuscando instruments.json en otras ubicaciones...")
for json_file in base.rglob("instruments.json"):
    print(f"  Encontrado en: {json_file}")
    
print("\nSi instruments.json está fuera de data/, moverlo con:")
print("  move instruments.json data\\instruments.json")