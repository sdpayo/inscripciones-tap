import json
from config.settings import INSTRUMENTS_FILE
import shutil

print("Convirtiendo instruments.json...")

# Backup
backup = INSTRUMENTS_FILE.with_suffix('.json.backup')
shutil.copy(INSTRUMENTS_FILE, backup)
print(f"Backup: {backup.name}")

# Cargar
with open(INSTRUMENTS_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Formato actual: dict con {len(data)} materias")

# Convertir dict a list
lista_materias = []

for nombre_materia, config in data.items():
    if isinstance(config, dict):
        # Asegurar que tenga el campo 'materia'
        if "materia" not in config:
            config["materia"] = nombre_materia
        lista_materias.append(config)
    else:
        # Si el valor no es dict, crear uno básico
        lista_materias.append({
            "materia": nombre_materia,
            "profesor": "",
            "comision": "",
            "turno": "",
            "año": 1,
            "cupo": 0
        })

print(f"\nConvertidas {len(lista_materias)} materias")

# Mostrar muestra
print("\nPrimeras 5 materias:")
for i, mat in enumerate(lista_materias[:5], 1):
    print(f"  {i}. {mat['materia']}")
    print(f"     Profesor: {mat.get('profesor', 'N/A')}")
    print(f"     Comision: {mat.get('comision', 'N/A')}")

# Guardar
with open(INSTRUMENTS_FILE, 'w', encoding='utf-8') as f:
    json.dump(lista_materias, f, indent=2, ensure_ascii=False)

print(f"\nOK: Guardado en formato lista")
print(f"Backup guardado en: {backup.name}")