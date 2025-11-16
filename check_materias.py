"""Verifica estructura de materias."""
import json
from config.settings import INSTRUMENTS_FILE

with open(INSTRUMENTS_FILE, 'r', encoding='utf-8') as f:
    materias = json.load(f)

print(f"Total materias: {len(materias)}")
print("\nPrimeras 3 materias completas:\n")

for i, mat in enumerate(materias[:3], 1):
    print(f"{i}. {json.dumps(mat, indent=2, ensure_ascii=False)}")
    print("-" * 60)