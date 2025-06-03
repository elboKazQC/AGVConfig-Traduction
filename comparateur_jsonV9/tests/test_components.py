import unittest
import tkinter as tk
from tkinter import ttk, TclError
import sys
import os

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.components import (
    StyledFrame,
    StyledButton,
    StyledEntry,
    SearchBar,
    StatusBar
)

class TestUIComponents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.root = tk.Tk()
        except TclError:
            raise unittest.SkipTest("Tkinter not available in this environment")
        
    def test_styled_frame(self):
        frame = StyledFrame(self.root)
        self.assertIsInstance(frame, ttk.Frame)
        
    def test_styled_button(self):
        button = StyledButton(self.root, text="Test")
        self.assertIsInstance(button, ttk.Button)
        self.assertEqual(button['text'], "Test")
        
    def test_search_bar(self):
        search_called = False
        def on_search():
            nonlocal search_called
            search_called = True
            
        search_bar = SearchBar(self.root, search_command=on_search)
        search_bar.search_button.invoke()
        self.assertTrue(search_called)
        
    def test_status_bar(self):
        status = StatusBar(self.root)
        test_message = "Test Status"
        status.set_status(test_message)
        self.assertEqual(status.status_label['text'], test_message)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "root"):
            cls.root.destroy()

if __name__ == '__main__':
    unittest.main()