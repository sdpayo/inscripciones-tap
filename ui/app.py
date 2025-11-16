"""Aplicación principal con interfaz gráfica."""
import tkinter as tk
from tkinter import ttk
from config.settings import settings

class InscripcionApp:
    """Aplicación principal de inscripciones."""
    
    def __init__(self, root):
        """Inicializa la aplicación."""
        self.root = root
        self.root.title("Sistema de Inscripciones - ESM N°6003")
        self.root.geometry("1400x800")
        
        # Configurar estilo
        self._setup_style()
        
        # Crear estructura principal
        self._create_layout()
        
        # Crear pestañas
        self._create_tabs()
    
    def _setup_style(self):
        """Configura estilos de la aplicación."""
        style = ttk.Style()
        
        # Tema
        theme = settings.get("ui.theme", "clam")
        available_themes = style.theme_names()
        if theme in available_themes:
            style.theme_use(theme)
        else:
            style.theme_use("clam")
        
        # Configuraciones personalizadas
        style.configure("TLabel", padding=2)
        style.configure("TButton", padding=5)
        style.configure("TNotebook.Tab", padding=[10, 5])
    
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
        for tab in [self.form_tab, self.listados_tab, self.historial_tab, self.config_tab]:
            try:
                tab.refresh()
            except Exception as e:
                print(f"[WARN] No se pudo refrescar tab: {e}")

    def update_status(self, mensaje):
        """Actualiza mensaje de estado."""
        self.status_label.config(text=mensaje)
    
    def run(self):
        """Inicia el loop principal."""
        self.root.mainloop()