# fix_csv_handler_duplicate.py
"""Elimina la definición duplicada de guardar_registro en csv_handler.py"""

with open("database/csv_handler.py", 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Buscar las dos definiciones de guardar_registro
definiciones = []
for i, line in enumerate(lines):
    if line.strip().startswith('def guardar_registro('):
        definiciones.append(i)

print(f"Definiciones de guardar_registro encontradas: {len(definiciones)}")

if len(definiciones) == 2:
    print(f"  1. Línea {definiciones[0] + 1}")
    print(f"  2. Línea {definiciones[1] + 1} (DUPLICADA - se eliminará)")
    
    # Mantener la primera, eliminar la segunda
    primera_def = definiciones[0]
    segunda_def = definiciones[1]
    
    # Encontrar el final de la segunda definición
    # (buscar la siguiente función o el final del archivo)
    fin_segunda = len(lines)
    for i in range(segunda_def + 1, len(lines)):
        line = lines[i]
        # Si encontramos otra función al mismo nivel de indentación
        if line.startswith('def ') and not line.startswith('    '):
            fin_segunda = i
            break
    
    # Crear nuevo contenido sin la segunda definición
    new_lines = lines[:segunda_def] + lines[fin_segunda:]
    
    # Guardar
    with open("database/csv_handler.py", 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"\n✅ Eliminada segunda definición (líneas {segunda_def + 1}-{fin_segunda})")
    print(f"✅ Se mantiene la primera definición (línea {primera_def + 1})")

elif len(definiciones) == 1:
    print("✅ Solo hay una definición de guardar_registro, no hay duplicado")
    
    # Verificar que retorna tupla
    def_line = definiciones[0]
    encontrado_return = False
    
    for i in range(def_line, min(def_line + 30, len(lines))):
        if 'return True,' in lines[i] or 'return False,' in lines[i]:
            encontrado_return = True
            print("✅ La función retorna tupla (bool, str)")
            break
    
    if not encontrado_return:
        print("⚠️  La función NO retorna tupla, necesita corrección")
else:
    print(f"❌ Situación inesperada: {len(definiciones)} definiciones")