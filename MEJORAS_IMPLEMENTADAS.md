# Mejoras Implementadas

Este documento describe las 3 mejoras implementadas en el sistema de inscripciones TAP.

## 1. Monto en Certificados PDF

### Descripción
Se agregó la visualización del pago voluntario y el monto en los certificados PDF generados.

### Ubicación
- **Archivo**: `services/pdf_generator.py`
- **Línea**: Después de la línea 206 (sección de obra social)

### Características
- ✅ Muestra "✓ Pago voluntario" cuando el campo `pago_voluntario` está marcado como "Sí"
- ✅ Formatea el monto con formato de moneda: `$1,000.00`
- ✅ Maneja tanto valores numéricos como texto
- ✅ Maneja errores de formato gracefully (muestra el valor original si no puede formatear)

### Ejemplo de uso
```python
registro = {
    "nombre": "Juan Pérez",
    "pago_voluntario": "Sí",
    "monto": "1500.50"  # Se mostrará como $1,500.50
}
```

### Campos utilizados
- `registro.get("pago_voluntario")` - "Sí" o "No"
- `registro.get("monto")` - Puede ser número o texto

---

## 2. Filtros Optimizados en Listados

### Descripción
Se simplificaron los filtros de búsqueda para mostrar solo materias y profesores que tienen inscripciones activas.

### Ubicación
- **Archivo**: `ui/listados_tab.py`
- **Métodos modificados**: 
  - `_build_filtros()`
  - `_on_filtro_materia_change()`
  - `_aplicar_filtros()`
  - `_limpiar_filtros()`

### Cambios realizados

#### Filtros removidos
- ❌ Filtro de **Turno** (removido de UI de filtros)
- ❌ Filtro de **Año** (removido de UI de filtros)

#### Filtros optimizados
- ✅ **Materia**: Muestra solo materias con inscripciones
- ✅ **Profesor**: Muestra solo profesores con inscripciones
- ✅ Los profesores se filtran dinámicamente según la materia seleccionada

#### Columnas mantenidas
- ✅ Turno sigue apareciendo en la tabla de resultados
- ✅ Año sigue apareciendo en la tabla de resultados
- ✅ Ambas columnas se incluyen en las exportaciones

### Comportamiento
1. Al abrir la pestaña, los combos de Materia y Profesor se llenan con datos de inscripciones reales
2. Al seleccionar una materia, el combo de Profesor se actualiza automáticamente
3. Al aplicar filtros, se filtran solo por Materia y Profesor
4. Al limpiar filtros, se restauran todas las opciones disponibles

---

## 3. Sincronización con Google Sheets

### Descripción
Se implementó sincronización automática y no-bloqueante con Google Sheets para respaldar las inscripciones.

### Nuevos archivos
- **`services/google_sheets.py`** - Servicio de sincronización

### Funciones implementadas

#### `get_google_sheets_service()`
- Obtiene el servicio de Google Sheets API
- Usa credenciales de Service Account
- Busca el archivo `service_account.json` en múltiples ubicaciones
- Retorna `(service, error_message)`

#### `sync_to_google_sheets(registro, operation)`
- Sincroniza un registro individual
- **Operaciones soportadas**:
  - `'insert'` - Insertar o actualizar registro
  - `'delete'` - Eliminar registro
- **No-bloqueante**: No falla si Google Sheets no está configurado

#### `sync_in_background(registro, operation)`
- Ejecuta la sincronización en un hilo separado
- Totalmente no-bloqueante
- No afecta el flujo principal de la aplicación

### Integración en form_tab.py

#### En `_guardar()`
```python
# Después de guardar el registro
guardar_registro(registro)

# Sync en background (no-bloqueante)
sync_in_background(registro, operation='insert')
```

#### En `_eliminar_seleccionados()`
```python
# Después de eliminar registros
for registro in registros_a_eliminar:
    sync_in_background(registro, operation='delete')
```

### Configuración

#### Archivo de configuración: `data/config.json`
```json
{
  "google_sheets": {
    "enabled": true,
    "sheet_id": "TU_SHEET_ID_AQUI",
    "range": "Sheet1",
    "credentials_file": "service_account.json"
  }
}
```

#### Credenciales de Service Account
1. Crear un proyecto en Google Cloud Console
2. Habilitar Google Sheets API
3. Crear una Service Account
4. Descargar el archivo JSON de credenciales
5. Guardarlo como `service_account.json` en:
   - `/data/service_account.json`, o
   - `/data/config/service_account.json`, o
   - En la raíz del proyecto

#### Compartir la hoja
- Compartir la hoja de Google Sheets con el email de la Service Account
- Dar permisos de **Editor**

### Características de seguridad
- ✅ **Opcional**: Si no está configurado, no afecta el funcionamiento
- ✅ **No-bloqueante**: Se ejecuta en background, no ralentiza la UI
- ✅ **Error handling**: Maneja errores sin interrumpir la operación principal
- ✅ **Secure**: Usa Service Account (no requiere OAuth del usuario)

### Instalación de dependencias
```bash
pip install google-api-python-client google-auth
```

---

## Testing

Se crearon dos archivos de test:

### `test_mejoras.py`
- Prueba funcional de las tres mejoras
- Verifica que los componentes se importan correctamente
- Prueba con datos de ejemplo

### `test_requirements_validation.py`
- Valida que todos los requisitos se cumplieron
- Verifica la presencia de funciones y lógica implementada
- Genera un reporte de validación completo

### Ejecutar tests
```bash
python test_mejoras.py
python test_requirements_validation.py
```

---

## Resumen de archivos modificados

### Archivos nuevos
1. `services/google_sheets.py` - Servicio de sincronización con Google Sheets
2. `test_mejoras.py` - Tests funcionales
3. `test_requirements_validation.py` - Validación de requisitos

### Archivos modificados
1. `services/pdf_generator.py` - Agregado monto y pago voluntario
2. `ui/listados_tab.py` - Optimización de filtros
3. `ui/form_tab.py` - Integración de sincronización Google Sheets

---

## Notas importantes

1. **PDF**: El formato de monto es flexible y maneja errores
2. **Filtros**: La tabla siempre muestra Turno y Año, solo se removieron de los filtros
3. **Google Sheets**: Es completamente opcional y no afecta el funcionamiento si no está configurado
4. **Performance**: Los filtros cargan datos una sola vez al iniciar, luego usan cache
5. **Threading**: La sincronización usa threads daemon, no bloquea el cierre de la aplicación

---

## Compatibilidad

- ✅ Compatible con Python 3.7+
- ✅ No requiere cambios en la estructura de datos existente
- ✅ Backward compatible con versiones anteriores
- ✅ Funciona sin Google Sheets configurado
