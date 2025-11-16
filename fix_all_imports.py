"""Arregla imports obsoletos en todos los archivos UI."""
from pathlib import Path

files_to_fix = [
    "ui/form_tab.py",
    "ui/listados_tab.py",
    "ui/historial_tab.py",
]

for file_path in files_to_fix:
    path = Path(file_path)
    
    if not path.exists():
        print(f"⚠️  No existe: {file_path}")
        continue
    
    print(f"Procesando: {file_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Reemplazar imports
    replacements = [
        ("from models.materias import get_materias_list", 
         "from models.materias import get_todas_materias"),
        
        ("get_materias_list,", "get_todas_materias,"),
        ("get_materias_list ", "get_todas_materias "),
        ("get_materias_list()", "get_todas_materias()"),
    ]
    
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            print(f"  ✅ Reemplazado: {old}")
    
    # Guardar solo si hubo cambios
    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  💾 Guardado: {file_path}")
    else:
        print(f"  ℹ️  Sin cambios: {file_path}")
    
    print()

print("✅ Proceso completado")