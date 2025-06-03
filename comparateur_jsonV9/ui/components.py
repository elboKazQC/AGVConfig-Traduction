#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI Components Module

This module contains reusable UI components for the application.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, Any, Union, Callable
from config.constants import Colors, Fonts

class StyledFrame(ttk.Frame):
    """Extended Frame class with styling capabilities."""

    def __init__(self, parent: Union[tk.Widget, tk.Tk, tk.Toplevel], style_type: str = "default", **kwargs):
        """Initialize styled frame."""
        # Create style name based on type
        style_name = f"{style_type}.TFrame"
        style = ttk.Style()

        # Set default styling based on type
        if style_type == "column":
            style.configure(style_name, background=Colors.BG_COLUMN, relief='raised')
            kwargs.setdefault('padding', 1)
        elif style_type == "row":
            style.configure(style_name, background=Colors.BG_ROW)
        else:
            style.configure(style_name, background=Colors.BG_MAIN)

        kwargs['style'] = style_name
        super().__init__(parent, **kwargs)

    def as_tk_frame(self) -> ttk.Frame:
        """Return self for compatibility."""
        return self

class StyledButton(ttk.Button):
    """A styled button with consistent appearance."""
    def __init__(self, parent, text, command=None, style_type='default', **kwargs):
        if command is None:
            command = lambda: None  # No-op function as default

        style_name = f"{style_type}.TButton"
        style = ttk.Style()
        style.configure(style_name, padding=6, relief="flat")

        super().__init__(
            parent,
            text=text,
            command=command,
            style=style_name,
            **kwargs
        )

class StyledEntry(ttk.Entry):
    """A styled entry field with consistent appearance."""
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            style='Fault.TEntry',
            **kwargs
        )

class StyledLabel(ttk.Label):
    """A styled label with consistent appearance."""
    def __init__(self, parent, text='', style_type='default', **kwargs):
        super().__init__(parent, text=text, **kwargs)
        self.style_type = style_type
        self.configure_style()

    def configure_style(self):
        """Configure the style of the label based on the style type."""
        style = ttk.Style()
        if self.style_type == 'default':
            style.configure('Default.TLabel', font=('Arial', 12), background='white', foreground='black')
            self.config(style='Default.TLabel')
        elif self.style_type == 'highlight':
            style.configure('Highlight.TLabel', font=('Arial', 12, 'bold'), background='yellow', foreground='black')
            self.config(style='Highlight.TLabel')

class SearchBar(ttk.Frame):
    """A search bar component with entry field and search button."""
    def __init__(self, parent, search_command=None):
        super().__init__(parent, padding=5)

        self.entry = StyledEntry(self)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.search_button = StyledButton(
            self,
            text="🔍 Rechercher",
            command=search_command
        )
        self.search_button.pack(side=tk.LEFT, padx=(5, 0))

class StatusBar(ttk.Frame):
    """A status bar component for displaying application status."""
    def __init__(self, parent):
        super().__init__(parent)

        self.status_label = ttk.Label(
            self,
            text="Prêt",
            padding=(5, 2)
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X)

    def set_status(self, message):
        """Update the status message."""
        self.status_label['text'] = message

def configure_styles():
    """Configure ttk styles for the application."""
    style = ttk.Style()

    # Button styles
    style.configure(
        'Fault.TButton',
        padding=6,
        relief="flat",
        background="#007acc",
        foreground="white"
    )

    # Entry styles
    style.configure(
        'Fault.TEntry',
        padding=5,
        relief="solid"
    )

    # Frame styles
    style.configure(
        'Fault.TFrame',
        background="#ffffff"
    )

class ProgressDialog(tk.Toplevel):
    """A progress dialog window."""

    def __init__(self, parent: Union[tk.Widget, tk.Tk, tk.Toplevel], title: str = "Progress"):
        """Initialize progress dialog."""
        super().__init__(parent)
        self.title(title)
        self.geometry("400x150")
        self.transient(parent)
        self.grab_set()

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(padx=20, pady=20, fill="x")

        # Status label
        self.status_label = tk.Label(self, text="Initializing...")
        self.status_label.pack(pady=10)

        # Cancel button
        self.cancel_button = ttk.Button(self, text="Cancel", command=self.destroy)
        self.cancel_button.pack(pady=10)

    def update_progress(self, value: float, status: str = ""):
        """Update progress bar and status."""
        self.progress_var.set(value)
        if status:
            self.status_label.config(text=status)
        self.update()

