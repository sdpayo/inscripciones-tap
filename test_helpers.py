from utils.helpers import _norm_key, _sanitize_filename, validar_email

assert _norm_key("Cañón") == "canon"
assert _sanitize_filename("Mi Archivo 123.pdf") == "Mi_Archivo_123.pdf"
assert validar_email("test@example.com") == True
assert validar_email("invalid") == False
print("✅ Helpers funcionan!")