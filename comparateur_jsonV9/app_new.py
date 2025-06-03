#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
New Application Entry Point

This module provides the new entry point for the Fault Editor application.
"""

import os
import sys
import logging
import tkinter as tk
from main_controller import FaultEditorController

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create a simple file manager class
class SimpleFileManager:
    """Simple file manager for compatibility."""

    def __init__(self):
        self.file_map = {}
        self.data_map = {}

    def initialize_file_map(self, base_directory: str):
        """Initialize file map with files from base directory."""
        import os
        import json

        self.file_map.clear()
        for root_dir, _, files in os.walk(base_directory):
            for file in files:
                if file.endswith(".json"):
                    self.file_map[file] = os.path.join(root_dir, file)

        logger.info(f"Initialized file map with {len(self.file_map)} files")

def run_application():
    """Run the main application."""
    try:
        root = tk.Tk()
        app = FaultEditorController(root)

        # Create and set up file manager
        file_manager = SimpleFileManager()
        app.file_manager = file_manager

        # Configure cleanup on window close
        def on_closing():
            app.cleanup()
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()

    except Exception as e:
        logger.error(f"Error running application: {e}")
        raise

def main():
    """Main function to run the application."""
    try:
        root = tk.Tk()
        app = FaultEditorController(root)

        # Create and set up file manager
        file_manager = SimpleFileManager()
        app.file_manager = file_manager

        # Configure cleanup on window close
        def on_closing():
            app.cleanup()
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()

    except Exception as e:
        logger.error(f"Error in main: {e}")

def create_application():
    """Create and return application instance."""
    root = tk.Tk()
    app = FaultEditorController(root)

    # Create and set up file manager
    file_manager = SimpleFileManager()
    app.file_manager = file_manager

    return app

# Legacy compatibility: allow the file to be run directly
if __name__ == "__main__":
    main()
