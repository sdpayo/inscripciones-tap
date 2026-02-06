# 🎵 Sistema de Inscripciones TAP

Sistema de inscripciones para el Trayecto Artístico Profesionalizante - Escuela Superior de Música N°6003

## ✨ Características

- 📝 **Formulario de inscripción** completo con validación de datos
- 📊 **Sincronización con Google Sheets** (incremental e inteligente)
- 📄 **Generación automática de certificados PDF**
- 📧 **Envío de certificados por email**
- 🔄 **Sistema de respaldo automático local**
- 📈 **Gestión de cupos** por materia/profesor/comisión
- 🔍 **Búsqueda y filtrado** de inscripciones
- 📋 **Generación de listados** por materia/profesor
- 🎨 **Interfaz moderna** con tema oscuro de alto contraste

## 🚀 Instalación

### 1. Requisitos previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### 2. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/inscripciones-tap.git
cd inscripciones-tap
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar el sistema

#### a) Configuración general

Copia el archivo de ejemplo y edítalo:

```bash
cp data/config.json.example data/config.json
```

Edita `data/config.json` con tus datos:
- `spreadsheet_id`: ID de tu Google Spreadsheet
- `smtp.username` y `smtp.password`: Credenciales de email

#### b) Credenciales de Google Sheets

1. Crea un proyecto en [Google Cloud Console](https://console.cloud.google.com/)
2. Habilita la API de Google Sheets
3. Crea una cuenta de servicio y descarga el JSON
4. Renombra el archivo a `credentials.json` en la raíz del proyecto

```bash
cp credentials.json.example credentials.json
# Luego edita con tus credenciales reales
```

#### c) Configuración de Email (opcional)

Si deseas enviar certificados por email:

```bash
cp smtp_config.json.example smtp_config.json
# Edita con tus credenciales de Gmail
```

**Nota**: Para Gmail, necesitas generar una [contraseña de aplicación](https://support.google.com/accounts/answer/185833).

### 5. Ejecutar la aplicación

```bash
python main.py
```

## 📁 Estructura del proyecto

```
inscripciones-tap/
├── config/              # Configuración global
├── data/                # Datos y archivos generados
│   ├── certificates/    # Certificados PDF generados
│   ├── logs/           # Logs de la aplicación
│   └── reports/        # Reportes generados
├── database/           # Manejo de datos (CSV, Google Sheets)
├── models/             # Modelos de datos (materias, etc.)
├── services/           # Servicios (email, PDF, Google Sheets)
├── ui/                 # Interfaz gráfica (Tkinter)
├── utils/              # Utilidades generales
└── main.py            # Punto de entrada
```

## 🔧 Configuración avanzada

### Sincronización con Google Sheets

El sistema soporta dos modos de sincronización:

1. **Incremental** (recomendado): Solo sincroniza cambios recientes (últimas 24h)
2. **Completa**: Sincroniza todos los registros

Configura en `data/config.json`:

```json
{
  "google_sheets": {
    "sync_mode": "incremental",
    "sync_window_hours": 24,
    "has_header_row": false
  }
}
```

### Respaldo automático

- Cada vez que sincroniza desde Google Sheets, se crea un respaldo local en `data/inscripciones_sheets.csv`
- Si Google Sheets no está disponible, el sistema carga automáticamente el último respaldo

## 🎯 Uso

### Interfaz principal

1. **Pestaña Formulario**: Registrar nuevos estudiantes
2. **Pestaña Listados**: Ver y filtrar inscripciones
3. **Pestaña Historial**: Buscar por DNI/Legajo
4. **Pestaña Configuración**: Ajustes del sistema

### Sincronización

- **Automática**: Al iniciar la aplicación
- **Manual**: Click en botón "🔄 Sincronizar"
  - Elige modo incremental o completo según necesites

### Generación de certificados

1. Selecciona un registro en la tabla
2. Click en "📄 Certificado"
3. El PDF se guarda en `data/certificates/`
4. Opcionalmente, envíalo por email con "📧 Enviar certificado"

## 🛡️ Seguridad

**IMPORTANTE**: Los siguientes archivos contienen información sensible y están excluidos del repositorio:

- `credentials.json` - Credenciales de Google
- `data/config.json` - Configuración con datos sensibles
- `smtp_config.json` - Credenciales de email
- `data/inscripciones*.csv` - Datos de estudiantes
- `data/certificates/` - Certificados generados

Nunca subas estos archivos al repositorio.

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es de uso interno para la Escuela Superior de Música N°6003.

## 📧 Contacto

Escuela Superior de Música N°6003 - inscripcionesesm@gmail.com

---

Desarrollado con ❤️ para la comunidad educativa

