#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test module for UI components.
"""

import unittest
import tkinter as tk
from typing import Union
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ui.components import StyledFrame, SearchableListbox
    from config.constants import Colors
except ImportError as e:
    print(f"Import error: {e}")
    StyledFrame = None
    SearchableListbox = None

class TestComponents(unittest.TestCase):
    """Test cases for UI components."""

    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the test window

    def tearDown(self):
        """Clean up after tests."""
        if self.root:
            self.root.destroy()

    def test_styled_frame_creation(self):
        """Test StyledFrame creation."""
        if StyledFrame is None:
            self.skipTest("StyledFrame not available")

        frame = StyledFrame(self.root)
        self.assertIsInstance(frame, tk.Frame)
        self.assertIsInstance(frame, StyledFrame)

    def test_styled_frame_as_tk_frame(self):
        """Test StyledFrame as_tk_frame method."""
        if StyledFrame is None:
            self.skipTest("StyledFrame not available")

        frame = StyledFrame(self.root)
        tk_frame = frame.as_tk_frame()
        self.assertIsInstance(tk_frame, tk.Frame)

    def test_searchable_listbox_creation(self):
        """Test SearchableListbox creation."""
        if SearchableListbox is None:
            self.skipTest("SearchableListbox not available")

        listbox = SearchableListbox(self.root)
        self.assertIsInstance(listbox, tk.Frame)
        self.assertIsInstance(listbox, SearchableListbox)

if __name__ == '__main__':
    unittest.main()
