"""Limpia y recrea configuración."""
from pathlib import Path
import shutil

data_dir = Path("data")
config_file = data_dir / "config.json"

print("Limpiando configuración...")

# Backup del viejo si existe
if config_file.exists():
    backup = config_file.with_suffix('.json.old')
    shutil.copy(config_file, backup)
    print(f"Backup: {backup}")
    
    # Borrar corrupto
    config_file.unlink()
    print(f"Borrado: {config_file}")

print("\nRecreando configuración...")

# Importar settings (esto creará el nuevo)
from config.settings import settings

print(f"\nOK: Configuración recreada")
print(f"Archivo: {config_file}")