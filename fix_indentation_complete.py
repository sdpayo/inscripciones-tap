# fix_indentation_complete.py
"""Arregla toda la indentación del método _build_ui"""

with open("ui/form_tab.py", 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    
    # Si encontramos la definición de _build_ui
    if line.strip() == 'def _build_ui(self):':
        print(f"[Línea {i+1}] Encontrado def _build_ui(self)")
        
        # Agregar con 4 espacios de indentación
        fixed_lines.append('    def _build_ui(self):\n')
        i += 1
        
        # Procesar todo el contenido del método
        method_indent_found = False
        original_indent = None
        
        while i < len(lines):
            current_line = lines[i]
            stripped = current_line.strip()
            
            # Si es línea vacía, mantenerla
            if not stripped:
                fixed_lines.append(current_line)
                i += 1
                continue
            
            # Si encontramos otro método al mismo nivel, terminamos
            if stripped.startswith('def ') and not method_indent_found:
                break
            
            # Calcular indentación original
            current_indent = len(current_line) - len(current_line.lstrip())
            
            # Si es la primera línea con contenido (docstring)
            if not method_indent_found:
                original_indent = current_indent
                method_indent_found = True
            
            # Si encontramos un método con poca indentación, salimos
            if stripped.startswith('def ') and current_indent < 8:
                break
            
            # Calcular nueva indentación
            if original_indent == 0:
                # Estaba sin indentar, agregar 8 espacios (4 clase + 4 método)
                new_indent = 8 + (current_indent - original_indent)
            else:
                # Ya tenía algo de indentación, ajustar
                indent_diff = current_indent - original_indent
                new_indent = 8 + indent_diff
            
            # Agregar línea con nueva indentación
            fixed_lines.append(' ' * new_indent + stripped + '\n')
            i += 1
        
        print(f"  Procesadas {i} líneas del método")
        continue
    
    # Líneas normales
    fixed_lines.append(line)
    i += 1

# Guardar
with open("ui/form_tab.py", 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("\n✅ Archivo corregido")

# Verificar
print("\nVerificando...")
with open("ui/form_tab.py", 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if 'def _build_ui(self):' in line:
        indent = len(line) - len(line.lstrip())
        print(f"\nLínea {i}: def _build_ui(self):")
        print(f"  Indentación: {indent} espacios {'✅' if indent == 4 else '❌'}")
        
        # Mostrar siguientes 5 líneas
        print("\n  Siguientes líneas:")
        for j in range(i, min(i+5, len(lines))):
            next_line = lines[j]
            next_indent = len(next_line) - len(next_line.lstrip())
            marker = "✅" if next_indent >= 8 or not next_line.strip() else "❌"
            print(f"    {j+1}: [{next_indent:2d}] {marker} {next_line.rstrip()[:60]}")
        break