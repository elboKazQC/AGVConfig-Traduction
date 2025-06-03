"""
Main Application Controller

This module provides the main application controller that orchestrates all the modular components
of the Fault Editor application. It replaces the monolithic FaultEditor class with a clean,
modular architecture that's easier for AI agents to understand and modify.

Author: AI Assistant
Created: 2024
"""

import os
import sys
import json
import logging
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import glob
from typing import Dict, List, Any, Optional, Tuple, cast

# Import modules
from config.constants import Colors, Fonts, Messages
from translation.translation_manager import TranslationManager
from file_ops.file_manager import FileManager
from search.search_manager import SearchManager
from script_ops.script_operations import ScriptOperations
from ui.components import StyledFrame, StyledButton, StyledLabel
from ui.flat_editor import FlatEditor
from ui.hierarchical_editor import HierarchicalEditor
from ui.themes import theme_manager
from ui.keyboard_nav import init_keyboard_navigation
from plugins.plugin_system import plugin_manager
from models.data_models import ApplicationState

# LanguageSelector class (temporary until moved to its own module)
class LanguageSelector:
    """Handles language selection for the application."""

    def __init__(self, parent, current_language="fr", callback=None):
        """Initialize the language selector."""
        self.parent = parent
        self.current_language = current_language
        self.callback = callback
        self.languages = {
            "fr": "Français",
            "en": "English",
            "es": "Español"
        }

    def create_selector(self, container):
        """Create the language selector UI."""
        self.var = tk.StringVar(value=self.current_language)

        # Create frame for language selector
        frame = tk.Frame(container, bg=Colors.BG_TOPBAR)
        frame.pack(side="right", padx=10)

        # Create label
        label = tk.Label(frame, text="🌐", bg=Colors.BG_TOPBAR, fg="white", font=Fonts.DEFAULT)
        label.pack(side="left", padx=(0, 5))

        # Create dropdown
        dropdown = ttk.Combobox(frame, textvariable=self.var, values=list(self.languages.keys()),
                                width=2, state="readonly")
        dropdown.pack(side="left")

        # Bind selection event
        dropdown.bind("<<ComboboxSelected>>", self._on_language_change)

        return frame

    def _on_language_change(self, event):
        """Handle language change event."""
        new_lang = self.var.get()
        if new_lang != self.current_language:
            self.current_language = new_lang
            if self.callback:
                self.callback(new_lang)

# Create convenient aliases for frequently used constants
# Remove this constant and use Colors.BG_MAIN directly
# Colors.BG_MAIN = Colors.BG_MAIN
# Colors.BG_TOPBAR = Colors.BG_TOPBAR
# Colors.BG_COLUMN = Colors.BG_COLUMN
Fonts.DEFAULT = Fonts.DEFAULT

# Configure logging
logger = logging.getLogger(__name__)


