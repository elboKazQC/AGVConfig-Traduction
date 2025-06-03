"""
Keyboard navigation enhancements for the application.

This module provides enhanced keyboard navigation capabilities
for the application, improving accessibility and user experience.
"""

import tkinter as tk
from typing import Dict, Any, List, Optional, Callable

class KeyboardNavigator:
    """
    Enhances keyboard navigation in tkinter applications.

    This class improves keyboard navigation through form fields,
    enabling tab order control, keyboard shortcuts, and navigation
    between UI components.
    """

    def __init__(self, root):
        """
        Initialize the keyboard navigator.

        Args:
            root: The root tkinter window
        """
        self.root = root
        self.shortcuts: Dict[str, Callable] = {}
        self.focus_groups: Dict[str, List[tk.Widget]] = {}
        self.current_group: str = "default"
        self.current_index: int = 0

        # Bind global navigation keys
        root.bind("<F6>", self._next_focus_group)
        root.bind("<Shift-F6>", self._prev_focus_group)

    def add_shortcut(self, key: str, callback: Callable, description: str = ""):
        """
        Add a keyboard shortcut.

        Args:
            key: The key combination (e.g., "<Control-s>")
            callback: The function to call when the shortcut is triggered
            description: A description of what the shortcut does
        """
        self.shortcuts[key] = {
            "callback": callback,
            "description": description
        }
        self.root.bind(key, lambda e: callback())

    def define_focus_group(self, group_name: str, widgets: List[tk.Widget]):
        """
        Define a group of widgets for keyboard navigation.

        Args:
            group_name: The name of the focus group
            widgets: List of widgets in this group
        """
        self.focus_groups[group_name] = widgets

        # Bind navigation within group
        for widget in widgets:
            widget.bind("<Up>", lambda e, g=group_name: self._navigate_group(g, -1))
            widget.bind("<Down>", lambda e, g=group_name: self._navigate_group(g, 1))
            widget.bind("<Home>", lambda e, g=group_name: self._navigate_group(g, "first"))
            widget.bind("<End>", lambda e, g=group_name: self._navigate_group(g, "last"))

    def activate_group(self, group_name: str):
        """
        Activate a focus group.

        Args:
            group_name: The name of the group to activate
        """
        if group_name in self.focus_groups and self.focus_groups[group_name]:
            self.current_group = group_name
            self.current_index = 0
            self.focus_groups[group_name][0].focus_set()

    def _next_focus_group(self, event=None):
        """Move focus to the next focus group."""
        groups = list(self.focus_groups.keys())
        if not groups:
            return

        current_idx = groups.index(self.current_group) if self.current_group in groups else -1
        next_idx = (current_idx + 1) % len(groups)
        self.activate_group(groups[next_idx])

    def _prev_focus_group(self, event=None):
        """Move focus to the previous focus group."""
        groups = list(self.focus_groups.keys())
        if not groups:
            return

        current_idx = groups.index(self.current_group) if self.current_group in groups else 0
        prev_idx = (current_idx - 1) % len(groups)
        self.activate_group(groups[prev_idx])

    def _navigate_group(self, group_name: str, direction):
        """
        Navigate within a focus group.

        Args:
            group_name: The name of the focus group
            direction: Navigation direction (1=next, -1=previous, "first", "last")
        """
        if group_name not in self.focus_groups or not self.focus_groups[group_name]:
            return

        widgets = self.focus_groups[group_name]

        if direction == "first":
            self.current_index = 0
        elif direction == "last":
            self.current_index = len(widgets) - 1
        else:
            current_idx = self.current_index
            self.current_index = (current_idx + direction) % len(widgets)

        # Set focus to the widget
        widgets[self.current_index].focus_set()

    def show_help_dialog(self):
        """Show a help dialog with keyboard shortcuts."""
        help_window = tk.Toplevel(self.root)
        help_window.title("Keyboard Shortcuts Help")
        help_window.geometry("500x400")
        help_window.transient(self.root)
        help_window.grab_set()

        # Create scrollable area
        frame = tk.Frame(help_window)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Add title
        tk.Label(frame, text="Keyboard Shortcuts", font=("Segoe UI", 14, "bold")).pack(pady=(0, 10))

        # Navigation section
        tk.Label(frame, text="Navigation", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(10, 5))

        nav_text = """
F6: Next focus group
Shift+F6: Previous focus group
Tab: Next field
Shift+Tab: Previous field
Up/Down: Navigate within a group
Home: First item in group
End: Last item in group
        """

        tk.Label(frame, text=nav_text, justify="left").pack(anchor="w", padx=10)

        # Application shortcuts section
        tk.Label(frame, text="Application Shortcuts", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(10, 5))

        for key, shortcut in self.shortcuts.items():
            shortcut_text = f"{key}: {shortcut['description']}"
            tk.Label(frame, text=shortcut_text, justify="left").pack(anchor="w", padx=10)

        # Close button
        tk.Button(help_window, text="Close", command=help_window.destroy).pack(pady=10)

        # Center window
        help_window.update_idletasks()
        width = help_window.winfo_width()
        height = help_window.winfo_height()
        x = (help_window.winfo_screenwidth() // 2) - (width // 2)
        y = (help_window.winfo_screenheight() // 2) - (height // 2)
        help_window.geometry(f'{width}x{height}+{x}+{y}')

# Create global keyboard navigator instance
keyboard_navigator = None

def init_keyboard_navigation(root):
    """Initialize the keyboard navigator."""
    global keyboard_navigator
    keyboard_navigator = KeyboardNavigator(root)
    return keyboard_navigator
