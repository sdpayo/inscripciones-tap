# test_config.py (en la raíz del proyecto)
from config.settings import BASE_DIR, CSV_FIELDS, DEBUG

print(f"BASE_DIR: {BASE_DIR}")
print(f"DEBUG: {DEBUG}")
print(f"Campos CSV: {len(CSV_FIELDS)}")
print("✅ Config funciona!")