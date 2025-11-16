"""Tema personalizado con alto contraste."""
from tkinter import ttk

# Colores principales
COLORS = {
    "primary": "#0066CC",      # Azul principal
    "primary_dark": "#004499", # Azul oscuro
    "secondary": "#28A745",    # Verde éxito
    "danger": "#DC3545",       # Rojo peligro
    "warning": "#FFC107",      # Amarillo advertencia
    "info": "#17A2B8",         # Cyan información
    "light": "#F8F9FA",        # Gris muy claro
    "dark": "#212529",         # Gris muy oscuro
    "bg": "#FFFFFF",           # Fondo blanco
    "fg": "#212529",           # Texto negro
    "border": "#DEE2E6",       # Borde gris claro
    "hover": "#E9ECEF",        # Hover gris
    "selected": "#CCE5FF",     # Selección azul claro
    "header_bg": "#495057",    # Header gris oscuro
    "header_fg": "#FFFFFF",    # Header texto blanco
}

def aplicar_tema_alto_contraste(root):
    """Aplica tema con alto contraste a toda la aplicación."""
    style = ttk.Style(root)
    
    # Usar tema base
    try:
        style.theme_use("clam")
    except:
        style.theme_use("default")
    
    # === CONFIGURACIÓN GENERAL ===
    style.configure(".",
        background=COLORS["bg"],
        foreground=COLORS["fg"],
        bordercolor=COLORS["border"],
        darkcolor=COLORS["dark"],
        lightcolor=COLORS["light"],
        troughcolor=COLORS["light"],
        focuscolor=COLORS["primary"],
        selectbackground=COLORS["selected"],
        selectforeground=COLORS["dark"],
        font=("Segoe UI", 10)
    )
    
    # === LABELS ===
    style.configure("TLabel",
        background=COLORS["bg"],
        foreground=COLORS["dark"],
        font=("Segoe UI", 10)
    )
    
    style.configure("Title.TLabel",
        font=("Segoe UI", 14, "bold"),
        foreground=COLORS["primary_dark"]
    )
    
    # === BUTTONS ===
    style.configure("TButton",
        background=COLORS["primary"],
        foreground=COLORS["dark"],
        borderwidth=1,
        focuscolor="none",
        font=("Segoe UI", 10),
        padding=(10, 5)
    )
    
    style.map("TButton",
        background=[("active", COLORS["primary_dark"]), ("pressed", COLORS["primary_dark"])],
        foreground=[("active", COLORS["fg"])]
    )
    
    # Botón de éxito (verde)
    style.configure("Success.TButton",
        background=COLORS["secondary"],
        foreground="white"
    )
    
    # Botón de peligro (rojo)
    style.configure("Danger.TButton",
        background=COLORS["danger"],
        foreground="white"
    )
    
    # === ENTRIES ===
    style.configure("TEntry",
        fieldbackground=COLORS["bg"],
        foreground=COLORS["dark"],
        bordercolor=COLORS["border"],
        lightcolor=COLORS["border"],
        darkcolor=COLORS["border"],
        insertcolor=COLORS["dark"]
    )
    
    # === COMBOBOX ===
    style.configure("TCombobox",
        fieldbackground=COLORS["bg"],
        background=COLORS["bg"],
        foreground=COLORS["dark"],
        arrowcolor=COLORS["dark"],
        bordercolor=COLORS["border"]
    )
    
    # === TREEVIEW (Tablas) ===
    style.configure("Treeview",
        background=COLORS["bg"],
        foreground=COLORS["dark"],
        fieldbackground=COLORS["bg"],
        borderwidth=1,
        font=("Segoe UI", 9)
    )
    
    style.configure("Treeview.Heading",
        background=COLORS["header_bg"],
        foreground=COLORS["header_fg"],
        borderwidth=1,
        font=("Segoe UI", 10, "bold")
    )
    
    style.map("Treeview.Heading",
        background=[("active", COLORS["primary_dark"])]
    )
    
    style.map("Treeview",
        background=[("selected", COLORS["primary"])],
        foreground=[("selected", "white")]
    )
    
    # === LABELFRAME ===
    style.configure("TLabelframe",
        background=COLORS["bg"],
        foreground=COLORS["dark"],
        bordercolor=COLORS["border"],
        borderwidth=2
    )
    
    style.configure("TLabelframe.Label",
        background=COLORS["bg"],
        foreground=COLORS["primary_dark"],
        font=("Segoe UI", 10, "bold")
    )
    
    # === NOTEBOOK (Pestañas) ===
    style.configure("TNotebook",
        background=COLORS["light"],
        borderwidth=0
    )
    
    style.configure("TNotebook.Tab",
        background=COLORS["light"],
        foreground=COLORS["dark"],
        padding=(15, 8),
        font=("Segoe UI", 10)
    )
    
    style.map("TNotebook.Tab",
        background=[("selected", COLORS["bg"])],
        foreground=[("selected", COLORS["primary_dark"])],
        expand=[("selected", [1, 1, 1, 0])]
    )
    
    return style