class LanguageSelector:
    """Sélecteur de langue avec boutons radio"""

    def __init__(self, parent, current_lang="fr", callback=None):
        self.frame = StyledFrame(parent, style_type="topbar")
        self.lang_var = tk.StringVar(value=current_lang)
        self.callback = callback

        languages = [
            ("FR", "fr"),
            ("EN", "en"),
            ("ES", "es")
        ]

        for text, value in languages:            ttk.Radiobutton(
                self.frame,
                text=text,
                value=value,
                variable=self.lang_var,
                command=self._on_language_change
            ).pack(side="left", padx=2)

    def _on_language_change(self):
        """Appelé quand la langue change"""
        if self.callback:
            self.callback(self.lang_var.get())

    def get_language(self) -> str:
        """Retourne la langue sélectionnée"""
        return self.lang_var.get()

    def set_language(self, language: str):
        """Définit la langue sélectionnée"""
        self.lang_var.set(language)

    def pack(self, **kwargs):
        """Delegate pack method to internal frame"""
        return self.frame.pack(**kwargs)

class FileInfoBar:
    """Barre d'information sur le fichier sélectionné"""

    def __init__(self, parent):
        self.frame = StyledFrame(parent, style_type="toolbar")
        self.frame.pack_propagate(False)

        self.file_label = StyledLabel(
            self.frame,
            text="Aucun fichier sélectionné",
            style_type="topbar"
        )
        self.file_label.pack(side="left", padx=10)

    def update_file(self, filename: str):
        """Met à jour le fichier affiché"""
        self.file_label.config(text=f"Fichier sélectionné : {filename}")

class ToolbarBuilder:
    """Constructeur pour les barres d'outils"""

    @staticmethod
    def create_main_toolbar(parent, callbacks: Dict[str, Callable]) -> tk.Frame:
        """Crée la barre d'outils principale"""
        toolbar = StyledFrame(parent, style_type="toolbar")

        buttons = [
            ("💾 Sync All", callbacks.get("sync_all")),
            ("🔄 Sync One", callbacks.get("sync_one")),
            ("📄 Générer", callbacks.get("generate")),
            ("🔍 Vérifier", callbacks.get("check")),
        ]

        for text, command in buttons:
            if command:
                StyledButton(
                    toolbar,
                    text=text,
                    command=command,
                    style_type="topbar"
                ).pack(side="left", padx=5)

        return toolbar.as_tk_frame()

    @staticmethod
    def create_flat_editor_toolbar(parent, callbacks: Dict[str, Callable]) -> tk.Frame:
        """Crée la barre d'outils pour l'éditeur plat"""
        toolbar = StyledFrame(parent, style_type="toolbar")

        buttons = [
            ("💾 Sauvegarder", callbacks.get("save"), "action"),
            ("🔍 Rechercher", callbacks.get("search"), "topbar"),
            ("🌐 Traduire tout", callbacks.get("translate_all"), "topbar"),
        ]

        for text, command, style in buttons:
            if command:
                StyledButton(
                    toolbar,
                    text=text,
                    command=command,
                    style_type=style
                ).pack(side="left", padx=15, pady=5)

        return toolbar.as_tk_frame()

