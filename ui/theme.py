"""Tema oscuro profesional."""
from tkinter import ttk

COLORS = {
    "bg_main": "#2B2B2B",        # Fondo principal
    "bg_form": "#1E1E1E",        # Fondo formularios
    "bg_input": "#3C3C3C",       # Fondo campos
    "fg_primary": "#FFFFFF",     # Texto blanco
    "fg_secondary": "#CCCCCC",   # Texto gris claro
    "border": "#4A4A4A",         # Bordes
    "header_bg": "#1A1A1A",      # Headers tabla negro
    "header_fg": "#FFFFFF",      # Headers texto blanco
    "button_bg": "#3C3C3C",      # Botones gris
    "button_hover": "#4A4A4A",   # Botones hover
    "selected": "#505050",       # Selección
    "accent": "#6A6A6A"          # Acento
}

def aplicar_tema_alto_contraste(root):
    """Aplica tema oscuro profesional."""
    style = ttk.Style(root)
    
    try:
        style.theme_use("clam")
    except:
        style.theme_use("default")
    
    # === CONFIGURACIÓN GENERAL ===
    style.configure(".",
        background=COLORS["bg_main"],
        foreground=COLORS["fg_primary"],
        bordercolor=COLORS["border"],
        darkcolor=COLORS["bg_form"],
        lightcolor=COLORS["accent"],
        troughcolor=COLORS["bg_input"],
        fieldbackground=COLORS["bg_input"],
        selectbackground=COLORS["selected"],
        selectforeground=COLORS["fg_primary"],
        font=("Segoe UI", 9)
    )
    
    # === FRAMES ===
    style.configure("TFrame",
        background=COLORS["bg_main"]
    )
    
    # === LABELS ===
    style.configure("TLabel",
        background=COLORS["bg_main"],
        foreground=COLORS["fg_primary"],
        font=("Segoe UI", 9)
    )
    
    # === BUTTONS ===
    style.configure("TButton",
        background=COLORS["button_bg"],
        foreground=COLORS["fg_primary"],
        bordercolor=COLORS["border"],
        borderwidth=1,
        relief="flat",
        font=("Segoe UI", 9),
        padding=(10, 5)
    )
    
    style.map("TButton",
        background=[("active", COLORS["button_hover"]), ("pressed", COLORS["button_hover"])],
        foreground=[("active", COLORS["fg_primary"])],
        bordercolor=[("active", COLORS["accent"])]
    )
    
    # === ENTRIES ===
    style.configure("TEntry",
        fieldbackground=COLORS["bg_input"],
        foreground=COLORS["fg_primary"],
        bordercolor=COLORS["border"],
        insertcolor=COLORS["fg_primary"],
        lightcolor=COLORS["border"],
        darkcolor=COLORS["border"]
    )
    
    style.map("TEntry",
        fieldbackground=[("focus", COLORS["bg_input"])],
        bordercolor=[("focus", COLORS["accent"])]
    )
    
    # === COMBOBOX ===
    style.configure("TCombobox",
        fieldbackground=COLORS["bg_input"],
        background=COLORS["bg_input"],
        foreground=COLORS["fg_primary"],
        arrowcolor=COLORS["fg_primary"],
        bordercolor=COLORS["border"],
        selectbackground=COLORS["selected"],
        selectforeground=COLORS["fg_primary"]
    )
    
    style.map("TCombobox",
        fieldbackground=[("readonly", COLORS["bg_input"]), ("focus", COLORS["bg_input"])],
        selectbackground=[("readonly", COLORS["selected"])],
        bordercolor=[("focus", COLORS["accent"])]
    )
    
    # === TREEVIEW (Tablas) ===
    style.configure("Treeview",
        background=COLORS["bg_form"],
        foreground=COLORS["fg_primary"],
        fieldbackground=COLORS["bg_form"],
        borderwidth=0,
        font=("Segoe UI", 9)
    )
    
    style.configure("Treeview.Heading",
        background=COLORS["header_bg"],
        foreground=COLORS["header_fg"],
        borderwidth=1,
        relief="flat",
        font=("Segoe UI", 9, "bold")
    )
    
    style.map("Treeview.Heading",
        background=[("active", COLORS["button_hover"])],
        foreground=[("active", COLORS["fg_primary"])]
    )
    
    style.map("Treeview",
        background=[("selected", COLORS["selected"])],
        foreground=[("selected", COLORS["fg_primary"])]
    )
    
    # === LABELFRAME ===
    style.configure("TLabelframe",
        background=COLORS["bg_main"],
        foreground=COLORS["fg_primary"],
        bordercolor=COLORS["border"],
        borderwidth=1,
        relief="flat"
    )
    
    style.configure("TLabelframe.Label",
        background=COLORS["bg_main"],
        foreground=COLORS["fg_primary"],
        font=("Segoe UI", 10, "bold")
    )
    
    # === NOTEBOOK (Pestañas) ===
    style.configure("TNotebook",
        background=COLORS["bg_main"],
        borderwidth=0
    )
    
    style.configure("TNotebook.Tab",
        background=COLORS["bg_form"],
        foreground=COLORS["fg_secondary"],
        bordercolor=COLORS["border"],
        padding=(15, 8),
        font=("Segoe UI", 9)
    )
    
    style.map("TNotebook.Tab",
        background=[("selected", COLORS["bg_main"])],
        foreground=[("selected", COLORS["fg_primary"])],
        bordercolor=[("selected", COLORS["accent"])]
    )
    
    # === SCROLLBAR ===
    style.configure("Vertical.TScrollbar",
        background=COLORS["bg_input"],
        troughcolor=COLORS["bg_form"],
        bordercolor=COLORS["border"],
        arrowcolor=COLORS["fg_primary"]
    )
    
    # === CHECKBUTTON ===
    style.configure("TCheckbutton",
        background=COLORS["bg_main"],
        foreground=COLORS["fg_primary"],
        font=("Segoe UI", 9)
    )
    
    # === RADIOBUTTON ===
    style.configure("TRadiobutton",
        background=COLORS["bg_main"],
        foreground=COLORS["fg_primary"],
        font=("Segoe UI", 9)
    )
    
    # === SEPARADOR ===
    style.configure("TSeparator",
        background=COLORS["border"]
    )
    
    return style
