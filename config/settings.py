"""Configuración global de la aplicación."""
import json
from pathlib import Path

# Rutas base
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CONFIG_FILE = DATA_DIR / "config.json"

# Archivos de datos
INSTRUMENTS_FILE = DATA_DIR / "instruments.json"
MERGED_FILE = DATA_DIR / "merged.json"
CSV_FILE = DATA_DIR / "inscripciones.csv"
DATA_DIR = BASE_DIR / "data"
INSCRIPCIONES_FILE = CSV_FILE


# Directorios de salida
CERTIFICATES_DIR = DATA_DIR / "certificates"
REPORTS_DIR = DATA_DIR / "reports"
LOGS_DIR = DATA_DIR / "logs"

# Archivos de configuración (para compatibilidad)
SMTP_CONFIG_FILE = CONFIG_FILE
GOOGLE_SHEETS_CONFIG_FILE = CONFIG_FILE

# Constantes
DEBUG = False

# Crear directorios si no existen
DATA_DIR.mkdir(exist_ok=True)
CERTIFICATES_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)


CSV_FIELDS = [
    "id", "fecha_inscripcion", "nombre", "apellido", "dni",
    "fecha_nacimiento", "edad", "legajo", "direccion", "telefono", "email",
    "nombre_padre", "nombre_madre", "telefono_emergencia",
    "saeta", "obra_social", "seguro_escolar", "pago_voluntario",
    "monto", "permiso", "observaciones",
    "anio", "turno", "materia", "profesor", "comision", "horario",
    "en_lista_espera"
]

# Configuración por defecto
DEFAULT_CONFIG = {
    "app": {
        "check_cupos": True,
        "require_seguro_escolar": True,
        "auto_backup": True,
        "backup_interval_days": 7,
        "debug": False,
        "auto_refresh": True
    },
    "ui": {
        "theme": "clam",
        "font_size": 10
    },
    "smtp": {
        "host": "smtp.gmail.com",
        "port": 587,
        "use_tls": True,
        "username": "",
        "password": ""
    },
    "google_sheets": {
       "enabled": True,  # ← Agregar esto
        "spreadsheet_id": "PEGA_AQUI_EL_ID_DE_TU_HOJA1LYzWjGeJeEzBylSU1eI7Sn4gsmT-FPNTflYIsJWfGEc",  # ← Cambiar nombre
        "sheet_name": "Inscripciones",  # ← Agregar esto
        "credentials_path": "credentials.json",  # ← Cambiar nombre
        "auto_sync": True,  # ← Cambiar a True para que sincronice automáticamente
        "has_header_row": False,  # ← SI GOOGLE SHEETS TIENE HEADER EN LA FILA 1, cambiar a True
        "sync_mode": "incremental",  # ← "incremental" o "full" - incremental es más eficiente
        "sync_window_hours": 24  # ← Ventana de tiempo para sync incremental (horas)
    },
    "pdf": {
        "logo_path": "",
        "institution_name": "Escuela Superior de Música N°6003",
        "footer_text": "Este certificado es válido con firma y sello de la institución"
    }
}


class Settings:
    """Gestor de configuración."""
    
    def __init__(self):
        """Inicializa configuración."""
        self.config = DEFAULT_CONFIG.copy()
        self.config = self._load_config()
    
    def _load_config(self):
        """Carga configuración desde archivo."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        # Archivo vacío, usar defaults
                        print("[INFO] config.json vacío, usando configuración por defecto")
                        self.save()
                        return DEFAULT_CONFIG.copy()
                    
                    config = json.loads(content)
                    # Merge con defaults (por si faltan claves nuevas)
                    return self._merge_configs(DEFAULT_CONFIG, config)
            except json.JSONDecodeError as e:
                print(f"[WARN] config.json corrupto: {e}")
                print("[INFO] Recreando configuración por defecto")
                # Borrar archivo corrupto
                CONFIG_FILE.unlink()
                self.save()
                return DEFAULT_CONFIG.copy()
            except Exception as e:
                print(f"[WARN] No se pudo cargar config: {e}")
                return DEFAULT_CONFIG.copy()
        else:
            # Crear config por defecto
            print("[INFO] Creando config.json con valores por defecto")
            self.save()
            return DEFAULT_CONFIG.copy()
    
    def _merge_configs(self, default, loaded):
        """Merge recursivo de configs."""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def save(self):
        """Guarda configuración a archivo."""
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"[INFO] Configuración guardada en {CONFIG_FILE}")
        except Exception as e:
            print(f"[ERROR] No se pudo guardar config: {e}")
    
    def get(self, key, default=None):
        """
        Obtiene valor de configuración.
        Args:
            key (str): Clave en formato "section.key"
            default: Valor por defecto
        Returns:
            Valor configurado o default
        """
        parts = key.split('.')
        value = self.config
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        
        return value
    
    def set(self, key, value):
        """
        Establece valor de configuración.
        Args:
            key (str): Clave en formato "section.key"
            value: Valor a establecer
        """
        parts = key.split('.')
        config = self.config
        
        for part in parts[:-1]:
            if part not in config:
                config[part] = {}
            config = config[part]
        
        config[parts[-1]] = value
        self.save()
    
    def get_section(self, section):
        """
        Obtiene sección completa de configuración.
        Args:
            section (str): Nombre de la sección
        Returns:
            dict: Configuración de la sección
        """
        return self.config.get(section, {}).copy()
    
    def set_section(self, section, values):
        """
        Establece sección completa de configuración.
        Args:
            section (str): Nombre de la sección
            values (dict): Valores de la sección
        """
        if not isinstance(values, dict):
            print(f"[WARN] set_section: valores deben ser dict, recibido {type(values)}")
            return
        
        self.config[section] = values
        self.save()

# Configuración de la aplicación
APP_TITLE = "Sistema de Inscripciones TAP"
SCHOOL_NAME = "Escuela Superior de Música Nº6003"

# Google Sheets / Service Account
GOOGLE_SERVICE_ACCOUNT_FILE = "config/google_service_account.json"
GOOGLE_SHEET_ID = "1LYzWjGeJeEzBylSU1eI7Sn4gsmT-FPNTflYIsJWfGEc"

# Instancia global
settings = Settings()