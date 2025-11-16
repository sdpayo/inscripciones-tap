"""Verifica estructura de form_tab.py"""
import re

with open("ui/form_tab.py", 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar todos los métodos _build_*
methods = re.findall(r'def (_build_\w+)\(self', content)

print("Métodos _build_* encontrados en form_tab.py:")
print("=" * 60)
for method in methods:
    print(f"  - {method}")

print("\n" + "=" * 60)
print(f"Total: {len(methods)} métodos")

# Buscar el método _build_ui
if '_build_ui' in methods:
    print("\n_build_ui() llama a:")
    match = re.search(r'def _build_ui\(self\):.*?(?=\n    def |\Z)', content, re.DOTALL)
    if match:
        calls = re.findall(r'self\.(_build_\w+)\(\)', match.group())
        for call in calls:
            print(f"  → {call}()")