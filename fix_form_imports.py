"""Arregla imports obsoletos en form_tab.py"""

with open("ui/form_tab.py", 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar imports obsoletos
old_imports = [
    "from models.materias import get_materias_list",
    "from models.materias import (get_materias_list",
    "get_materias_list,",
]

for old_import in old_imports:
    if old_import in content:
        print(f"[FOUND] {old_import}")
        if "get_materias_list," in content:
            content = content.replace("get_materias_list,", "get_todas_materias,")
        elif "get_materias_list" in content:
            content = content.replace("get_materias_list", "get_todas_materias")

# Reemplazar usos de la función
content = content.replace("get_materias_list()", "get_todas_materias()")

# Guardar
with open("ui/form_tab.py", 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Imports actualizados en form_tab.py")