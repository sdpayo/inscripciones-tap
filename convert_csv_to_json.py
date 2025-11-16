"""Convierte Materias_TAP.csv a instruments.json."""
import csv
import json
from pathlib import Path

# Archivos
csv_file = Path("Materias_TAP.csv")
json_file = Path("instruments.json")

# Verificar que existe el CSV
if not csv_file.exists():
    print(f"ERROR: {csv_file} no existe")
    exit(1)

print("=" * 60)
print("CONVERTIR MATERIAS_TAP.CSV → INSTRUMENTS.JSON")
print("=" * 60)

# Leer CSV
materias = []
with open(csv_file, 'r', encoding='utf-8-sig', newline='') as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        # Limpiar y normalizar datos
        profesor = row.get('Docente', '').strip().replace('\n', '').replace('\r', '')
        turno = row.get('Turno', '').strip() or "Mañana"
        
        # Convertir cupo
        try:
            cupo = int(row.get('CUPOS', '').strip())
        except (ValueError, AttributeError):
            cupo = 30  # Default para grupales sin cupo definido
        
        # Convertir año
        try:
            anio = int(row.get('Año', '1').strip())
        except (ValueError, AttributeError):
            anio = 1
        
        # Crear registro
        materia = {
            "materia": row.get('Asignatura', '').strip(),
            "profesor": profesor,
            "comision": row.get('Div.', '').strip(),
            "año": anio,
            "cupo": cupo,
            "turno": turno,
            "tipo": row.get('Tipo', '').strip()
        }
        
        materias.append(materia)

print(f"\nTotal registros leídos: {len(materias)}")

# Estadísticas
materias_unicas = len(set(m['materia'] for m in materias if m['materia']))
profesores_unicos = len(set(m['profesor'] for m in materias if m['profesor']))
comisiones_unicas = len(set(m['comision'] for m in materias if m['comision']))

print(f"\nEstadísticas:")
print(f"  Materias únicas: {materias_unicas}")
print(f"  Profesores únicos: {profesores_unicos}")
print(f"  Comisiones únicas: {comisiones_unicas}")

# Mostrar muestra
print(f"\nPrimeras 5 materias:")
for i, mat in enumerate(materias[:5], 1):
    print(f"\n  {i}. {mat['materia']}")
    print(f"     Profesor: {mat['profesor']}")
    print(f"     Comisión: {mat['comision']}")
    print(f"     Año: {mat['año']}")
    print(f"     Turno: {mat['turno']}")
    print(f"     Cupo: {mat['cupo']}")
    print(f"     Tipo: {mat['tipo']}")

# Guardar JSON
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(materias, f, indent=2, ensure_ascii=False)

print(f"\n{'='*60}")
print(f"OK: Guardado en {json_file}")
print(f"Total registros: {len(materias)}")
print(f"{'='*60}")