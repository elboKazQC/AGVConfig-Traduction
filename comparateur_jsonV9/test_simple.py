import sys
import os
import unittest
import tkinter as tk

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import app


class TestFaultEditorBasic(unittest.TestCase):
    """Test basic functionality of the FaultEditor application.

    Updated to reflect the current state of the application after evolution.
    Original test was checking for obsolete methods:
    - save_json_file (replaced by save_file)
    - create_widgets (replaced by setup_ui)
    - update_info_frame (no longer exists)
    """

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during testing
        try:
            self.app = app.FaultEditor(self.root)
        except Exception as e:
            self.root.destroy()
            raise e

    def tearDown(self):
        """Clean up after each test method."""
        try:
            if hasattr(self, 'app') and self.app:
                # Clean up the app if it exists
                if hasattr(self.app, 'root') and self.app.root:
                    self.app.root.quit()
            if hasattr(self, 'root') and self.root:
                self.root.quit()
                self.root.destroy()
        except tk.TclError:
            # Handle case where Tkinter is already destroyed
            pass
        except Exception as e:
            print(f"Warning: Error during tearDown: {e}")

    def test_app_has_required_methods(self):
        """Test that the FaultEditor app has all required methods.

        Updated method list to reflect current application state:
        - load_json_file: Still exists (unchanged)
        - save_file: Replaces save_json_file with more generic functionality
        - save_flat_files: New method for handling flat JSON files
        - setup_ui: Replaces create_widgets with improved UI setup
        """
        # Current methods that should exist in the evolved application
        required_methods = [
            'load_json_file',    # Original method still exists
            'save_file',         # Replaces save_json_file
            'save_flat_files',   # New method for flat JSON handling
            'setup_ui'           # Replaces create_widgets
        ]

        for method_name in required_methods:
            with self.subTest(method=method_name):
                self.assertTrue(
                    hasattr(self.app, method_name) and callable(getattr(self.app, method_name)),
                    f"Méthode manquante: {method_name}"
                )

    def test_app_initialization(self):
        """Test that the app initializes properly."""
        self.assertIsNotNone(self.app)
        self.assertIsInstance(self.app, app.FaultEditor)


if __name__ == '__main__':
    unittest.main()
