"""Diagnostica formato de instruments.json."""
import json
from config.settings import INSTRUMENTS_FILE, MERGED_FILE

def diagnosticar():
    file_to_check = MERGED_FILE if MERGED_FILE.exists() else INSTRUMENTS_FILE
    
    print("=" * 60)
    print(f"DIAGNÓSTICO: {file_to_check}")
    print("=" * 60)
    
    if not file_to_check.exists():
        print("❌ Archivo no existe")
        return
    
    try:
        with open(file_to_check, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\n✅ JSON válido")
        print(f"Tipo de datos: {type(data).__name__}")
        
        if isinstance(data, list):
            print(f"Total de elementos: {len(data)}")
            
            if len(data) > 0:
                print(f"\n📋 Primeros 3 elementos:")
                for i, item in enumerate(data[:3], 1):
                    print(f"\n  {i}. Tipo: {type(item).__name__}")
                    if isinstance(item, dict):
                        print(f"     Claves: {list(item.keys())}")
                        print(f"     Materia: {item.get('materia', 'N/A')}")
                    else:
                        print(f"     Valor: {item}")
                
                # Contar tipos
                tipos = {}
                for item in data:
                    tipo = type(item).__name__
                    tipos[tipo] = tipos.get(tipo, 0) + 1
                
                print(f"\n📊 Resumen de tipos:")
                for tipo, count in tipos.items():
                    print(f"   {tipo}: {count}")
                
                # Verificar si todos son dict
                if all(isinstance(item, dict) for item in data):
                    print(f"\n✅ Formato correcto: todos los elementos son diccionarios")
                    
                    # Verificar campos
                    campos = set()
                    for item in data:
                        campos.update(item.keys())
                    
                    print(f"\n📝 Campos encontrados:")
                    for campo in sorted(campos):
                        print(f"   • {campo}")
                else:
                    print(f"\n⚠️  PROBLEMA: No todos los elementos son diccionarios")
                    print(f"   Se necesita formato: [{{'materia': '...', 'profesor': '...'}}, ...]")
        else:
            print(f"⚠️  PROBLEMA: Se esperaba una lista, se encontró {type(data).__name__}")
    
    except json.JSONDecodeError as e:
        print(f"❌ Error de formato JSON: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    diagnosticar()