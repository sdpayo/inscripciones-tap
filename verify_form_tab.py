# verify_form_tab.py
import re

with open("ui/form_tab.py", 'r', encoding='utf-8') as f:
    content = f.read()

# Verificar que FormTab hereda de BaseTab
if "class FormTab(BaseTab):" in content:
    print("✅ FormTab hereda correctamente de BaseTab")
else:
    print("❌ Problema con la definición de clase")
    if "class FormTab" in content:
        match = re.search(r'class FormTab\([^)]*\):', content)
        if match:
            print(f"   Encontrado: {match.group()}")

# Buscar definición de _build_ui
matches = list(re.finditer(r'def _build_ui\(self.*?\):', content))

print(f"\n{'='*60}")
print(f"Definiciones de _build_ui encontradas: {len(matches)}")
print(f"{'='*60}")

for i, match in enumerate(matches, 1):
    start = match.start()
    # Contar líneas hasta este punto
    line_no = content[:start].count('\n') + 1
    
    # Obtener la línea completa
    line_start = content.rfind('\n', 0, start) + 1
    line_end = content.find('\n', start)
    line = content[line_start:line_end]
    
    # Calcular indentación
    indent = len(line) - len(line.lstrip())
    
    print(f"\n#{i} - Línea {line_no}:")
    print(f"   {line}")
    print(f"   Indentación: {indent} espacios", end="")
    
    if indent == 4:
        print(" ✅ (correcta para método de clase)")
    elif indent == 0:
        print(" ❌ (no está dentro de una clase)")
    else:
        print(f" ⚠️  (inusual)")

# Verificar si hay múltiples definiciones
if len(matches) > 1:
    print(f"\n⚠️  ADVERTENCIA: Hay {len(matches)} definiciones de _build_ui")
    print("   Solo debería haber UNA dentro de la clase FormTab")