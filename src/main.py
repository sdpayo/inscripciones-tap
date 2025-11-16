"""Main entry point for the application."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ui import MainWindow
from src.config import Config


def main():
    """Run the application."""
    # Ensure directories exist
    Config.ensure_directories()
    
    # Create and run main window
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()
