# test_email.py
from services.email_service import (
    load_smtp_config, save_smtp_config, test_smtp_connection
)

# Test guardar/cargar config
config_test = {
    "host": "smtp.gmail.com",
    "port": 587,
    "username": "test@example.com",
    "password": "app_password_here",
    "use_tls": True,
    "from_name": "Escuela Test"
}

ok, msg = save_smtp_config(
    host=config_test["host"],
    port=config_test["port"],
    username=config_test["username"],
    password=config_test["password"],
    use_tls=config_test.get("use_tls", True)
)
assert ok, msg
print("✅ Config SMTP guardada")

config_loaded = load_smtp_config()
assert config_loaded["host"] == "smtp.gmail.com"
print("✅ Config SMTP cargada")

# Test conexión (requiere config real)
# ok, msg = test_smtp_connection(config_loaded)
# print(f"Conexión SMTP: {msg}")

print("\n🎉 Email service funciona!")