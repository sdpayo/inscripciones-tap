# fix_build_ui_indent.py
"""Corrige la indentación de _build_ui en form_tab.py"""

with open("ui/form_tab.py", 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed_lines = []
in_build_ui = False
in_formtab_class = False

for i, line in enumerate(lines):
    # Detectar clase FormTab
    if line.strip().startswith('class FormTab('):
        in_formtab_class = True
        fixed_lines.append(line)
        continue
    
    # Detectar otra clase (fin de FormTab)
    if in_formtab_class and line.startswith('class ') and 'FormTab' not in line:
        in_formtab_class = False
    
    # Detectar _build_ui sin indentación correcta
    if line.strip().startswith('def _build_ui(self):'):
        indent = len(line) - len(line.lstrip())
        
        if indent == 0:
            print(f"[Línea {i+1}] Corrigiendo indentación de _build_ui")
            # Agregar 4 espacios
            fixed_lines.append('    ' + line)
            in_build_ui = True
            continue
        else:
            fixed_lines.append(line)
            continue
    
    # Si estamos dentro de _build_ui mal indentado, agregar 4 espacios
    if in_build_ui:
        # Verificar si es el siguiente método (termina _build_ui)
        if line.strip().startswith('def ') and '_build_ui' not in line:
            in_build_ui = False
            # Este método también necesita indentación correcta
            if not line.startswith('    '):
                fixed_lines.append('    ' + line)
            else:
                fixed_lines.append(line)
            continue
        
        # Si es una línea de código dentro de _build_ui
        if line.strip():  # No es línea vacía
            if not line.startswith('    '):
                # Agregar 4 espacios si no los tiene
                fixed_lines.append('    ' + line)
            else:
                fixed_lines.append(line)
        else:
            # Línea vacía
            fixed_lines.append(line)
    else:
        fixed_lines.append(line)

# Guardar
with open("ui/form_tab.py", 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("✅ Indentación corregida en form_tab.py")
print("\nVerificando resultado...")

# Verificar
with open("ui/form_tab.py", 'r', encoding='utf-8') as f:
    content = f.read()
    
import re
match = re.search(r'(def _build_ui\(self\):)', content)
if match:
    start = match.start()
    line_start = content.rfind('\n', 0, start) + 1
    line_end = content.find('\n', start)
    line = content[line_start:line_end]
    indent = len(line) - len(line.lstrip())
    
    if indent == 4:
        print("✅ _build_ui ahora tiene indentación correcta (4 espacios)")
    else:
        print(f"⚠️  _build_ui tiene {indent} espacios de indentación")