class ResultsDialog:
    """Dialogue pour afficher les résultats d'opérations"""

    def __init__(self, parent, title: str, content: str, is_success: bool = True):
        self.popup = tk.Toplevel(parent)
        self.popup.title(title)
        self.popup.geometry("800x600")
        self.popup.transient(parent)
        self.popup.resizable(True, True)

        # Configuration des couleurs selon le succès
        bg_color = Colors.BG_MAIN
        text_color = Colors.FG_TEXT if is_success else Colors.RED

        self.popup.configure(bg=bg_color)

        # Frame pour le titre
        title_frame = StyledFrame(self.popup)
        title_frame.pack(fill="x", padx=10, pady=5)

        StyledLabel(
            title_frame,
            text=title,
            style_type="title"
        ).pack()

        # Zone de texte avec scrollbar
        text_frame = StyledFrame(self.popup)
        text_frame.pack(fill="both", expand=True, padx=10, pady=5)

        text_widget = tk.Text(
            text_frame,
            bg=Colors.EDIT_BG,
            fg=Colors.FG_TEXT,
            font=Fonts.DEFAULT,
            wrap=tk.WORD
        )

        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Insérer le contenu
        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)

        # Bouton de fermeture
        button_frame = StyledFrame(self.popup)
        button_frame.pack(fill="x", padx=10, pady=5)

        StyledButton(
            button_frame,
            text="Fermer",
            command=self.popup.destroy,
            style_type="action"
        ).pack(side="right")

        # Centrer la fenêtre
        self._center_window(parent)

    def _center_window(self, parent):
        """Centre la fenêtre par rapport au parent"""
        self.popup.update_idletasks()
        x = (self.popup.winfo_screenwidth() // 2) - (self.popup.winfo_width() // 2)
        y = (self.popup.winfo_screenheight() // 2) - (self.popup.winfo_height() // 2)
        self.popup.geometry(f"+{x}+{y}")

class ConfirmationDialog:
    """Dialogue de confirmation standardisé"""

    def __init__(self, parent, title: str, message: str,
                 ok_text: str = "Oui", cancel_text: str = "Non"):
        self.result = False

        self.popup = tk.Toplevel(parent)
        self.popup.title(title)
        self.popup.geometry("400x150")
        self.popup.transient(parent)
        self.popup.grab_set()
        self.popup.resizable(False, False)

        # Message
        StyledLabel(
            self.popup,
            text=message,
            style_type="default"
        ).pack(pady=20)

        # Boutons
        button_frame = StyledFrame(self.popup)
        button_frame.pack(fill="x", padx=20, pady=10)

        StyledButton(
            button_frame,
            text=ok_text,
            command=self._on_ok,
            style_type="action"
        ).pack(side="right", padx=5)

        StyledButton(
            button_frame,
            text=cancel_text,
            command=self._on_cancel,
            style_type="danger"
        ).pack(side="right", padx=5)

        # Centrer et attendre
        self._center_window(parent)
        self.popup.wait_window()

    def _center_window(self, parent):
        """Centre la fenêtre par rapport au parent"""
        self.popup.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.popup.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.popup.winfo_height() // 2)
        self.popup.geometry(f"+{x}+{y}")

    def _on_ok(self):
        self.result = True
        self.popup.destroy()

    def _on_cancel(self):
        self.result = False
        self.popup.destroy()

    def get_result(self) -> bool:
        return self.result

class SearchableListbox(tk.Frame):
    """A listbox with built-in search functionality."""

    def __init__(self, parent: Union[tk.Widget, tk.Tk, tk.Toplevel], **kwargs):
        """Initialize searchable listbox."""
        super().__init__(parent)

        # Search entry
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self, textvariable=self.search_var)
        self.search_entry.pack(fill="x", padx=5, pady=5)

        # Listbox with scrollbar
        list_frame = tk.Frame(self)
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.listbox = tk.Listbox(list_frame, **kwargs)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)

        self.listbox.configure(yscrollcommand=scrollbar.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind search
        self.search_var.trace('w', self._on_search)
        self._original_items = []

    def insert_items(self, items):
        """Insert items into the listbox."""
        self._original_items = items[:]
        self.listbox.delete(0, tk.END)
        for item in items:
            self.listbox.insert(tk.END, item)

    def _on_search(self, *args):
        """Filter items based on search query."""
        query = self.search_var.get().lower()
        self.listbox.delete(0, tk.END)

        for item in self._original_items:
            if query in str(item).lower():
                self.listbox.insert(tk.END, item)

    def as_tk_frame(self) -> tk.Frame:
        """Return self as a tk.Frame for compatibility."""
        return self
