# Sistema de Inscripciones TAP

Sistema modular de gestión de inscripciones para el **Trayecto Artístico Profesionalizando** de la **Escuela Superior de Música N°6003**.

## 🎵 Características

### ✅ Gestión de Estudiantes
- **Registro completo**: Información personal, académica y de contacto
- **Búsqueda y filtrado**: Por nombre, DNI, email y estado
- **Estados**: Pendiente, Aprobado, Rechazado
- **Base de datos SQLite**: Almacenamiento local y confiable

### 📄 Exportación
- **PDF**: 
  - Lista completa de estudiantes
  - Certificados de inscripción individuales
  - Fichas detalladas de estudiantes
- **Excel**: 
  - Exportación completa con todos los datos
  - Estadísticas por instrumento, nivel y ciudad
  - Formato profesional con columnas ajustables

### 📧 Envío de Emails
- **Email de bienvenida**: Confirmación automática de inscripción
- **Certificados por email**: Envío automático de certificados PDF
- **Notificaciones de estado**: Alertas sobre cambios de estado
- **Templates HTML**: Emails profesionales y personalizados

### ☁️ Sincronización con Google Sheets
- **Exportación a la nube**: Sincronización automática con Google Sheets
- **Importación**: Carga de datos desde Google Sheets
- **Colaboración**: Acceso compartido para múltiples usuarios
- **Backup automático**: Respaldo en la nube de todos los datos

### 🖥️ Interfaz Gráfica (Tkinter)
- **Intuitiva y fácil de usar**: Diseño moderno y funcional
- **Lista de estudiantes**: Vista completa con colores por estado
- **Formularios completos**: Validación de datos en tiempo real
- **Panel de acciones**: Acceso rápido a todas las funcionalidades

## 📋 Requisitos

- Python 3.8 o superior
- Sistema operativo: Windows, Linux o macOS
- Conexión a internet (solo para funciones de email y Google Sheets)

## 🚀 Instalación Rápida

```bash
# Clonar el repositorio
git clone https://github.com/sdpayo/inscripciones-tap.git
cd inscripciones-tap

# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Ejecutar la aplicación
python src/main.py
```

## 📚 Documentación

- [Guía de Instalación Detallada](docs/INSTALLATION.md)
- [Guía de Usuario](docs/USER_GUIDE.md)

## 🏗️ Arquitectura del Sistema

```
inscripciones-tap/
├── src/
│   ├── config/          # Configuración de la aplicación
│   ├── models/          # Modelos de datos y base de datos
│   ├── ui/              # Interfaz de usuario (Tkinter)
│   ├── export/          # Exportadores PDF y Excel
│   ├── email/           # Sistema de envío de emails
│   ├── sync/            # Sincronización con Google Sheets
│   ├── utils/           # Utilidades y validadores
│   └── main.py          # Punto de entrada
├── data/                # Base de datos SQLite
├── exports/             # Archivos exportados
├── docs/                # Documentación
├── requirements.txt     # Dependencias Python
├── .env.example         # Ejemplo de configuración
└── README.md
```

## 🔧 Configuración

### Email (Gmail)

1. Habilitar verificación en dos pasos en tu cuenta de Google
2. Crear contraseña de aplicación: https://myaccount.google.com/apppasswords
3. Configurar en `.env`:
   ```env
   EMAIL_ADDRESS=tu-email@gmail.com
   EMAIL_PASSWORD=tu-contraseña-de-app
   ```

### Google Sheets

1. Crear proyecto en Google Cloud Console
2. Habilitar Google Sheets API
3. Crear cuenta de servicio y descargar credenciales
4. Guardar credenciales como `credentials.json`
5. Compartir tu hoja de cálculo con el email de la cuenta de servicio
6. Configurar en `.env`:
   ```env
   GOOGLE_SHEET_ID=id-de-tu-hoja
   ```

## 🎯 Uso

### Iniciar la aplicación

```bash
python src/main.py
```

### Funciones principales

1. **Registrar estudiante**: Menú Estudiantes > Nuevo Estudiante
2. **Exportar lista**: Menú Archivo > Exportar a PDF/Excel
3. **Enviar email**: Menú Email > seleccionar tipo de email
4. **Sincronizar**: Menú Sincronización > Sincronizar con Google Sheets

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork del repositorio
2. Crear una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear un Pull Request

## 📝 Licencia

Este proyecto está bajo una licencia de uso educativo para la Escuela Superior de Música N°6003.

## 👥 Autores

- Desarrollado para el Trayecto Artístico Profesionalizando
- Escuela Superior de Música N°6003, Salta, Argentina

## 📞 Soporte

Para soporte técnico o consultas, contactar a través del repositorio de GitHub.

---

**Sistema de Inscripciones TAP** - Facilitando la gestión de inscripciones musicales 🎼
