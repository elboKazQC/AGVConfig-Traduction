#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main entry point for the Fault Editor application.

This module initializes the user interface and launches the application.
It sets up the main tkinter window and starts the application using
the MainController class.

Author: AI Assistant
Created: 2024
"""

import os
import sys
import logging
import tkinter as tk
from tkinter import messagebox

# Import our modular components
from main_controller import run_application
from plugins.plugin_system import plugin_manager

# Legacy compatibility imports
from config.constants import *
from models.data_models import ApplicationState, FaultData, FileMetadata
from file_ops.file_manager import FileManager
from search.search_manager import SearchManager
from translation.translation_manager import TranslationManager
from ui.components import *

# Create logs directory
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('logs/app_modular.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# Legacy compatibility wrapper
class FaultEditor:
    """
    Legacy compatibility wrapper that maintains the same interface as the original
    FaultEditor class but uses the new modular architecture underneath.

    This allows existing code that relies on the FaultEditor class to continue
    working without modifications.
    """

    def __init__(self, root):
        """Initialize the legacy wrapper with the new modular controller."""
        logger.info("🔄 Starting Fault Editor with modular architecture (legacy compatibility mode)")

        self.root = root
        self.controller = FaultEditorController(root)

        # Expose commonly used attributes for backward compatibility
        self.lang = self.controller.app_state.current_language
        self.file_map = self.controller.file_manager.file_map
        self.data_map = self.controller.file_manager.data_map
        self.base_dir = self.controller.app_state.base_directory
        self.search_results = self.controller.app_state.search_results

        logger.info("✅ Legacy wrapper initialized with modular backend")

    def __getattr__(self, name):
        """
        Delegate any unknown attribute access to the controller.
        This provides transparent access to controller methods.
        """
        if hasattr(self.controller, name):
            return getattr(self.controller, name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    # Legacy method compatibility
    def initialize_file_map(self, folder):
        """Legacy method compatibility."""
        return self.controller.file_manager.initialize_file_map(folder)

    def setup_ui(self):
        """Legacy method compatibility - UI is already set up by controller."""
        pass

    def open_folder(self):
        """Legacy method compatibility."""
        return self.controller._open_folder()

    def load_flat_json(self):
        """Legacy method compatibility."""
        return self.controller._load_flat_json()

    def show_search(self):
        """Legacy method compatibility."""
        return self.controller._show_search()


def main():
    """
    Main entry point for the Fault Editor application.

    This function can be called from the original app.py interface
    or from the new modular main_controller.py
    """
    try:
        logger.info("🚀 Starting Fault Editor Application")

        # Create the main tkinter window
        root = tk.Tk()

        # Check if we should use legacy mode or new modular mode
        # Default to modular mode for better architecture
        use_legacy_wrapper = os.environ.get('FAULT_EDITOR_LEGACY_MODE', 'false').lower() == 'true'

        if use_legacy_wrapper:
            logger.info("📦 Using legacy compatibility wrapper")
            app = FaultEditor(root)
        else:
            logger.info("🏗️ Using new modular architecture")
            app = FaultEditorController(root)

        # Setup cleanup handler
        def on_closing():
            try:
                if hasattr(app, 'cleanup'):
                    app.cleanup()
                logger.info("🔚 Application closed successfully")
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
            finally:
                root.quit()
                root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)

        logger.info("✅ Application initialized successfully")
        print("🎉 Fault Editor - Architecture Modulaire activée!")
        print("📚 Les modules sont maintenant séparés pour une meilleure maintenabilité")
        print("🤖 L'interface est optimisée pour les agents IA")

        # Start the main event loop
        root.mainloop()

    except ImportError as e:
        error_msg = f"❌ Erreur d'importation des modules: {e}"
        logger.error(error_msg)
        print(error_msg)
        print("💡 Vérifiez que tous les modules sont présents dans les dossiers:")
        print("   - config/")
        print("   - models/")
        print("   - file_ops/")
        print("   - search/")
        print("   - translation/")
        print("   - ui/")
        print("   - script_ops/")
        sys.exit(1)

    except Exception as e:
        error_msg = f"❌ Erreur fatale: {e}"
        logger.error(error_msg, exc_info=True)
        print(error_msg)

        # Try to show error dialog if tkinter is available
        try:
            import tkinter.messagebox as mb
            mb.showerror("Erreur Fatale", f"L'application n'a pas pu démarrer:\n\n{e}")
        except:
            pass

        sys.exit(1)


# Legacy compatibility: allow the file to be run directly
if __name__ == "__main__":
    main()
