"""Pestaña de Configuración (SMTP, Google Sheets, etc.)."""
import tkinter as tk
from tkinter import ttk
from ui.base_tab import BaseTab
from config.settings import settings
from services.email_service import save_smtp_config, test_smtp_connection
from database.google_sheets import test_google_sheets_connection
import threading

class ConfigTab(BaseTab):
    """Pestaña de configuración de la aplicación."""
        
    def _build_ui(self):
        """Construye la interfaz de configuración."""
        # Notebook para secciones
        self.config_notebook = ttk.Notebook(self.frame)
        self.config_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Construir secciones
        self._build_app_config()
        self._build_smtp_config()
        self._build_gsheets_config()
        
    def _build_app_config(self):
        """Construye sección de configuración general de la aplicación."""
        # Crear frame
        app_frame = ttk.Frame(self.config_notebook, padding=10)
        self.config_notebook.add(app_frame, text="General")
        
        row = 0
        
        # === TÍTULO ===
        ttk.Label(
            app_frame,
            text="Configuración General",
            font=("Helvetica", 12, "bold")
        ).grid(row=row, column=0, columnspan=2, pady=10, sticky="w")
        row += 1
        
        # === CHECK CUPOS ===
        self.check_cupos_var = tk.BooleanVar()
        self.check_cupos_var.set(settings.get("app.check_cupos", True))
        
        ttk.Checkbutton(
            app_frame,
            text="Verificar cupos disponibles al inscribir",
            variable=self.check_cupos_var
        ).grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        row += 1
        
        # === REQUIRE SEGURO ===
        self.require_seguro_var = tk.BooleanVar()
        self.require_seguro_var.set(settings.get("app.require_seguro_escolar", True))
        
        ttk.Checkbutton(
            app_frame,
            text="Requerir información de seguro escolar",
            variable=self.require_seguro_var
        ).grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        row += 1
        
        # === AUTO BACKUP ===
        self.auto_backup_var = tk.BooleanVar()
        self.auto_backup_var.set(settings.get("app.auto_backup", True))
        
        ttk.Checkbutton(
            app_frame,
            text="Crear backups automáticos",
            variable=self.auto_backup_var
        ).grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        row += 1
        
        # === BACKUP INTERVAL ===
        ttk.Label(app_frame, text="Días entre backups:").grid(
            row=row, column=0, sticky="e", padx=5, pady=5
        )
        self.backup_interval_var = tk.StringVar()
        self.backup_interval_var.set(str(settings.get("app.backup_interval_days", 7)))
        
        ttk.Spinbox(
            app_frame,
            from_=1,
            to=30,
            textvariable=self.backup_interval_var,
            width=10
        ).grid(row=row, column=1, sticky="w", padx=5, pady=5)
        row += 1
        
        # === SEPARADOR ===
        ttk.Separator(app_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky="ew", pady=15
        )
        row += 1
        
        # === TEMA ===
        ttk.Label(
            app_frame,
            text="Apariencia",
            font=("Helvetica", 12, "bold")
        ).grid(row=row, column=0, columnspan=2, pady=10, sticky="w")
        row += 1
        
        ttk.Label(app_frame, text="Tema:").grid(
            row=row, column=0, sticky="e", padx=5, pady=5
        )
        self.theme_var = tk.StringVar()
        self.theme_var.set(settings.get("ui.theme", "clam"))
        
        # Obtener temas disponibles
        style = ttk.Style()
        available_themes = style.theme_names()
        
        ttk.Combobox(
            app_frame,
            textvariable=self.theme_var,
            values=list(available_themes),
            state="readonly",
            width=20
        ).grid(row=row, column=1, sticky="w", padx=5, pady=5)
        row += 1
        
        # Botón para aplicar tema inmediatamente
        ttk.Button(
            app_frame,
            text="🎨 Aplicar Tema Ahora",
            command=self._apply_theme_now
        ).grid(row=row, column=1, sticky="w", padx=5, pady=5)
        row += 1
        
        ttk.Label(
            app_frame,
            text="(Guardá los cambios para hacerlo permanente)",
            font=("Helvetica", 8),
            foreground="gray"
        ).grid(row=row, column=1, sticky="w", padx=5)
        row += 1
        
        # === DEBUG MODE ===
        ttk.Label(app_frame, text="Modo Debug:").grid(
            row=row, column=0, sticky="e", padx=5, pady=5
        )
        self.debug_var = tk.BooleanVar()
        self.debug_var.set(settings.get("app.debug", False))
        ttk.Checkbutton(
            app_frame,
            text="Activar logs detallados",
            variable=self.debug_var
        ).grid(row=row, column=1, sticky="w", padx=5, pady=5)
        row += 1
        
        # === AUTO-REFRESH ===
        ttk.Label(app_frame, text="Auto-refresh:").grid(
            row=row, column=0, sticky="e", padx=5, pady=5
        )
        self.auto_refresh_var = tk.BooleanVar()
        self.auto_refresh_var.set(settings.get("app.auto_refresh", True))
        ttk.Checkbutton(
            app_frame,
            text="Refrescar tablas automáticamente",
            variable=self.auto_refresh_var
        ).grid(row=row, column=1, sticky="w", padx=5, pady=5)
        row += 1
        
        # === SEPARADOR ===
        ttk.Separator(app_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky="ew", pady=15
        )
        row += 1
        
        # === BOTONES ===
        buttons_frame = ttk.Frame(app_frame)
        buttons_frame.grid(row=row, column=0, columnspan=2, pady=10)
        
        ttk.Button(
            buttons_frame,
            text="💾 Guardar Configuración",
            command=self._save_app_config
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            buttons_frame,
            text="🔄 Restaurar Valores por Defecto",
            command=self._restore_defaults
        ).pack(side=tk.LEFT, padx=5)
        row += 1
        
        # === INFO ===
        info_text = (
            "Los cambios en la configuración general se aplican inmediatamente,\n"
            "excepto el tema que requiere reiniciar la aplicación."
        )
        ttk.Label(
            app_frame,
            text=info_text,
            font=("Helvetica", 9),
            foreground="gray",
            justify=tk.LEFT
        ).grid(row=row, column=0, columnspan=2, pady=10, sticky="w")

    def _save_app_config(self):
        """Guarda configuración general de la app."""
        try:
            # Guardar configuraciones básicas
            if hasattr(self, 'check_cupos_var'):
                settings.set("app.check_cupos", self.check_cupos_var.get())
            
            if hasattr(self, 'require_seguro_var'):
                settings.set("app.require_seguro_escolar", self.require_seguro_var.get())
            
            if hasattr(self, 'auto_backup_var'):
                settings.set("app.auto_backup", self.auto_backup_var.get())
            
            if hasattr(self, 'backup_interval_var'):
                try:
                    backup_days = int(self.backup_interval_var.get())
                    settings.set("app.backup_interval_days", backup_days)
                except ValueError:
                    pass
            
            # Guardar tema
            if hasattr(self, 'theme_var'):
                nuevo_tema = self.theme_var.get()
                settings.set("ui.theme", nuevo_tema)
                
                # Aplicar tema inmediatamente
                try:
                    style = ttk.Style()
                    style.theme_use(nuevo_tema)
                except Exception as e:
                    print(f"[WARN] No se pudo aplicar tema: {e}")
            
            # Guardar debug mode
            if hasattr(self, 'debug_var'):
                settings.set("app.debug", self.debug_var.get())
            
            # Guardar auto-refresh
            if hasattr(self, 'auto_refresh_var'):
                settings.set("app.auto_refresh", self.auto_refresh_var.get())
            
            self.show_info("Guardado", "Configuración de aplicación guardada")
            
        except Exception as e:
            self.show_error("Error", f"No se pudo guardar la configuración: {e}")

    def _restore_defaults(self):
        """Restaura valores por defecto."""
        if not self.ask_yes_no(
            "Restaurar Valores",
            "¿Estás seguro de restaurar la configuración por defecto?\nEsto no afectará tus datos."
        ):
            return
        
        # Restaurar valores
        self.check_cupos_var.set(True)
        self.require_seguro_var.set(True)
        self.auto_backup_var.set(True)
        self.backup_interval_var.set("7")
        self.theme_var.set("clam")
        if hasattr(self, 'debug_var'):
            self.debug_var.set(False)
        if hasattr(self, 'auto_refresh_var'):
            self.auto_refresh_var.set(True)
        
        self._save_app_config()

    def _apply_theme_now(self):
        """Aplica el tema seleccionado inmediatamente sin guardar."""
        nuevo_tema = self.theme_var.get()
        try:
            style = ttk.Style()
            style.theme_use(nuevo_tema)
            self.show_info("Tema aplicado", f"Tema '{nuevo_tema}' aplicado temporalmente.\nGuardá los cambios para hacerlo permanente.")
        except Exception as e:
            self.show_error("Error", f"No se pudo aplicar el tema: {e}")

    def _build_smtp_config(self):
        """Sección de configuración SMTP."""
        frame = ttk.Frame(self.config_notebook, padding=10)
        self.config_notebook.add(frame, text="Email (SMTP)")
        
        # Título
        ttk.Label(
            frame, 
            text="Configuración de Email (SMTP)",
            font=("Helvetica", 12, "bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        ttk.Label(
            frame,
            text="Usar App Password de Gmail (https://myaccount.google.com/apppasswords)",
            foreground="gray"
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        # Campos SMTP
        smtp_config = settings.get_section("smtp")
        
        row = 2
        
        # Host
        ttk.Label(frame, text="Servidor SMTP:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.smtp_host_var = tk.StringVar(value=smtp_config.get("host", "smtp.gmail.com"))
        ttk.Entry(frame, textvariable=self.smtp_host_var, width=30).grid(row=row, column=1, sticky="w", padx=5, pady=5)
        
        row += 1
        
        # Port
        ttk.Label(frame, text="Puerto:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.smtp_port_var = tk.IntVar(value=smtp_config.get("port", 587))
        ttk.Entry(frame, textvariable=self.smtp_port_var, width=10).grid(row=row, column=1, sticky="w", padx=5, pady=5)
        
        row += 1
        
        # Username
        ttk.Label(frame, text="Usuario (Email):").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.smtp_user_var = tk.StringVar(value=smtp_config.get("username", ""))
        ttk.Entry(frame, textvariable=self.smtp_user_var, width=40).grid(row=row, column=1, sticky="w", padx=5, pady=5)
        
        row += 1
        
        # Password
        ttk.Label(frame, text="App Password:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.smtp_pass_var = tk.StringVar(value=smtp_config.get("password", ""))
        pass_entry = ttk.Entry(frame, textvariable=self.smtp_pass_var, show="*", width=30)
        pass_entry.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        
        row += 1
        
        # From name
        ttk.Label(frame, text="Nombre remitente:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.smtp_from_name_var = tk.StringVar(value=smtp_config.get("from_name", "Escuela"))
        ttk.Entry(frame, textvariable=self.smtp_from_name_var, width=40).grid(row=row, column=1, sticky="w", padx=5, pady=5)
        
        row += 1
        
        # Botones
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ttk.Button(
            btn_frame,
            text="💾 Guardar configuración",
            command=self._save_smtp_config
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="🧪 Probar conexión",
            command=self._test_smtp
        ).pack(side=tk.LEFT, padx=5)
    
    def _build_gsheets_config(self):
        """Construye sección de Google Sheets."""
        # Crear frame
        google_frame = ttk.Frame(self.config_notebook, padding=10)
        self.config_notebook.add(google_frame, text="Google Sheets")
        
        row = 0
        
        # Sheet Key
        ttk.Label(google_frame, text="ID de la Hoja de Google:").grid(
            row=row, column=0, sticky="e", padx=5, pady=5
        )
        self.google_sheet_key_var = tk.StringVar()
        self.google_sheet_key_var.set(settings.get("google_sheets.sheet_key", ""))
        
        ttk.Entry(
            google_frame,
            textvariable=self.google_sheet_key_var,
            width=50
        ).grid(row=row, column=1, sticky="w", padx=5, pady=5)
        row += 1
        
        # Credentials file
        ttk.Label(google_frame, text="Archivo de Credenciales:").grid(
            row=row, column=0, sticky="e", padx=5, pady=5
        )
        self.google_creds_file_var = tk.StringVar()
        self.google_creds_file_var.set(settings.get("google_sheets.credentials_file", "credentials.json"))
        
        ttk.Entry(
            google_frame,
            textvariable=self.google_creds_file_var,
            width=50
        ).grid(row=row, column=1, sticky="w", padx=5, pady=5)
        row += 1
        
        # Info
        ttk.Label(
            google_frame,
            text="Descargá credentials.json desde Google Cloud Console\ny guardalo en la carpeta del proyecto.",
            foreground="gray",
            font=("Helvetica", 9)
        ).grid(row=row, column=0, columnspan=2, pady=5)
        row += 1
        
        # Separador
        ttk.Separator(google_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky="ew", pady=10
        )
        row += 1
        
        # Botón guardar
        ttk.Button(
            google_frame,
            text="💾 Guardar Configuración",
            command=self._save_google_sheets_config
        ).grid(row=row, column=0, columnspan=2, pady=5)
        row += 1
        
        # Botón probar
        ttk.Button(
            google_frame,
            text="🧪 Probar Conexión",
            command=self._test_google_sheets
        ).grid(row=row, column=0, columnspan=2, pady=5)
        row += 1
        
        # Botón descargar
        ttk.Button(
            google_frame,
            text="📥 Descargar desde Google Sheets",
            command=self._download_from_sheets
        ).grid(row=row, column=0, columnspan=2, pady=5)
        row += 1
        
        # Botón sincronizar
        ttk.Button(
            google_frame,
            text="🔄 Sincronizar (Bidireccional)",
            command=self._sincronizar_bidireccional
        ).grid(row=row, column=0, columnspan=2, pady=5)    
    # ========== Handlers SMTP ==========
    
    def _save_smtp_config(self):
        """Guarda configuración SMTP con validación."""
        host = self.smtp_host_var.get().strip()
        username = self.smtp_user_var.get().strip()
        
        # Validación básica
        if not host:
            self.show_error("SMTP", "El servidor SMTP es obligatorio.")
            return
        
        if not username:
            self.show_warning("SMTP", "Se recomienda configurar el usuario (email).")
        
        config = {
            "host": host,
            "port": self.smtp_port_var.get(),
            "username": username,
            "password": self.smtp_pass_var.get(),
            "use_tls": True,
            "from_name": self.smtp_from_name_var.get().strip() or "Escuela",
            "from_addr": ""
        }
        
        ok, msg = save_smtp_config(config)
        if ok:
            settings.update_section("smtp", config)
            self.show_info("✅ SMTP", "Configuración guardada correctamente.")
        else:
            self.show_error("❌ SMTP", msg)
    
    def _test_smtp(self):
        """Prueba conexión SMTP en background."""
        config = {
            "host": self.smtp_host_var.get().strip(),
            "port": self.smtp_port_var.get(),
            "username": self.smtp_user_var.get().strip(),
            "password": self.smtp_pass_var.get(),
            "use_tls": True
        }
        
        def worker():
            ok, msg = test_smtp_connection(config)
            def finish():
                if ok:
                    self.show_info("SMTP", f"✅ {msg}")
                else:
                    self.show_error("SMTP", f"❌ {msg}")
            
            try:
                self.frame.after(1, finish)
            except:
                finish()
        
        threading.Thread(target=worker, daemon=True).start()
        self.show_info("SMTP", "Probando conexión en segundo plano...")
    
    # ========== Handlers Google Sheets ==========
    
    def _save_gs_key(self):
        """Guarda Sheet ID."""
        sheet_key = self.gs_key_var.get().strip()
        settings.set("google_sheets.sheet_key", sheet_key)
        self.show_info("Google Sheets", "Sheet ID guardado.")
    
    def _toggle_auto_sync(self):
        """Activa/desactiva auto-sync."""
        enabled = self.auto_sync_var.get()
        interval = self.auto_sync_interval_var.get()
        
        settings.set("google_sheets.auto_sync_enabled", enabled)
        settings.set("google_sheets.auto_sync_interval_minutes", interval)
        
        if enabled:
            self.show_info("Auto-sync", f"Activado (cada {interval} minutos)")
        else:
            self.show_info("Auto-sync", "Desactivado")
    
    def _sync_from_gs(self):
        """Descarga desde Google Sheets."""
        from database.google_sheets import sync_from_google_sheets
        
        sheet_key = self.gs_key_var.get().strip()
        if not sheet_key:
            self.show_warning("Google Sheets", "Configurá el Sheet ID primero.")
            return
        
        def worker():
            ok, msg = sync_from_google_sheets(sheet_key)
            def finish():
                if ok:
                    self.show_info("Sincronización", msg)
                    try:
                        self.app.refresh_all()
                    except:
                        pass
                else:
                    self.show_error("Error", msg)
            
            try:
                self.frame.after(1, finish)
            except:
                finish()
        
        threading.Thread(target=worker, daemon=True).start()
        self.show_info("Google Sheets", "Descargando en segundo plano...")
    
    def _sync_to_gs(self):
        """Sube a Google Sheets."""
        from database.google_sheets import sync_to_google_sheets
        
        sheet_key = self.gs_key_var.get().strip()
        if not sheet_key:
            self.show_warning("Google Sheets", "Configurá el Sheet ID primero.")
            return
        
        if not self.ask_yes_no("Confirmar", "¿Sobrescribir datos en Google Sheets?"):
            return
        
        def worker():
            ok, msg = sync_to_google_sheets(sheet_key)
            def finish():
                if ok:
                    self.show_info("Subida", msg)
                else:
                    self.show_error("Error", msg)
            
            try:
                self.frame.after(1, finish)
            except:
                finish()
        
        threading.Thread(target=worker, daemon=True).start()
        self.show_info("Google Sheets", "Subiendo en segundo plano...")
    
    def _test_gs(self):
        """Prueba conexión Google Sheets."""
        sheet_key = self.gs_key_var.get().strip()
        if not sheet_key:
            self.show_warning("Google Sheets", "Configurá el Sheet ID primero.")
            return
        
        try:
            self.gs_status_label.config(text="Probando...", foreground="orange")
        except AttributeError:
            pass
        
        def worker():
            ok, msg = test_google_sheets_connection(sheet_key)
            def finish():
                try:
                    if ok:
                        self.gs_status_label.config(text="✅ Conectado", foreground="green")
                        self.show_info("Google Sheets", f"✅ {msg}")
                    else:
                        self.gs_status_label.config(text="❌ Error", foreground="red")
                        self.show_error("Google Sheets", f"❌ {msg}")
                except AttributeError:
                    if ok:
                        self.show_info("Google Sheets", f"✅ {msg}")
                    else:
                        self.show_error("Google Sheets", f"❌ {msg}")
            
            try:
                self.frame.after(1, finish)
            except:
                finish()
        
        threading.Thread(target=worker, daemon=True).start()
    
    # ========== Handlers App Config ==========
    
    def _save_theme(self):
        """Guarda tema seleccionado."""
        theme = self.theme_var.get()
        settings.set("ui.theme", theme)
        self.show_info("Tema", f"Tema '{theme}' guardado. Reiniciá la app para aplicar cambios.")

    def _save_google_sheets_config(self):
        """Guarda configuración de Google Sheets."""
        sheet_key = self.google_sheet_key_var.get().strip()
        creds_file = self.google_creds_file_var.get().strip()
        
        settings.set("google_sheets.sheet_key", sheet_key)
        settings.set("google_sheets.credentials_file", creds_file)
        
        self.show_info("Google Sheets", "Configuración guardada correctamente.")

    def _test_google_sheets(self):
        """Prueba conexión con Google Sheets."""
        sheet_key = self.google_sheet_key_var.get().strip()
        
        if not sheet_key:
            self.show_warning("Google Sheets", "Ingresá el ID de la hoja primero.")
            return
        
        from database.google_sheets import test_google_sheets_connection
        
        ok, msg = test_google_sheets_connection(sheet_key)
        
        if ok:
            self.show_info("Conexión exitosa", msg)
        else:
            self.show_error("Error de conexión", msg)

    def _download_from_sheets(self):
        """Descarga datos desde Google Sheets."""
        sheet_key = self.google_sheet_key_var.get().strip()
        
        if not sheet_key:
            self.show_warning("Google Sheets", "Ingresá el ID de la hoja primero.")
            return
        
        from database.google_sheets import descargar_desde_google_sheets
        from database.csv_handler import guardar_todos_registros
        
        ok, result = descargar_desde_google_sheets(sheet_key)
        
        if ok:
            # result es la lista de registros
            registros = result
            ok_save, msg_save = guardar_todos_registros(registros)
            
            if ok_save:
                self.show_info("Descarga exitosa", f"Descargados {len(registros)} registros desde Google Sheets.")
                self.app.refresh_all()
            else:
                self.show_error("Error al guardar", msg_save)
        else:
            # result es el mensaje de error
            self.show_error("Error de descarga", result)

    def _upload_to_sheets(self):
        """Sube datos locales a Google Sheets."""
        sheet_key = self.google_sheet_key_var.get().strip()
        
        if not sheet_key:
            self.show_warning("Google Sheets", "Ingresá el ID de la hoja primero.")
            return
        
        from database.csv_handler import cargar_registros
        from database.google_sheets import subir_a_google_sheets
        
        registros = cargar_registros()
        
        if not registros:
            self.show_warning("Sin datos", "No hay registros locales para subir.")
            return
        
        ok, msg = subir_a_google_sheets(registros, sheet_key)
        
        if ok:
            self.show_info("Subida exitosa", msg)
        else:
            self.show_error("Error de subida", msg)

    def _sincronizar_bidireccional(self):
        """Sincronización bidireccional con Google Sheets."""
        sheet_key = self.google_sheet_key_var.get().strip()
        
        if not sheet_key:
            self.show_warning("Google Sheets", "Ingresá el ID de la hoja primero.")
            return
        
        from database.google_sheets import sincronizar_bidireccional
        
        ok, msg = sincronizar_bidireccional(sheet_key)
        
        if ok:
            self.show_info("Sincronización exitosa", msg)
            self.app.refresh_all()
        else:
            self.show_error("Error de sincronización", msg)