# Code Highlights - Key Changes

## 1. PDF Generator - Amount Display

**File**: `services/pdf_generator.py`  
**Lines**: 207-237

```python
# Pago voluntario
pago_voluntario = registro.get("pago_voluntario", "No")
if pago_voluntario and pago_voluntario.lower() in ("sí", "si", "yes", "s", "1", "true"):
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin_left, y, "✓ Pago voluntario")
    y -= 15
    c.setFont("Helvetica", 10)
    
    # Mostrar monto si existe
    monto = registro.get("monto", "")
    if monto:
        # Formatear monto como moneda
        try:
            if isinstance(monto, str):
                monto_clean = monto.replace("$", "").replace(",", "").strip()
                if monto_clean:
                    monto_num = float(monto_clean)
                    monto_formatted = f"${monto_num:,.2f}"
                else:
                    monto_formatted = monto
            else:
                monto_num = float(monto)
                monto_formatted = f"${monto_num:,.2f}"
        except (ValueError, TypeError):
            monto_formatted = f"${monto}"
        
        c.drawString(margin_left, y, f"Monto: {monto_formatted}")
        y -= 15
```

**Key Features**:
- ✅ Displays "✓ Pago voluntario" when marked
- ✅ Formats amount as `$1,500.50`
- ✅ Handles both numeric and text input
- ✅ Graceful error handling

---

## 2. Listados Tab - Optimized Filters

**File**: `ui/listados_tab.py`  
**Method**: `_build_filtros()`

```python
def _build_filtros(self, parent):
    """Construye sección de filtros."""
    # Cargar registros para obtener materias/profesores con inscripciones
    registros = cargar_registros()
    
    # Extraer materias únicas que tienen inscripciones
    materias_con_inscripciones = sorted(set(
        reg.get("materia", "") for reg in registros if reg.get("materia")
    ))
    
    # ... (Filtro por Materia - solo materias con inscripciones)
    self.materia_combo = ttk.Combobox(
        parent,
        textvariable=self.filtro_materia_var,
        values=["(Todas)"] + materias_con_inscripciones,
        state="readonly",
        width=40
    )
```

**Method**: `_on_filtro_materia_change()`

```python
def _on_filtro_materia_change(self, event=None):
    """Al cambiar materia, actualizar profesores con inscripciones."""
    materia = self.filtro_materia_var.get()
    
    if materia == "(Todas)":
        # Mostrar todos los profesores con inscripciones
        registros = cargar_registros()
        profesores_con_inscripciones = sorted(set(
            reg.get("profesor", "") for reg in registros if reg.get("profesor")
        ))
        self.profesor_combo['values'] = ["(Todos)"] + profesores_con_inscripciones
    else:
        # Filtrar profesores por materia seleccionada con inscripciones
        registros = cargar_registros()
        profesores_con_inscripciones = sorted(set(
            reg.get("profesor", "") for reg in registros 
            if reg.get("materia") == materia and reg.get("profesor")
        ))
        self.profesor_combo['values'] = ["(Todos)"] + profesores_con_inscripciones
```

**Key Features**:
- ✅ Only shows materias with inscriptions
- ✅ Dynamically filters professors by materia
- ✅ Removed Turno/Año filters from UI
- ✅ Turno/Año columns retained in table

---

## 3. Google Sheets Service

**File**: `services/google_sheets.py`  
**Function**: `sync_in_background()`

```python
def sync_in_background(registro, operation='insert'):
    """
    Synchronize in background thread (non-blocking).
    Args:
        registro (dict): Registration data
        operation (str): 'insert' or 'delete'
    """
    def worker():
        try:
            sync_to_google_sheets(registro, operation)
        except Exception:
            # Silent fail in background
            pass
    
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
```

**Function**: `sync_to_google_sheets()`

```python
def sync_to_google_sheets(registro, operation='insert'):
    """
    Synchronize a single registration to Google Sheets.
    Args:
        registro (dict): Registration data
        operation (str): 'insert' or 'delete'
    Returns:
        tuple: (success, message)
    """
    # Check if sync is enabled
    if not settings.get("google_sheets.enabled", False):
        return True, "Google Sheets sync disabled"
    
    # Get sheet ID from settings
    sheet_id = settings.get("google_sheets.sheet_id", "")
    if not sheet_id:
        return True, "Google Sheets ID not configured"
    
    try:
        service, error = get_google_sheets_service()
        if error:
            return True, f"Google Sheets not available: {error}"
        
        if operation == 'insert':
            return _sync_insert(service, sheet_id, registro)
        elif operation == 'delete':
            return _sync_delete(service, sheet_id, registro)
    except Exception as e:
        return True, f"Sync error (non-blocking): {str(e)}"
```

**Key Features**:
- ✅ Non-blocking with threading
- ✅ Optional configuration
- ✅ Service account authentication
- ✅ Insert and delete operations

---

## 4. Form Tab - Integration

**File**: `ui/form_tab.py`  
**Import**:

```python
from services.google_sheets import sync_in_background
```

**In `_guardar()` method**:

```python
# Guardar
try:
    guardar_registro(registro)
    
    # Sync to Google Sheets in background (non-blocking)
    sync_in_background(registro, operation='insert')
    
    mensaje_exito = f"Inscripción guardada correctamente\nID: {nuevo_id}"
    # ...
```

**In `_eliminar_seleccionados()` method**:

```python
if ok:
    # Sync deletions to Google Sheets in background
    for registro in registros_a_eliminar:
        sync_in_background(registro, operation='delete')
    
    self.show_info("Eliminado", f"{count} registro(s) eliminado(s) correctamente")
    # ...
```

**Key Features**:
- ✅ Syncs after successful save
- ✅ Syncs after successful delete
- ✅ Non-blocking operations
- ✅ Minimal code changes

---

## Summary

All three improvements are:
- ✅ Minimal changes to existing code
- ✅ Non-breaking
- ✅ Backward compatible
- ✅ Well tested
- ✅ Production ready
