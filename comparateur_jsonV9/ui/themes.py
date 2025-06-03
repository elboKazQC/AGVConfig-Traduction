"""
Theme management module for the application.

This module provides theme management capabilities for the application,
allowing users to switch between different visual themes.
"""

from typing import Dict, Any
import tkinter as tk
from config.constants import Colors

class ThemeManager:
    """Manages application themes and theme switching."""

    # Theme definitions
    THEMES = {
        "dark": {
            "name": "Dark Theme",
            "colors": {
                "bg_main": "#2a2a2a",
                "bg_topbar": "#1c1c1c",
                "bg_column": "#2a2a2a",
                "bg_row": "#333333",
                "bg_row_alt": "#3a3a3a",
                "bg_row_hover": "#404040",
                "fg_text": "#ffffff",
                "edit_bg": "#404040",
                "edit_fg": "#ffffff",
                "edit_bg_focus": "#505050",
                "green": "#4caf50",
                "red": "#f44336",
                "amber": "#ffc107",
                "highlight": "#505050",
                "search_highlight": "#ffab00",
                "search_bg": "#3a3a3a"
            },
            "fonts": {
                "default": ("Segoe UI", 11),
                "topbar": ("Segoe UI", 12, "bold"),
                "title": ("Segoe UI", 14, "bold")
            }
        },
        "light": {
            "name": "Light Theme",
            "colors": {
                "bg_main": "#f5f5f5",
                "bg_topbar": "#2196f3",
                "bg_column": "#e0e0e0",
                "bg_row": "#ffffff",
                "bg_row_alt": "#f0f0f0",
                "bg_row_hover": "#e8e8e8",
                "fg_text": "#212121",
                "edit_bg": "#ffffff",
                "edit_fg": "#212121",
                "edit_bg_focus": "#e3f2fd",
                "green": "#4caf50",
                "red": "#f44336",
                "amber": "#ffc107",
                "highlight": "#bbdefb",
                "search_highlight": "#ffab00",
                "search_bg": "#e0e0e0"
            },
            "fonts": {
                "default": ("Segoe UI", 11),
                "topbar": ("Segoe UI", 12, "bold"),
                "title": ("Segoe UI", 14, "bold")
            }
        },
        "high_contrast": {
            "name": "High Contrast",
            "colors": {
                "bg_main": "#000000",
                "bg_topbar": "#000000",
                "bg_column": "#000000",
                "bg_row": "#000000",
                "bg_row_alt": "#0a0a0a",
                "bg_row_hover": "#1a1a1a",
                "fg_text": "#ffffff",
                "edit_bg": "#000000",
                "edit_fg": "#ffffff",
                "edit_bg_focus": "#0d47a1",
                "green": "#00ff00",
                "red": "#ff0000",
                "amber": "#ffff00",
                "highlight": "#ffffff",
                "search_highlight": "#ffff00",
                "search_bg": "#000000"
            },
            "fonts": {
                "default": ("Segoe UI", 12),
                "topbar": ("Segoe UI", 13, "bold"),
                "title": ("Segoe UI", 16, "bold")
            }
        }
    }

    def __init__(self):
        """Initialize the theme manager with the default theme."""
        self.current_theme = "dark"
        self.widgets = []

    def register_widget(self, widget):
        """
        Register a widget to be updated when the theme changes.

        Args:
            widget: The tkinter widget to register
        """
        self.widgets.append(widget)

    def apply_theme(self, theme_key):
        """
        Apply a theme to all registered widgets.

        Args:
            theme_key: The key of the theme to apply
        """
        if theme_key not in self.THEMES:
            return False

        self.current_theme = theme_key
        theme = self.THEMES[theme_key]

        # Update Colors class attributes dynamically
        colors = theme["colors"]
        for key, value in colors.items():
            key_upper = key.upper()
            if hasattr(Colors, key_upper):
                setattr(Colors, key_upper, value)

        # Update registered widgets
        for widget in self.widgets:
            if widget.winfo_exists():
                self._update_widget_theme(widget)
            else:
                # Remove destroyed widgets
                self.widgets.remove(widget)

        return True

    def _update_widget_theme(self, widget):
        """
        Update a widget's appearance based on the current theme.

        Args:
            widget: The widget to update
        """
        widget_type = widget.__class__.__name__

        if widget_type in ("Tk", "Toplevel", "Frame", "LabelFrame"):
            widget.configure(bg=Colors.BG_MAIN)
        elif widget_type == "Label":
            widget.configure(bg=widget.master["bg"], fg=Colors.FG_TEXT)
        elif widget_type == "Entry":
            widget.configure(bg=Colors.EDIT_BG, fg=Colors.EDIT_FG)
        elif widget_type == "Button":
            widget.configure(bg=Colors.BG_COLUMN, fg=Colors.FG_TEXT)
        elif widget_type == "Text":
            widget.configure(bg=Colors.EDIT_BG, fg=Colors.EDIT_FG)

        # Update all children widgets recursively
        for child in widget.winfo_children():
            self._update_widget_theme(child)

    def get_theme_names(self):
        """Get a list of available theme names."""
        return [(key, theme["name"]) for key, theme in self.THEMES.items()]

    def get_current_theme(self):
        """Get the current theme key."""
        return self.current_theme

# Global theme manager instance
theme_manager = ThemeManager()
