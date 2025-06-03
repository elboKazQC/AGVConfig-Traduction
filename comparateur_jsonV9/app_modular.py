#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modular Application Entry Point

This module provides the modular entry point for the Fault Editor application.
"""

import tkinter as tk
import logging
from main_controller import FaultEditorController

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def run_application():
    """Run the main application."""
    try:
        root = tk.Tk()
        app = FaultEditorController(root)

        # Configure cleanup on window close
        def on_closing():
            app.cleanup()
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()

    except Exception as e:
        logger.error(f"Error running application: {e}")
        raise

if __name__ == "__main__":
    run_application()
