# Guía de Usuario - Sistema de Inscripciones TAP

## Introducción

El Sistema de Inscripciones TAP es una aplicación de escritorio diseñada para gestionar inscripciones de estudiantes del Trayecto Artístico Profesionalizando de la Escuela Superior de Música N°6003.

## Funcionalidades Principales

### 1. Gestión de Estudiantes

#### Crear Nuevo Estudiante

1. Hacer clic en **"Nuevo Estudiante"** en el panel derecho o en el menú **Estudiantes > Nuevo Estudiante**
2. Completar el formulario con la información del estudiante:
   - **Información Personal**: Nombre, apellido, DNI, fecha de nacimiento, email, teléfono
   - **Dirección**: Dirección completa, ciudad, provincia, código postal
   - **Contacto de Emergencia**: Datos de una persona de contacto
   - **Información Académica**: Instrumento, nivel, experiencia previa
   - **Estado**: Pendiente, Aprobado o Rechazado
   - **Notas**: Observaciones adicionales
3. Hacer clic en **"Guardar"**

**Nota**: Los campos marcados con asterisco (*) son obligatorios.

#### Editar Estudiante

1. Seleccionar un estudiante de la lista
2. Hacer clic en **"Editar Estudiante"**
3. Modificar los campos deseados
4. Hacer clic en **"Guardar"**

#### Eliminar Estudiante

1. Seleccionar un estudiante de la lista
2. Hacer clic en **"Eliminar Estudiante"**
3. Confirmar la eliminación

**Advertencia**: Esta acción no se puede deshacer.

### 2. Búsqueda y Filtrado

#### Buscar Estudiantes

Utilizar la barra de búsqueda para encontrar estudiantes por:
- Nombre
- Apellido
- DNI
- Email

La búsqueda es en tiempo real.

#### Filtrar por Estado

Usar el desplegable **"Estado"** para filtrar estudiantes por:
- Todos
- Pendiente
- Aprobado
- Rechazado

### 3. Ver Detalles

1. Seleccionar un estudiante de la lista
2. Hacer clic en **"Ver Detalles"**
3. Se abrirá una ventana con toda la información del estudiante

### 4. Exportación

#### Exportar Lista a PDF

1. Ir a **Archivo > Exportar a PDF** o hacer clic en **"Exportar Lista (PDF)"**
2. Se generará un PDF con la lista completa de estudiantes
3. El archivo se guardará en la carpeta `exports/`

El PDF incluye:
- Encabezado con el nombre de la institución
- Tabla con datos principales de cada estudiante
- Total de inscriptos

#### Exportar Lista a Excel

1. Ir a **Archivo > Exportar a Excel** o hacer clic en **"Exportar Lista (Excel)"**
2. Se generará un archivo Excel con todos los datos
3. El archivo se guardará en la carpeta `exports/`

El Excel incluye columnas ajustables con toda la información de los estudiantes.

### 5. Certificados

#### Generar Certificado

1. Seleccionar un estudiante
2. Hacer clic en **"Generar Certificado"**
3. Se creará un PDF con el certificado de inscripción
4. El archivo se guardará en la carpeta `exports/`

El certificado incluye:
- Nombre completo del estudiante
- DNI
- Programa de inscripción
- Instrumento y nivel
- Fecha de inscripción

### 6. Envío de Emails

**Nota**: Requiere configuración previa de SMTP en el archivo `.env`

#### Enviar Email de Bienvenida

1. Seleccionar un estudiante
2. Ir a **Email > Enviar Bienvenida**
3. Se enviará un email automático al estudiante con:
   - Confirmación de inscripción
   - Datos registrados
   - Estado actual

#### Enviar Certificado por Email

1. Seleccionar un estudiante
2. Ir a **Email > Enviar Certificado**
3. Se generará el certificado y se enviará por email adjunto

#### Enviar Actualización de Estado

1. Seleccionar un estudiante
2. Cambiar el estado si es necesario (editar estudiante)
3. Ir a **Email > Enviar Actualización de Estado**
4. Se enviará un email notificando el cambio de estado

### 7. Sincronización con Google Sheets

**Nota**: Requiere configuración previa de Google Sheets (ver guía de instalación)

#### Sincronizar Datos a Google Sheets

1. Ir a **Sincronización > Sincronizar con Google Sheets**
2. Los datos se exportarán a la hoja de cálculo configurada
3. Se crearán o actualizarán los datos en la hoja

**Ventajas**:
- Acceso desde cualquier dispositivo
- Colaboración en tiempo real
- Backup automático

#### Importar desde Google Sheets

1. Ir a **Sincronización > Importar desde Google Sheets**
2. Confirmar la importación
3. Los datos se sincronizarán con la base de datos local
4. Los estudiantes existentes se actualizarán, los nuevos se agregarán

## Atajos de Teclado

La aplicación actualmente no tiene atajos de teclado, pero puedes usar:
- `Alt` + letra subrayada en los menús para acceso rápido

## Consejos y Mejores Prácticas

### Respaldo de Datos

- La base de datos se encuentra en `data/inscripciones.db`
- Hacer copias de seguridad periódicas de esta carpeta
- Usar Google Sheets como respaldo en la nube

### Gestión de Emails

- Verificar las credenciales de email antes de enviar masivos
- Usar la función de actualización de estado solo cuando sea necesario
- Personalizar los templates de email si es necesario (en el código)

### Exportación

- Los archivos exportados tienen timestamp para evitar sobrescrituras
- Revisar periódicamente la carpeta `exports/` para limpiar archivos antiguos

### Estados de Estudiantes

- **Pendiente**: Recién inscrito, esperando revisión
- **Aprobado**: Inscripción confirmada
- **Rechazado**: Inscripción no aprobada

Usar las notas para agregar detalles específicos del estado.

## Solución de Problemas Comunes

### No puedo enviar emails

- Verificar configuración en `.env`
- Para Gmail, usar contraseña de aplicación
- Verificar conexión a internet

### Error al sincronizar con Google Sheets

- Verificar que `credentials.json` existe
- Verificar que la hoja está compartida con la cuenta de servicio
- Verificar que el `GOOGLE_SHEET_ID` es correcto en `.env`

### La aplicación no inicia

- Verificar que Python 3.8+ está instalado
- Verificar que todas las dependencias están instaladas
- En Linux, verificar que tkinter está instalado

### Los datos no se guardan

- Verificar permisos de escritura en la carpeta `data/`
- Verificar que no hay otro proceso usando la base de datos

## Soporte

Para reportar problemas o solicitar nuevas funcionalidades, contactar con el equipo de desarrollo o crear un issue en el repositorio del proyecto.
