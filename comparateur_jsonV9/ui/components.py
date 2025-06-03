# Composants d'interface utilisateur pour l'application Fault Editor
"""
Ce module contient les composants réutilisables de l'interface utilisateur.
Utilisez ces classes pour créer des widgets cohérents et modulaires.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Callable, Optional, Dict, Any
from config.constants import Colors, Fonts, Dimensions

class StyledFrame(ttk.Frame):
    """A styled frame component with consistent padding and styling."""
    def __init__(self, parent, style_type='default', **kwargs):
        padding = kwargs.pop('padding', 10)
        bg_color = kwargs.pop('bg', None)
        style_name = f"{style_type}.TFrame"

        if bg_color:
            style = ttk.Style()
            style.configure(style_name, background=bg_color)

        super().__init__(parent, style=style_name, padding=padding, **kwargs)

    def pack(self, **kwargs):
        """Ensure compatibility with tk.Frame."""
        return super().pack(**kwargs)

    def grid(self, **kwargs):
        """Ensure compatibility with tk.Frame."""
        return super().grid(**kwargs)

    def place(self, **kwargs):
        """Ensure compatibility with tk.Frame."""
        return super().place(**kwargs)

    def as_tk_frame(self) -> tk.Frame:
        """Return self explicitly cast as a tk.Frame."""
        return tk.Frame(self.master)

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

class ProgressDialog:
    """Dialogue de progression pour les opérations longues"""

    def __init__(self, parent, title="Traitement en cours", message="Veuillez patienter..."):
        self.popup = tk.Toplevel(parent)
        self.popup.title(title)
        self.popup.geometry("350x120")
        self.popup.transient(parent)
        self.popup.grab_set()
        self.popup.resizable(False, False)

        # Message principal
        self.message_label = StyledLabel(self.popup, text=message, style_type="default")
        self.message_label.pack(pady=(15, 5))

        # Barre de progression
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.popup, variable=self.progress_var,
                                           maximum=100, mode='determinate')
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 10))

        # Label de statut
        self.status_label = StyledLabel(self.popup, text="", style_type="default")
        self.status_label.pack(pady=(0, 15))

        # Centrer la fenêtre
        self._center_window(parent)

    def _center_window(self, parent):
        """Centre la fenêtre par rapport au parent"""
        self.popup.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.popup.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.popup.winfo_height() // 2)
        self.popup.geometry(f"+{x}+{y}")

    def update_progress(self, value: float, status: str = ""):
        """Met à jour la progression"""
        self.progress_var.set(value)
        if status:
            self.status_label.config(text=status)
        self.popup.update_idletasks()

    def close(self):
        """Ferme le dialogue"""
        self.popup.destroy()

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
