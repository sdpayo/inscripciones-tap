# check_instruments.py
import json
from pathlib import Path

instruments_file = Path("data/instruments.json")

if not instruments_file.exists():
    print(f"❌ No existe: {instruments_file}")
else:
    with open(instruments_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ Archivo cargado: {len(data)} registros")
    print("\n📋 Estructura del primer registro:")
    print("=" * 60)
    
    if data:
        first = data[0]
        for key, value in first.items():
            print(f"  {key}: {value}")
    
    print("\n📊 Campos disponibles:")
    print("=" * 60)
    all_keys = set()
    for item in data[:10]:  # Primeros 10
        all_keys.update(item.keys())
    
    for key in sorted(all_keys):
        print(f"  - {key}")
    
    print("\n🔍 Verificar campo de año:")
    print("=" * 60)
    year_fields = ["año", "anio", "Año", "year", "curso"]
    for field in year_fields:
        if any(field in item for item in data[:5]):
            print(f"  ✅ Campo encontrado: '{field}'")
            # Mostrar valores únicos
            values = set(item.get(field) for item in data if field in item)
            print(f"     Valores: {sorted(values)}")