"""Aplicación principal con interfaz gráfica."""
import tkinter as tk
from tkinter import ttk
from config.settings import settings
from ui.theme import aplicar_tema_alto_contraste

class InscripcionApp:
    """Aplicación principal de inscripciones."""
    
    def __init__(self, root):
        """Inicializa la aplicación."""
        self.root = root
        self.root.title("Sistema de Inscripciones - ESM N°6003")
        #self.root.geometry("1400x800")
        self.root.minsize(900, 600)

        # Configurar estilo
        self._setup_style()
        
        # Crear estructura principal
        self._create_layout()
        
        # Crear pestañas
        self._create_tabs()
        # Ejecutar la sincronización inicial desde Google Sheets
        try:
            self._startup_sync_from_sheets(show_popup=True)
        except Exception:
            pass
        
    def _setup_style(self):
        """Configura estilos de la aplicación."""
        # Aplicar tema con alto contraste
        self.style = aplicar_tema_alto_contraste(self.root)
    
    def _create_layout(self):
        """Crea el layout principal."""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            header_frame,
            text="Sistema de Inscripciones TAP",
            font=("Helvetica", 16, "bold")
        ).pack(side=tk.LEFT)
        
        ttk.Label(
            header_frame,
            text="Escuela Superior de Música N°6003",
            font=("Helvetica", 10)
        ).pack(side=tk.LEFT, padx=20)
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Footer
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(
            footer_frame,
            text="Listo",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _startup_sync_from_sheets(self, show_popup: bool = True):
        """
        Al iniciar la app: descarga la planilla y sincroniza el CSV local.
        Si hay cambios, actualiza la UI (refresh) y muestra un resumen (added/updated/removed).
        Si falla, intenta cargar respaldo local.
        """
        try:
            # comprobar si está habilitado en settings
            enabled = settings.get("google_sheets.enabled", True)
            if not enabled:
                print("[STARTUP SYNC] google_sheets disabled in settings; skipping startup sync")
                return

            sheet_key = settings.get("google_sheets.sheet_key", "") or settings.get("spreadsheet_id", "")
            if not sheet_key:
                print("[STARTUP SYNC] No sheet_key configured; skipping startup sync")
                return

            print("[STARTUP SYNC] Iniciando sincronización remota -> local desde planilla...")
            from services.google_sheets import sync_remote_to_local, load_local_backup
            ok, result = sync_remote_to_local(sheet_key)
            
            if not ok:
                print("[STARTUP SYNC] Falló la sincronización inicial:", result)
                
                # INTENTAR CARGAR RESPALDO LOCAL
                print("[STARTUP SYNC] Intentando cargar respaldo local...")
                ok_backup, backup_result = load_local_backup()
                if ok_backup:
                    registros_backup = backup_result
                    from database.csv_handler import guardar_todos_registros
                    ok_save, msg_save = guardar_todos_registros(registros_backup)
                    if ok_save:
                        print(f"[STARTUP SYNC] ✓ Respaldo local cargado exitosamente ({len(registros_backup)} registros)")
                        if show_popup:
                            try:
                                self.show_warning(
                                    "Sincronización con Sheets falló",
                                    f"No se pudo conectar con Google Sheets.\n\n" +
                                    f"Se cargó el último respaldo local:\n" +
                                    f"• {len(registros_backup)} registros\n\n" +
                                    f"Error original: {result}"
                                )
                            except Exception:
                                pass
                        # Refresh UI con datos del respaldo
                        try:
                            if hasattr(self, "form_tab") and self.form_tab:
                                self.form_tab.refresh()
                            self.refresh_all()
                        except Exception:
                            pass
                        return
                else:
                    print(f"[STARTUP SYNC] No se pudo cargar respaldo local: {backup_result}")
                
                if show_popup:
                    try:
                        self.show_warning("Sincronización inicial", f"No se pudo sincronizar desde Google Sheets: {result}")
                    except Exception:
                        pass
                return

            stats = result or {}
            added = stats.get("added", 0)
            updated = stats.get("updated", 0)
            removed = stats.get("removed", 0)
            skipped = stats.get("skipped", 0)
            total_after = stats.get("local_total_after", 0)

            # refresh UI (tabs that show registros)
            try:
                # refresh main form tab and other tabs if needed
                if hasattr(self, "form_tab") and self.form_tab:
                    try:
                        print("[STARTUP SYNC] Refrescando form_tab...")
                        self.form_tab.refresh()
                        print("[STARTUP SYNC] form_tab refrescado exitosamente")
                    except Exception as e_form:
                        print(f"[STARTUP SYNC] Error refrescando form_tab: {e_form}")
                        import traceback
                        traceback.print_exc()
                try:
                    print("[STARTUP SYNC] Refrescando todas las tabs...")
                    self.refresh_all()
                    print("[STARTUP SYNC] Todas las tabs refrescadas exitosamente")
                except Exception as e_all:
                    print(f"[STARTUP SYNC] Error refrescando tabs: {e_all}")
                    import traceback
                    traceback.print_exc()
            except Exception as e_outer:
                print(f"[STARTUP SYNC] Error general en refresh: {e_outer}")
                import traceback
                traceback.print_exc()

            msg = f"Sincronización inicial completada.\nAñadidos: {added}\nActualizados: {updated}\nEliminados: {removed}\nIgnorados: {skipped}\nTotal local: {total_after}"
            print("[STARTUP SYNC] " + msg.replace("\n", " | "))
            if show_popup:
                try:
                    # usar show_info o un messagebox para alertar al usuario
                    self.show_info("Sincronización inicial", msg)
                except Exception:
                    import tkinter.messagebox as mb
                    try:
                        mb.showinfo("Sincronización inicial", msg)
                    except Exception:
                        print("[STARTUP SYNC] No se pudo mostrar popup, se imprimió en consola.")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print("[STARTUP SYNC] Error inesperado:", e)

    def _create_tabs(self):
        """Crea todas las pestañas."""
        from ui.form_tab import FormTab
        from ui.listados_tab import ListadosTab
        from ui.historial_tab import HistorialTab
        from ui.config_tab import ConfigTab
        
        # Formulario (principal)
        self.form_tab = FormTab(self.notebook, self)
        self.notebook.add(self.form_tab.frame, text="📝 Formulario")
        
        # Listados
        self.listados_tab = ListadosTab(self.notebook, self)
        self.notebook.add(self.listados_tab.frame, text="📊 Listados")
        
        # Historial
        self.historial_tab = HistorialTab(self.notebook, self)
        self.notebook.add(self.historial_tab.frame, text="🔍 Historial")
        
        # Configuración
        self.config_tab = ConfigTab(self.notebook, self)
        self.notebook.add(self.config_tab.frame, text="⚙️ Configuración")

    def refresh_all(self):
        """Refresca todas las pestañas."""
        print("[APP] Refrescando todas las pestañas...")
        for tab_name, tab in [("form_tab", self.form_tab), ("listados_tab", self.listados_tab), 
                              ("historial_tab", self.historial_tab), ("config_tab", self.config_tab)]:
            try:
                if hasattr(tab, 'refresh'):
                    print(f"[APP] Refrescando {tab_name}...")
                    tab.refresh()
                    print(f"[APP] {tab_name} refrescado exitosamente")
                else:
                    print(f"[APP] {tab_name} no tiene método refresh, saltando")
            except Exception as e:
                print(f"[WARN] No se pudo refrescar {tab_name}: {e}")
                import traceback
                traceback.print_exc()
        print("[APP] Refresh de todas las pestañas completado")

    def update_status(self, mensaje):
        """Actualiza mensaje de estado."""
        self.status_label.config(text=mensaje)
    
    def run(self):
        """Inicia el loop principal."""
        self.root.mainloop()