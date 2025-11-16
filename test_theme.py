"""Test del tema de alto contraste."""
import sys
import importlib.util

# Cargar el módulo sin importar tkinter
spec = importlib.util.spec_from_file_location("theme", "/home/runner/work/inscripciones-tap/inscripciones-tap/ui/theme.py")
module = importlib.util.module_from_spec(spec)

# Mock tkinter antes de ejecutar el módulo
sys.modules['tkinter'] = type(sys)('tkinter')
sys.modules['tkinter.ttk'] = type(sys)('tkinter.ttk')

# Ahora ejecutar el módulo
spec.loader.exec_module(module)
COLORS = module.COLORS
aplicar_tema_alto_contraste = module.aplicar_tema_alto_contraste

def test_colors_defined():
    """Verifica que todos los colores estén definidos."""
    required_colors = [
        "primary", "primary_dark", "secondary", "danger", "warning",
        "info", "light", "dark", "bg", "fg", "border", "hover",
        "selected", "header_bg", "header_fg"
    ]
    
    for color in required_colors:
        assert color in COLORS, f"Color {color} no está definido"
        assert COLORS[color].startswith("#"), f"Color {color} no es un código hexadecimal válido"
    
    print("✅ Todos los colores están definidos correctamente")

def test_contrast_ratios():
    """Verifica que los contrastes sean altos (WCAG AAA)."""
    # Función simple para calcular luminosidad relativa
    def get_luminance(hex_color):
        # Convertir hex a RGB
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Normalizar a 0-1
        r, g, b = r / 255, g / 255, b / 255
        
        # Aplicar función gamma
        r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
        g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
        b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
        
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    def contrast_ratio(color1, color2):
        lum1 = get_luminance(color1)
        lum2 = get_luminance(color2)
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        return (lighter + 0.05) / (darker + 0.05)
    
    # Verificar contraste texto principal
    text_bg_contrast = contrast_ratio(COLORS["fg"], COLORS["bg"])
    print(f"Contraste texto sobre fondo: {text_bg_contrast:.2f}:1")
    assert text_bg_contrast >= 7.0, f"Contraste texto/fondo debe ser >= 7:1 (AAA), es {text_bg_contrast:.2f}:1"
    
    # Verificar contraste headers
    header_contrast = contrast_ratio(COLORS["header_fg"], COLORS["header_bg"])
    print(f"Contraste header: {header_contrast:.2f}:1")
    assert header_contrast >= 7.0, f"Contraste header debe ser >= 7:1 (AAA), es {header_contrast:.2f}:1"
    
    print("✅ Todos los contrastes cumplen con WCAG AAA (>= 7:1)")

def test_theme_function():
    """Verifica que la función aplicar_tema_alto_contraste exista y sea callable."""
    assert callable(aplicar_tema_alto_contraste), "aplicar_tema_alto_contraste debe ser una función"
    print("✅ Función aplicar_tema_alto_contraste está disponible")

def test_alternating_row_colors():
    """Verifica que los colores de filas alternas sean diferentes."""
    assert COLORS["bg"] == "#FFFFFF", "Color de fila par debe ser blanco"
    assert COLORS["light"] == "#F8F9FA", "Color de fila impar debe ser gris claro"
    print("✅ Colores de filas alternas configurados correctamente")

if __name__ == "__main__":
    print("=" * 60)
    print("TEST DE TEMA DE ALTO CONTRASTE")
    print("=" * 60)
    
    try:
        test_colors_defined()
        test_contrast_ratios()
        test_theme_function()
        test_alternating_row_colors()
        
        print("\n" + "=" * 60)
        print("✅ TODOS LOS TESTS PASARON")
        print("=" * 60)
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
