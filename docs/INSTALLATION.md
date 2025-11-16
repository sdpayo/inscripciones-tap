# Guía de Instalación

## Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/sdpayo/inscripciones-tap.git
cd inscripciones-tap
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv

# En Linux/Mac:
source venv/bin/activate

# En Windows:
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copiar el archivo `.env.example` a `.env` y configurar las credenciales:

```bash
cp .env.example .env
```

Editar `.env` con tus credenciales:

- **Email**: Configurar SMTP (Gmail u otro proveedor)
- **Google Sheets**: Agregar credenciales de servicio

### 5. Ejecutar la aplicación

```bash
python src/main.py
```

## Configuración de Email (Gmail)

1. Ve a tu cuenta de Google
2. Activa la verificación en dos pasos
3. Genera una contraseña de aplicación: https://myaccount.google.com/apppasswords
4. Usa esa contraseña en `EMAIL_PASSWORD` en el archivo `.env`

## Configuración de Google Sheets

1. Ve a Google Cloud Console: https://console.cloud.google.com/
2. Crea un nuevo proyecto
3. Habilita la API de Google Sheets
4. Crea una cuenta de servicio
5. Descarga el archivo de credenciales JSON
6. Guarda el archivo como `credentials.json` en la raíz del proyecto
7. Comparte tu hoja de cálculo con el email de la cuenta de servicio

## Estructura de Directorios

Después de la instalación, la estructura será:

```
inscripciones-tap/
├── src/                 # Código fuente
├── data/                # Base de datos SQLite
├── exports/             # Archivos exportados (PDF/Excel)
├── templates/           # Plantillas
├── docs/                # Documentación
├── .env                 # Variables de entorno (crear)
├── credentials.json     # Credenciales Google (opcional)
└── requirements.txt     # Dependencias
```

## Solución de Problemas

### Error: tkinter no encontrado

En Linux, instalar tkinter:

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter
```

### Error: ModuleNotFoundError

Asegúrate de que el entorno virtual esté activado y las dependencias instaladas:

```bash
pip install -r requirements.txt
```

### Error de permisos en Google Sheets

Verifica que hayas compartido la hoja con el email de la cuenta de servicio.
