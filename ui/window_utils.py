import sys
import tkinter as tk
import tkinter.font as tkfont

def enable_windows_dpi_awareness():
    """Mejora el comportamiento de escalado en Windows HiDPI."""
    if sys.platform.startswith("win"):
        try:
            import ctypes
            # per-monitor DPI aware on Windows 8.1+
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

def adapt_scaling(root, design_w=1366, design_h=768, max_scale=1.0, min_font_size=8):
    """
    Escala la UI si la pantalla es menor que la resolución 'design'.
    Llamar justo después de crear `root = tk.Tk()` y antes de crear widgets.
    """
    try:
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        scale = min(screen_w / design_w, screen_h / design_h, max_scale)
        if scale <= 0 or scale >= 1.0:
            return
        try:
            root.tk.call('tk', 'scaling', scale)
        except Exception:
            pass
        for font_name in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont"):
            try:
                f = tkfont.nametofont(font_name)
                new_size = max(min_font_size, int(f.cget("size") * scale))
                f.configure(size=new_size)
            except Exception:
                continue
    except Exception:
        pass

def setup_window_geometry(root, base_w=1366, base_h=768, min_w=800, min_h=600, maximize_if_possible=False):
    """
    Ajusta la geometría inicial de la ventana para que no exceda la pantalla.
    - Si maximize_if_possible=True e hay suficiente espacio, maximiza (Windows: state('zoomed')).
    """
    try:
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        win_w = min(base_w, screen_w)
        win_h = min(base_h, screen_h)
        root.geometry(f"{win_w}x{win_h}")
        root.minsize(min_w, min_h)
        root.resizable(True, True)
        if maximize_if_possible and screen_w >= base_w and screen_h >= base_h:
            try:
                root.state('zoomed')
            except Exception:
                pass
    except Exception:
        pass