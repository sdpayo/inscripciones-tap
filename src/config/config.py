"""Configuration management for the application."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration."""
    
    # Application paths
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    DATABASE_PATH = DATA_DIR / "inscripciones.db"
    
    # Email configuration
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
    EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "Sistema de Inscripciones TAP")
    
    # Google Sheets configuration
    GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")
    
    # Application settings
    APP_NAME = "Sistema de Inscripciones TAP"
    APP_VERSION = "1.0.0"
    SCHOOL_NAME = "Escuela Superior de Música N°6003"
    PROGRAM_NAME = "Trayecto Artístico Profesionalizando"
    
    # Export settings
    PDF_TEMPLATE_DIR = BASE_DIR / "templates" / "pdf"
    EXPORT_DIR = BASE_DIR / "exports"
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist."""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.EXPORT_DIR.mkdir(exist_ok=True)
        if not cls.PDF_TEMPLATE_DIR.exists():
            cls.PDF_TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
