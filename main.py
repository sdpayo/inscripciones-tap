import tkinter as tk
from ui.app import InscripcionApp
from ui.window_utils import enable_windows_dpi_awareness, adapt_scaling, setup_window_geometry

def main():
    enable_windows_dpi_awareness()
    root = tk.Tk()

    # Ajustar escala si la pantalla es más pequeña que el diseño base
    adapt_scaling(root, design_w=1366, design_h=768)

    # Ajustar geometría inicial (no exceder la pantalla)
    setup_window_geometry(root, base_w=1366, base_h=768, min_w=900, min_h=600)

    app = InscripcionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()