class FaultEditorController:
    """
    Main application controller that orchestrates all modular components.

    This class replaces the monolithic FaultEditor class and provides a clean
    interface for managing the application state and coordinating between modules.
    """

    def __init__(self, root: tk.Tk):
        """
        Initialize the main application controller.

        Args:
            root: The main tkinter window
        """
        logger.info("🚀 Initializing Fault Editor Controller")

        self.root = root
        self.app_state = ApplicationState()

        # Initialize managers
        self.file_manager = FileManager()
        self.search_manager = SearchManager()
        self.translation_manager = TranslationManager()
          # Script operations will be initialized after we have a base directory
        self.script_operations = None        # Initialize UI components
        self.hierarchical_editor = HierarchicalEditor(cast(tk.Widget, self.root), self.app_state)
        self.flat_editor = FlatEditor(root, self.translation_manager)

        # UI references
        self.status_label: Optional[tk.Label] = None
        self.tools_frame: Optional[tk.Frame] = None
        self.main_canvas: Optional[tk.Canvas] = None
        self.selected_file_label: Optional[tk.Label] = None

        # Variables for UI controls
        self.sync_one_var = tk.StringVar()
        self.genfichier_file_var = tk.StringVar()
        self.genfichier_src_var = tk.StringVar(value="fr")
        self.genfichier_tgt_var = tk.StringVar(value="en")

        # Setup the UI
        self._setup_ui()

        logger.info("✅ Fault Editor Controller initialized successfully")

    def _setup_ui(self):
        """Setup the main user interface."""
        logger.info("Setting up main user interface")

        # Configure window
        self.root.title("Fault Editor - Modular Architecture")
        self.root.geometry("1400x800")
        self.root.configure(bg=Colors.BG_MAIN)

        # Setup styles
        self._setup_styles()

        # Create main UI components
        self._create_topbar()
        self._create_toolbar()
        self._create_main_area()
        self._create_status_bar()

        # Bind keyboard shortcuts
        self._bind_shortcuts()

        logger.info("✅ Main UI setup complete")

    def _setup_styles(self):
        """Configure TTK styles."""
        style = ttk.Style()
        style.configure('TRadiobutton', font=Fonts.DEFAULT)
        style.configure('TButton', font=Fonts.DEFAULT)

        # Custom scrollbar styles
        style.configure("Custom.Vertical.TScrollbar",                       background=Colors.BG_MAIN,
                       troughcolor=Colors.BG_MAIN,
                       arrowcolor="white")

    def _create_topbar(self):
        """Create the top navigation bar."""
        topbar = StyledFrame(self.root, bg=Colors.BG_TOPBAR, height=60)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        # Logo
        logo_frame = tk.Frame(topbar, bg=Colors.BG_TOPBAR)
        logo_frame.pack(side="left", padx=10)

        logo_label = tk.Label(
            logo_frame,
            text="noovelia",
            font=("Segoe UI", 16),
            bg=Colors.BG_TOPBAR,
            fg="white"
        )
        logo_label.pack(side="left")        # Right side controls
        controls_frame = tk.Frame(topbar, bg=Colors.BG_TOPBAR)
        controls_frame.pack(side="right", padx=10)

        # Search button
        search_btn = StyledButton(
            controls_frame,
            text="🔍 Rechercher",
            command=self._show_search,
            style_type="topbar"
        )
        search_btn.pack(side="right", padx=(10, 2))

        # File operations buttons
        open_btn = StyledButton(
            controls_frame,
            text="📂 Ouvrir un dossier",
            command=self._open_folder,
            style_type="topbar"
        )
        open_btn.pack(side="right", padx=2)

        load_flat_btn = StyledButton(
            controls_frame,
            text="📄 Charger JSON plat",
            command=self._load_flat_json,
            style_type="topbar"
        )
        load_flat_btn.pack(side="right", padx=2)

        # Language selector
        self.language_selector = LanguageSelector(
            controls_frame,
            self.app_state.current_language,
            self._on_language_change
        )
        self.language_frame = self.language_selector.create_selector(controls_frame)

    def _create_toolbar(self):
        """Create the main toolbar with script operation buttons."""
        self.tools_frame = StyledFrame(self.root, bg=Colors.BG_COLUMN, height=50)
        self.tools_frame.pack(fill="x", pady=(0, 5))
        self.tools_frame.pack_propagate(False)

        # Script operation buttons
        buttons = [
            ("Synchroniser tous les fichiers", self._run_sync_all),
            ("Générer les fichiers manquants", self._run_generer_manquant),
            ("Vérifier la cohérence", self._run_check_coherence),
            ("🔍 Vérifier l'orthographe", self._run_spell_check),
        ]

        for text, command in buttons:
            btn = StyledButton(self.tools_frame, text=text, command=command, style_type="action")
            btn.pack(side="left", padx=5)

        # File-specific operations
        self._create_file_operations()

        # Selected file label
        self.selected_file_label = tk.Label(
            self.tools_frame,
            text="Fichier sélectionné :",
            bg=Colors.BG_COLUMN,
            fg="white",
            font=Fonts.DEFAULT
        )
        self.selected_file_label.pack(side="left", padx=10)

    def _create_file_operations(self):
        """Create file-specific operation controls."""
        # Sync one file
        tk.Label(
            self.tools_frame,
            text="Fichier à synchroniser:",
            bg=Colors.BG_COLUMN,
            fg="white"
        ).pack(side="left", padx=(10, 1))

        ttk.Entry(
            self.tools_frame,
            textvariable=self.sync_one_var,
            width=25
        ).pack(side="left")

        StyledButton(
            self.tools_frame,
            text="Synchroniser ce fichier",
            command=self._run_sync_one,
            style_type="action"
        ).pack(side="left", padx=5)

        # Generate file controls
        tk.Label(
            self.tools_frame,
            text="gen_fichier:",
            bg=Colors.BG_COLUMN,
            fg="white"
        ).pack(side="left", padx=(10, 1))

        ttk.Entry(
            self.tools_frame,
            textvariable=self.genfichier_file_var,
            width=20
        ).pack(side="left")

        tk.Label(
            self.tools_frame,
            text="src:",
            bg=Colors.BG_COLUMN,
            fg="white"
        ).pack(side="left", padx=(10, 1))

        ttk.Entry(
            self.tools_frame,
            textvariable=self.genfichier_src_var,
            width=5
        ).pack(side="left")

        tk.Label(
            self.tools_frame,
            text="tgt:",
            bg=Colors.BG_COLUMN,
            fg="white"
        ).pack(side="left", padx=(10, 1))

        ttk.Entry(
            self.tools_frame,
            textvariable=self.genfichier_tgt_var,
            width=5
        ).pack(side="left")

        StyledButton(
            self.tools_frame,
            text="Générer fichier",
            command=self._run_generer_fichier,
            style="secondary"
        ).pack(side="left", padx=5)

    def _create_main_area(self):
        """Create the main content area."""
        # Container for canvas and scrollbars
        container = tk.Frame(self.root, bg=Colors.BG_MAIN)
        container.pack(fill="both", expand=True)

        # Main canvas for hierarchical view
        self.main_canvas = tk.Canvas(container, bg=Colors.BG_MAIN)
        self.main_canvas.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar_y = ttk.Scrollbar(
            container,
            orient="vertical",
            command=self.main_canvas.yview,
            style="Custom.Vertical.TScrollbar"
        )
        scrollbar_y.pack(side="right", fill="y")
        self.main_canvas.configure(yscrollcommand=scrollbar_y.set)

        # Configure scrolling
        self.main_canvas.bind("<MouseWheel>", self._on_mousewheel)

    def _create_status_bar(self):
        """Create the status bar."""
        self.status_label = tk.Label(
            self.root,
            text="Prêt - Interface modulaire chargée",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg=Colors.BG_TOPBAR,
            fg="white",
            font=Fonts.DEFAULT
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def _bind_shortcuts(self):
        """Bind keyboard shortcuts."""
        self.root.bind("<Control-f>", lambda e: self._show_search())
        self.root.bind("<Control-o>", lambda e: self._open_folder())
        self.root.bind("<F5>", lambda e: self._reload_current_view())

    # Event handlers

    def _on_language_change(self, new_language: str):
        """Handle language change."""
        logger.info(f"Language changed to: {new_language}")
        self.app_state.current_language = new_language
        self._reload_current_view()

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        if self.main_canvas:
            self.main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _update_status(self, message: str):
        """Update the status bar message."""
        if self.status_label:
            self.status_label.config(text=message)
        logger.info(f"Status: {message}")

    # File operations
    def _open_folder(self) -> None:
        """
        Open a folder containing JSON files and initialize the file manager.

        This method updates the application state with the selected directory
        and loads the hierarchical view of JSON files.

        Raises:
            Exception: If the folder cannot be opened or initialized.
        """
        folder_path = filedialog.askdirectory(title="Sélectionner le dossier JSON")
        if folder_path:
            try:
                self.app_state.base_directory = folder_path
                self.file_manager.initialize_directory(folder_path)
                self._initialize_script_operations(folder_path)
                self._update_status(f"Dossier ouvert: {folder_path}")
                self._load_hierarchical_view()
                logger.info(f"Folder opened: {folder_path}")
            except Exception as e:
                logger.error(f"Error opening folder: {e}")
                messagebox.showerror("Erreur", f"Impossible d'ouvrir le dossier: {e}")

    def _initialize_script_operations(self, base_directory: str):
        """Initialize script operations with the base directory."""
        try:
            self.script_operations = ScriptOperations(self.root, base_directory, self._update_status)
            logger.info(f"Script operations initialized for directory: {base_directory}")
        except Exception as e:
            logger.error(f"Failed to initialize script operations: {e}")
            self.script_operations = None

    def _ensure_script_operations(self) -> bool:
        """Ensure script operations are initialized. Returns True if available."""
        if self.script_operations is None:
            if self.app_state.base_directory:
                self._initialize_script_operations(self.app_state.base_directory)
            else:
                self._update_status("❌ Aucun dossier ouvert")
                return False
        return self.script_operations is not None and self.app_state.base_directory is not None

    def _load_flat_json(self) -> None:
        """
        Load flat JSON files for editing.

        This method opens a file dialog to select a French JSON file and
        derives the corresponding English and Spanish file paths for editing.

        Raises:
            Exception: If the JSON files cannot be loaded.
        """
        if not self.app_state.base_directory:
            messagebox.showwarning("Attention", "Veuillez d'abord ouvrir un dossier")
            return

        # Open file selection dialog for French file
        fr_file = filedialog.askopenfilename(
            title="Sélectionner le fichier français",
            initialdir=self.app_state.base_directory,
            filetypes=[("JSON files", "*.json")]
        )

        if fr_file:
            try:
                # Derive English and Spanish file paths
                base_name = fr_file.replace("_fr.json", "")
                en_file = f"{base_name}_en.json"
                es_file = f"{base_name}_es.json"

                self.flat_editor.load_flat_json(fr_file, en_file, es_file)
                self._update_status("Éditeur JSON plat ouvert")

            except Exception as e:
                logger.error(f"Error loading flat JSON: {e}")
                messagebox.showerror("Erreur", f"Impossible de charger les fichiers JSON: {e}")

    def _load_hierarchical_view(self):
        """Load the hierarchical view of JSON files."""
        if not self.app_state.base_directory:
            return

        try:
            self.hierarchical_editor.load_data(
                self.app_state.base_directory,
                self.app_state.current_language,
                self.main_canvas
            )
            self._update_status("Vue hiérarchique chargée")
        except Exception as e:
            logger.error(f"Error loading hierarchical view: {e}")
            self._update_status(f"Erreur: {e}")

    def _reload_current_view(self):
        """Reload the current view with updated language."""
        if self.app_state.base_directory:
            self._load_hierarchical_view()

    def _show_search(self) -> None:
        """
        Show the search interface for the application.

        This method activates the search bar and updates the status.

        Raises:
            Exception: If the search interface cannot be shown.
        """
        try:
            self.search_manager.show_search_bar(cast(tk.Widget, self.root), self._on_search_result)
            self._update_status("Recherche activée")
        except Exception as e:
            logger.error(f"Error showing search: {e}")
            self._update_status(f"Erreur de recherche: {e}")

    def _on_search_result(self, results: List[Any]):
        """Handle search results."""
        self.app_state.search_results = results
        self._update_status(f"{len(results)} résultats trouvés")

    # Script operations
    def _run_sync_all(self):
        """Run sync all files script."""
        if not self._ensure_script_operations():
            return

        if self.app_state.base_directory:
            cmd = ["python", "sync_all.py", self.app_state.base_directory]
            if self.script_operations and self.script_operations.runner:
                self.script_operations.runner.run_command(cmd, "Synchronisation de tous les fichiers")

    def _run_sync_one(self):
        """Run sync one file script."""
        filename = self.sync_one_var.get().strip()
        if not filename:
            self._update_status("❌ Aucun fichier spécifié")
            return

        if not self._ensure_script_operations():
            return

        if self.app_state.base_directory:
            file_path = os.path.join(self.app_state.base_directory, filename)
            cmd = ["python", "sync_one.py", file_path]
            if self.script_operations and self.script_operations.runner:
                self.script_operations.runner.run_command(cmd, f"Synchronisation de {filename}")

    def _run_generer_fichier(self):
        """Run generate file script."""
        filename = self.genfichier_file_var.get().strip()
        src_lang = self.genfichier_src_var.get().strip()
        tgt_lang = self.genfichier_tgt_var.get().strip()

        if not (filename and src_lang and tgt_lang):
            self._update_status("❌ Arguments manquants")
            return

        if not self._ensure_script_operations():
            return

        if self.app_state.base_directory:
            cmd = ["python", "generer_fichier.py", self.app_state.base_directory, filename, src_lang, tgt_lang]
            if self.script_operations and self.script_operations.runner:
                self.script_operations.runner.run_command(cmd, f"Génération fichier {filename} {src_lang}->{tgt_lang}")

    def _run_generer_manquant(self):
        """Run generate missing files script."""
        if not self._ensure_script_operations():
            return

        if self.app_state.base_directory:
            cmd = ["python", "generer_manquant.py", self.app_state.base_directory]
            if self.script_operations and self.script_operations.runner:
                self.script_operations.runner.run_command(cmd, "Génération des fichiers manquants")

    def _run_check_coherence(self):
        """Run coherence check script."""
        if not self._ensure_script_operations():
            return

        if self.app_state.base_directory:
            cmd = ["python", "check_coherence.py", self.app_state.base_directory]
            if self.script_operations and self.script_operations.runner:
                self.script_operations.runner.run_command_with_fix_option(
                    cmd,
                    self.app_state.base_directory,
                    "Vérification de cohérence"
                )

    def _run_spell_check(self):
        """Run spell check script."""
        if not self._ensure_script_operations():
            return

        if self.app_state.base_directory:
            cmd = ["python", "verifier_orthographe.py", self.app_state.base_directory]
            if self.script_operations and self.script_operations.runner:
                self.script_operations.runner.run_command(cmd, "Vérification orthographique")

    # File selection handling

    def update_selected_file(self, filename: str):
        """Update the selected file display."""
        if self.selected_file_label:
            self.selected_file_label.config(text=f"Fichier sélectionné : {filename}")

        self.sync_one_var.set(filename)
        self.genfichier_file_var.set(filename)
        self.app_state.current_file_path = filename

        logger.info(f"Selected file updated: {filename}")

    def get_app_state(self) -> ApplicationState:
        """Get the current application state."""
        return self.app_state

    def set_tools_enabled(self, enabled: bool):
        """Enable or disable toolbar buttons."""
        if self.tools_frame:
            state = "normal" if enabled else "disabled"

            for widget in self.tools_frame.winfo_children():
                # Skip widgets that don't support state configuration
                try:
                    # Try to configure the state - some widgets support it
                    widget.configure(state=state)  # type: ignore
                except (tk.TclError, TypeError):
                    # Widget doesn't support state option
                    pass

    def cleanup(self):
        """Cleanup resources when closing the application."""
        logger.info("Cleaning up application resources")
        try:
            # Cleanup managers
            if hasattr(self.translation_manager, 'cleanup'):
                self.translation_manager.cleanup()

            # Save any pending state
            # ... additional cleanup as needed

            logger.info("✅ Application cleanup complete")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


def main():
    """Main entry point for the modular Fault Editor application."""
    try:
        print("🚀 Démarrage de l'application Fault Editor - Architecture Modulaire...")

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/app_modular.log'),
                logging.StreamHandler()
            ]
        )

        # Create main window
        root = tk.Tk()

        # Create application controller
        app = FaultEditorController(root)

        # Setup cleanup on window close
        def on_closing():
            app.cleanup()
            root.quit()
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)

        print("✅ Interface utilisateur modulaire initialisée")
        logger.info("Application started successfully")

        # Start main loop
        root.mainloop()

    except Exception as e:
        error_msg = f"❌ Erreur fatale au démarrage : {e}"
        print(error_msg)
        logger.error(error_msg, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
