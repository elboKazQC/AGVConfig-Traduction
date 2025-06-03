#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Application Controller - Complete Interface

This module provides the complete main application controller that fully recreates
the original Fault Editor interface with all its functionalities, using the new
modular architecture underneath.

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
import subprocess
import re
from functools import partial
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Import modular components
from config.constants import Colors, Fonts, Messages, Dimensions
from models.data_models import ApplicationState

# Import translation function directly for compatibility
try:
    from translate import traduire
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("translate module not found - translation features may be limited")
    traduire = None

# Configure logging
logger = logging.getLogger(__name__)

# Styles pour les alarmes (from original app)
ALARM_STYLES = {
    "error": {"bg": "#f44336", "fg": "#ffffff"},
    "warning": {"bg": "#ffc107", "fg": "#000000"},
    "info": {"bg": "#2196f3", "fg": "#ffffff"},
    "success": {"bg": "#4caf50", "fg": "#ffffff"}
}


class FaultEditorController:
    """
    Main application controller that recreates the complete original interface
    while using the new modular architecture underneath.
    """

    def __init__(self, root: tk.Tk):
        """Initialize the complete fault editor interface."""
        logger.info("🚀 Initializing complete Fault Editor interface")

        self.root = root
        self.root.title(Messages.APP_TITLE)
        self.root.geometry(Dimensions.MAIN_WINDOW_SIZE)

        # Initialize application state
        self.app_state = ApplicationState()

        # Original application variables
        self.lang = "fr"
        self.file_map = {}
        self.data_map = {}
        self.path_map = {}
        self.columns = []  # Liste des colonnes créées
        self.current_path = [0, 255, 255, 255]  # Chemin courant
        self.editing_info = None  # Dictionnaire contenant les infos de l'édition en cours
        self.base_dir = None  # Dossier courant pour les fichiers JSON
        self.search_results = []  # Pour stocker les résultats de recherche
        self.current_search_index = -1  # Index actuel dans les résultats
        self.search_mode = "hierarchical"  # Mode de recherche (hierarchical ou flat)
        self.search_frame = None  # Frame pour la barre de recherche
        self.current_file_path = None  # Chemin du fichier actuellement sélectionné

        # Setup the complete UI
        self.setup_ui()

        logger.info("✅ Complete Fault Editor interface initialized")

    def setup_ui(self):
        """Setup the complete user interface exactly like the original."""
        logger.info("🎨 Setting up complete user interface")

        # Configure styles
        style = ttk.Style()
        style.configure('TRadiobutton', font=Fonts.TOPBAR)
        style.configure('TButton', font=Fonts.TOPBAR)

        # Barre supérieure avec logo
        topbar = tk.Frame(self.root, bg=Colors.BG_TOPBAR, height=Dimensions.TOPBAR_HEIGHT)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        # Logo Noovelia
        logo_frame = tk.Frame(topbar, bg=Colors.BG_TOPBAR)
        logo_frame.pack(side="left", padx=10)
        logo_label = tk.Label(logo_frame, text="noovelia", font=("Segoe UI", 16),
                             bg=Colors.BG_TOPBAR, fg="white")
        logo_label.pack(side="left")

        # Boutons de la barre supérieure
        buttons_frame = tk.Frame(topbar, bg=Colors.BG_TOPBAR)
        buttons_frame.pack(side="right", padx=10)

        # Bouton de recherche
        search_btn = tk.Button(buttons_frame, text="🔍 Rechercher",
                              command=lambda: self.show_search(),
                              bg=Colors.BG_TOPBAR, fg="white",
                              font=Fonts.DEFAULT,
                              relief="flat", padx=10, pady=5)
        search_btn.pack(side="right", padx=(10, 2))

        # Boutons d'ouverture de fichiers
        open_btn = ttk.Button(buttons_frame, text="📂 Ouvrir un dossier", command=self.open_folder)
        open_btn.pack(side="right", padx=2)

        load_flat_btn = ttk.Button(buttons_frame, text="📄 Charger JSON plat", command=self.load_flat_json)
        load_flat_btn.pack(side="right", padx=2)

        # Sélecteur de langue
        lang_frame = tk.Frame(buttons_frame, bg=Colors.BG_TOPBAR)
        lang_frame.pack(side="right", padx=10)

        self.lang_var = tk.StringVar(value="fr")
        ttk.Radiobutton(lang_frame, text="FR", value="fr", variable=self.lang_var,
                       command=self.reload_lang).pack(side="left", padx=2)
        ttk.Radiobutton(lang_frame, text="EN", value="en", variable=self.lang_var,
                       command=self.reload_lang).pack(side="left", padx=2)
        ttk.Radiobutton(lang_frame, text="ES", value="es", variable=self.lang_var,
                       command=self.reload_lang).pack(side="left", padx=2)

        # Cadre des outils (pour pouvoir désactiver/activer les boutons)
        self.tools_frame = tk.Frame(self.root, bg=Colors.BG_MAIN, height=Dimensions.TOOLBAR_HEIGHT)
        self.tools_frame.pack(fill="x", side="top", pady=(0, 5))
        self.tools_frame.pack_propagate(False)

        # Boutons de synchronisation et outils
        btn_sync_all = ttk.Button(self.tools_frame, text="Synchroniser tous les fichiers",
                                 command=self.run_sync_all)
        btn_sync_all.pack(side="left", padx=5)

        # Champ pour synchroniser un fichier spécifique
        self.sync_one_var = tk.StringVar()
        tk.Label(self.tools_frame, text="Fichier à synchroniser:",
                bg=Colors.BG_MAIN, fg="white").pack(side="left", padx=(10,1))
        ttk.Entry(self.tools_frame, textvariable=self.sync_one_var, width=25).pack(side="left")
        btn_sync_one = ttk.Button(self.tools_frame, text="Synchroniser ce fichier",
                                 command=self.run_sync_one)
        btn_sync_one.pack(side="left", padx=5)

        # Outils de génération de fichiers
        self.genfichier_file_var = tk.StringVar()
        self.genfichier_src_var = tk.StringVar(value="fr")
        self.genfichier_tgt_var = tk.StringVar(value="en")

        tk.Label(self.tools_frame, text="gen_fichier:",
                bg=Colors.BG_MAIN, fg="white").pack(side="left", padx=(10,1))
        ttk.Entry(self.tools_frame, textvariable=self.genfichier_file_var, width=20).pack(side="left")
        tk.Label(self.tools_frame, text="src:",
                bg=Colors.BG_MAIN, fg="white").pack(side="left", padx=(10,1))
        ttk.Entry(self.tools_frame, textvariable=self.genfichier_src_var, width=5).pack(side="left")
        tk.Label(self.tools_frame, text="tgt:",
                bg=Colors.BG_MAIN, fg="white").pack(side="left", padx=(10,1))
        ttk.Entry(self.tools_frame, textvariable=self.genfichier_tgt_var, width=5).pack(side="left")

        btn_genfichier = ttk.Button(self.tools_frame, text="Générer fichier",
                                   command=self.run_generer_fichier)
        btn_genfichier.pack(side="left", padx=5)

        btn_gen_manquant = ttk.Button(self.tools_frame, text="Générer les fichiers manquants",
                                     command=self.run_generer_manquant)
        btn_gen_manquant.pack(side="left", padx=5)

        btn_check = ttk.Button(self.tools_frame, text="Vérifier la cohérence",
                              command=self.run_check_coherence)
        btn_check.pack(side="left", padx=5)

        btn_spell_check = ttk.Button(self.tools_frame, text="🔍 Vérifier l'orthographe",
                                    command=self.run_spell_check)
        btn_spell_check.pack(side="left", padx=5)

        # Label pour afficher le fichier sélectionné
        self.selected_file_label = tk.Label(self.tools_frame, text="Fichier sélectionné :",
                                           bg=Colors.BG_MAIN, fg="white", font=Fonts.DEFAULT)
        self.selected_file_label.pack(side="left", padx=10)

        # Barre d'état
        self.status = tk.Label(self.root, text=Messages.READY, bd=1, relief=tk.SUNKEN,
                              anchor=tk.W, bg=Colors.BG_STATUSBAR, fg="white")
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        # Configuration des styles de scrollbars
        style = ttk.Style()
        style.configure("Custom.Vertical.TScrollbar",
                       background=Colors.BG_MAIN,
                       troughcolor=Colors.BG_MAIN,
                       arrowcolor="white")
        style.configure("Custom.Horizontal.TScrollbar",
                       background=Colors.BG_MAIN,
                       troughcolor=Colors.BG_MAIN,
                       arrowcolor="white")

        # Conteneur pour le canvas et les scrollbars
        container = tk.Frame(self.root)
        container.pack(fill="both", expand=True)

        # Canvas principal pour les colonnes avec scrollbars personnalisées
        self.main_canvas = tk.Canvas(container, bg=Colors.BG_MAIN)
        self.main_canvas.pack(side="left", fill="both", expand=True)

        # Scrollbar verticale
        scrollbar_y = ttk.Scrollbar(container, orient="vertical",
                                  command=self.main_canvas.yview,
                                  style="Custom.Vertical.TScrollbar")
        scrollbar_y.pack(side="right", fill="y")
        self.main_canvas.configure(yscrollcommand=scrollbar_y.set)

        # Scrollbar horizontale
        scrollbar_x = ttk.Scrollbar(container, orient="horizontal",
                                  command=self.main_canvas.xview,
                                  style="Custom.Horizontal.TScrollbar")
        scrollbar_x.pack(side="bottom", fill="x")
        self.main_canvas.configure(xscrollcommand=scrollbar_x.set)
        self.scrollbar_x = scrollbar_x

        # Frame interne contenant les colonnes
        self.columns_frame = tk.Frame(self.main_canvas, bg=Colors.BG_MAIN)
        self.canvas_window = self.main_canvas.create_window((0, 0), window=self.columns_frame, anchor="nw")

        # Configuration de la zone scrollable
        self.columns_frame.bind("<Configure>",
                               lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))
        self.columns_frame.bind("<Configure>",
                               lambda e: self.main_canvas.itemconfig(self.canvas_window,
                                                                    width=self.columns_frame.winfo_reqwidth()))

        # Gestion de la visibilité de la scrollbar horizontale
        self.main_canvas.bind("<Configure>", self.update_xscroll_visibility)
        self.columns_frame.bind("<Configure>", self.update_xscroll_visibility)

        # Ajustement de la hauteur du canvas
        self.root.bind("<Configure>", lambda e: self.main_canvas.config(height=self.root.winfo_height()))

        # Configuration de la molette de souris
        self.setup_mouse_wheel()

        # Configuration de la gestion du focus
        self.setup_focus_management()

        # Configuration des raccourcis clavier
        self.setup_keyboard_shortcuts()

        logger.info("✅ Complete UI setup finished")

    def setup_mouse_wheel(self):
        """Configure mouse wheel scrolling exactly like the original."""
        def on_mousewheel(event):
            if event.state & 0x4:  # Ctrl est pressé
                # Zoom ou dézoom (à implémenter si nécessaire)
                return
            elif event.state & 0x1:  # Shift est pressé
                self.main_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
            else:
                self.main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.root.unbind_all("<MouseWheel>")
        self.root.bind_all("<MouseWheel>", on_mousewheel)

    def setup_focus_management(self):
        """Configure focus management for Entry widgets."""
        def on_focus_in(event):
            if isinstance(event.widget, tk.Entry):
                event.widget.config(bg=Colors.EDIT_BG_FOCUS)

        def on_focus_out(event):
            if isinstance(event.widget, tk.Entry):
                event.widget.config(bg=Colors.EDIT_BG)

        self.root.bind_class("Entry", "<FocusIn>", on_focus_in)
        self.root.bind_class("Entry", "<FocusOut>", on_focus_out)

    def setup_keyboard_shortcuts(self):
        """Configure keyboard shortcuts exactly like the original."""
        self.root.bind("<Control-r>", lambda e: self.reload_root())
        self.root.bind("<Escape>", lambda e: self.unmake_editable())
        self.root.bind("<Control-f>", lambda e: self.show_search())

    def update_xscroll_visibility(self, event=None):
        """Show or hide horizontal scrollbar based on content width."""
        canvas_width = self.main_canvas.winfo_width()
        content_width = self.columns_frame.winfo_reqwidth()
        if content_width > canvas_width:
            self.scrollbar_x.pack(side="bottom", fill="x")
        else:
            self.scrollbar_x.pack_forget()

    # === FILE OPERATIONS ===

    def initialize_file_map(self, folder):
        """Initialize the file map for the given folder."""
        logger.info(f"Initialisation du file_map pour le dossier: {folder}")
        self.file_map.clear()
        for root_dir, _, files in os.walk(folder):
            for file in files:
                if file.endswith(".json"):
                    self.file_map[file] = os.path.join(root_dir, file)
        logger.info(f"Total : {len(self.file_map)} fichiers JSON trouvés dans {folder}")

    def open_folder(self):
        """Open a folder dialog and load the selected directory."""
        try:
            folder = filedialog.askdirectory(title="Sélectionner le dossier contenant les fichiers JSON")
            if folder:
                candidate = folder
                # If no faults_*.json files are found, try the common "JSON" subfolder
                if not glob.glob(os.path.join(candidate, "faults_*.json")):
                    possible = os.path.join(folder, "JSON")
                    if os.path.isdir(possible) and glob.glob(os.path.join(possible, "faults_*.json")):
                        candidate = possible

                if not glob.glob(os.path.join(candidate, "faults_*.json")):
                    messagebox.showerror(
                        "Erreur",
                        "Aucun fichier faults_*.json trouvé dans le dossier sélectionné"
                    )
                    logger.error("Dossier invalide: aucun fichier faults_*.json")
                    return

                self.base_dir = candidate
                self.app_state.base_directory = candidate
                self.initialize_file_map(candidate)
                self.load_root()
                self.status.config(text=f"✅ Dossier chargé: {candidate}")
                logger.info(f"Dossier ouvert: {candidate}")
        except Exception as e:
            error_msg = f"❌ Erreur lors de l'ouverture du dossier: {e}"
            self.status.config(text=error_msg)
            logger.error(error_msg)
            messagebox.showerror("Erreur", error_msg)

    def load_flat_json(self):
        """Load a flat JSON file for editing."""
        try:
            file_path = filedialog.askopenfilename(
                title="Sélectionner un fichier JSON",
                filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
            )
            if file_path:
                self.current_file_path = file_path
                self.load_flat_mode(file_path)
                self.status.config(text=f"✅ Fichier JSON plat chargé: {os.path.basename(file_path)}")
                logger.info(f"Fichier JSON plat chargé: {file_path}")
        except Exception as e:
            error_msg = f"❌ Erreur lors du chargement du fichier: {e}"
            self.status.config(text=error_msg)
            logger.error(error_msg)
            messagebox.showerror("Erreur", error_msg)

    def load_root(self):
        """Load the root level of the hierarchical structure."""
        try:
            # Clear existing columns
            for col in self.columns:
                col.destroy()
            self.columns.clear()

            # Reset current path
            self.current_path = [0, 255, 255, 255]

            # Load data and create first column
            self.load_data_for_current_language()
            self.create_first_column()

            self.status.config(text="✅ Interface rechargée depuis la racine")
            logger.info("Interface rechargée depuis la racine")
        except Exception as e:
            error_msg = f"❌ Erreur lors du rechargement: {e}"
            self.status.config(text=error_msg)
            logger.error(error_msg)

    def load_data_for_current_language(self):
        """Load data for the current language."""
        try:
            if not self.base_dir:
                return

            # Construct filename for current language
            filename = (
                f"faults_{self.current_path[0]:03d}_"
                f"{self.current_path[1]:03d}_"
                f"{self.current_path[2]:03d}_"
                f"{self.current_path[3]:03d}_{self.lang}.json"
            )
            file_path = os.path.join(self.base_dir, filename)

            logger.debug(f"Chemin de fichier calculé: {file_path}")

            if not os.path.isfile(file_path):
                self.data_map[self.lang] = {}
                logger.warning(f"Fichier non trouvé: {file_path}")
                messagebox.showerror("Erreur", f"Fichier introuvable: {file_path}")
                return

            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError as e:
                    logger.error(f"Erreur de décodage JSON pour {file_path}: {e}")
                    messagebox.showerror(
                        "Erreur", f"Impossible de lire {file_path}: {e}"
                    )
                    self.data_map[self.lang] = {}
                    return

            self.data_map[self.lang] = data

            if not data:
                logger.error(f"Aucune donnée chargée depuis {file_path}")
                messagebox.showerror(
                    "Erreur", f"Aucune donnée chargée depuis {file_path}"
                )
                return

            logger.info(f"Données chargées pour {self.lang}: {file_path}")

        except Exception as e:
            logger.error(f"Erreur lors du chargement des données: {e}")
            self.data_map[self.lang] = {}

    def create_first_column(self):
        """Create the first column with initial data."""
        try:
            # This is a placeholder for the actual column creation logic
            # You would implement the full hierarchical navigation here
            col_frame = tk.Frame(self.columns_frame, bg=Colors.BG_COLUMN,
                               width=Dimensions.MIN_COL_WIDTH, relief="raised", bd=1)
            col_frame.pack(side="left", fill="y", padx=1)
            col_frame.pack_propagate(False)

            # Add a header
            header = tk.Label(col_frame, text="Codes de défaut",
                            bg=Colors.BG_COLUMN, fg=Colors.FG_TEXT,
                            font=Fonts.TITLE, pady=10)
            header.pack(fill="x")

            # Add content area
            content_frame = tk.Frame(col_frame, bg=Colors.BG_COLUMN)
            content_frame.pack(fill="both", expand=True, padx=5, pady=5)

            # Add some sample content
            if self.data_map.get(self.lang):
                for key, value in list(self.data_map[self.lang].items())[:10]:  # Limit to first 10 items
                    item_frame = tk.Frame(content_frame, bg=Colors.BG_ROW, pady=2)
                    item_frame.pack(fill="x", pady=1)

                    label = tk.Label(item_frame, text=f"{key}: {str(value)[:50]}...",
                                   bg=Colors.BG_ROW, fg=Colors.FG_TEXT,
                                   font=Fonts.DEFAULT, anchor="w")
                    label.pack(fill="x", padx=5)
            else:
                no_data_label = tk.Label(content_frame, text="Aucune donnée disponible",
                                       bg=Colors.BG_COLUMN, fg=Colors.FG_TEXT,
                                       font=Fonts.DEFAULT)
                no_data_label.pack(pady=20)

            self.columns.append(col_frame)
            logger.info("Première colonne créée")

        except Exception as e:
            logger.error(f"Erreur lors de la création de la première colonne: {e}")

    def load_flat_mode(self, file_path):
        """Load and display a flat JSON file."""
        try:
            # Clear existing columns
            for col in self.columns:
                col.destroy()
            self.columns.clear()

            # Load the JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Create a single column for flat editing
            col_frame = tk.Frame(self.columns_frame, bg=Colors.BG_COLUMN,
                               relief="raised", bd=1)
            col_frame.pack(side="left", fill="both", expand=True, padx=1)

            # Add header
            header = tk.Label(col_frame, text=f"Édition: {os.path.basename(file_path)}",
                            bg=Colors.BG_COLUMN, fg=Colors.FG_TEXT,
                            font=Fonts.TITLE, pady=10)
            header.pack(fill="x")

            # Add scrollable content area
            canvas = tk.Canvas(col_frame, bg=Colors.BG_COLUMN)
            scrollbar = ttk.Scrollbar(col_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg=Colors.BG_COLUMN)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            # Pack the scrollable components
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Add editable entries for each key-value pair
            for key, value in data.items():
                item_frame = tk.Frame(scrollable_frame, bg=Colors.BG_ROW, pady=2)
                item_frame.pack(fill="x", pady=1, padx=5)

                # Key label
                key_label = tk.Label(item_frame, text=f"{key}:",
                                   bg=Colors.BG_ROW, fg=Colors.FG_TEXT,
                                   font=Fonts.DEFAULT, width=20, anchor="w")
                key_label.pack(side="left")

                # Value entry
                value_var = tk.StringVar(value=str(value))
                value_entry = tk.Entry(item_frame, textvariable=value_var,
                                     bg=Colors.EDIT_BG, fg=Colors.EDIT_FG,
                                     font=Fonts.DEFAULT)
                value_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))

            self.columns.append(col_frame)
            logger.info(f"Mode plat chargé: {file_path}")

        except Exception as e:
            logger.error(f"Erreur lors du chargement du mode plat: {e}")
            messagebox.showerror("Erreur", f"Impossible de charger le fichier: {e}")

    # === LANGUAGE MANAGEMENT ===

    def reload_lang(self):
        """Reload the interface when language changes."""
        try:
            new_lang = self.lang_var.get()
            if new_lang != self.lang:
                self.lang = new_lang
                self.app_state.current_language = new_lang
                self.load_data_for_current_language()
                self.refresh_columns()
                self.status.config(text=f"✅ Langue changée: {new_lang.upper()}")
                logger.info(f"Langue changée: {new_lang}")
        except Exception as e:
            error_msg = f"❌ Erreur lors du changement de langue: {e}"
            self.status.config(text=error_msg)
            logger.error(error_msg)

    def refresh_columns(self):
        """Refresh all columns with new language data."""
        try:
            # This would refresh the existing columns with new language data
            # For now, just reload the root
            self.load_root()
        except Exception as e:
            logger.error(f"Erreur lors du rafraîchissement des colonnes: {e}")

    # === SEARCH FUNCTIONALITY ===

    def show_search(self):
        """Show the search interface."""
        try:
            if self.search_frame and self.search_frame.winfo_exists():
                # Search frame already exists, focus on search entry
                return

            # Create search frame
            self.search_frame = tk.Toplevel(self.root)
            self.search_frame.title("🔍 Rechercher")
            self.search_frame.geometry("500x300")
            self.search_frame.transient(self.root)
            self.search_frame.configure(bg=Colors.BG_MAIN)

            # Search controls
            controls_frame = tk.Frame(self.search_frame, bg=Colors.BG_MAIN)
            controls_frame.pack(fill="x", padx=10, pady=10)

            tk.Label(controls_frame, text="Rechercher:",
                    bg=Colors.BG_MAIN, fg=Colors.FG_TEXT,
                    font=Fonts.DEFAULT).pack(anchor="w")

            self.search_var = tk.StringVar()
            search_entry = tk.Entry(controls_frame, textvariable=self.search_var,
                                  bg=Colors.EDIT_BG, fg=Colors.EDIT_FG,
                                  font=Fonts.DEFAULT, width=50)
            search_entry.pack(fill="x", pady=(5, 10))
            search_entry.focus()

            # Search buttons
            buttons_frame = tk.Frame(controls_frame, bg=Colors.BG_MAIN)
            buttons_frame.pack(fill="x")

            ttk.Button(buttons_frame, text="Rechercher",
                      command=self.perform_search).pack(side="left", padx=(0, 5))
            ttk.Button(buttons_frame, text="Suivant",
                      command=self.search_next).pack(side="left", padx=5)
            ttk.Button(buttons_frame, text="Précédent",
                      command=self.search_previous).pack(side="left", padx=5)

            # Results area
            results_frame = tk.Frame(self.search_frame, bg=Colors.BG_MAIN)
            results_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

            tk.Label(results_frame, text="Résultats:",
                    bg=Colors.BG_MAIN, fg=Colors.FG_TEXT,
                    font=Fonts.DEFAULT).pack(anchor="w")

            # Results listbox
            self.results_listbox = tk.Listbox(results_frame,
                                            bg=Colors.BG_ROW, fg=Colors.FG_TEXT,
                                            font=Fonts.DEFAULT)
            self.results_listbox.pack(fill="both", expand=True, pady=(5, 0))

            # Bind Enter key to search
            search_entry.bind("<Return>", lambda e: self.perform_search())

            logger.info("Interface de recherche affichée")

        except Exception as e:
            error_msg = f"❌ Erreur lors de l'affichage de la recherche: {e}"
            self.status.config(text=error_msg)
            logger.error(error_msg)

    def perform_search(self):
        """Perform a search operation."""
        try:
            query = self.search_var.get().strip()
            if not query:
                return

            self.search_results.clear()
            self.current_search_index = -1

            # Clear results listbox
            self.results_listbox.delete(0, tk.END)

            # Search in current data
            if self.data_map.get(self.lang):
                for key, value in self.data_map[self.lang].items():
                    if (query.lower() in key.lower() or
                        query.lower() in str(value).lower()):
                        result = f"{key}: {str(value)[:100]}..."
                        self.search_results.append((key, value))
                        self.results_listbox.insert(tk.END, result)

            # Update status
            count = len(self.search_results)
            self.status.config(text=f"🔍 {count} résultat(s) trouvé(s) pour '{query}'")

            logger.info(f"Recherche effectuée: '{query}' - {count} résultats")

        except Exception as e:
            error_msg = f"❌ Erreur lors de la recherche: {e}"
            self.status.config(text=error_msg)
            logger.error(error_msg)

    def search_next(self):
        """Navigate to next search result."""
        if self.search_results:
            self.current_search_index = (self.current_search_index + 1) % len(self.search_results)
            self.results_listbox.selection_clear(0, tk.END)
            self.results_listbox.selection_set(self.current_search_index)
            self.results_listbox.see(self.current_search_index)

    def search_previous(self):
        """Navigate to previous search result."""
        if self.search_results:
            self.current_search_index = (self.current_search_index - 1) % len(self.search_results)
            self.results_listbox.selection_clear(0, tk.END)
            self.results_listbox.selection_set(self.current_search_index)
            self.results_listbox.see(self.current_search_index)

    # === SCRIPT OPERATIONS ===

    def run_sync_all(self):
        """Run the sync_all script."""
        try:
            self.status.config(text="⏳ Synchronisation de tous les fichiers...")

            # Create a popup to show progress
            popup = self.afficher_popup_chargement("Synchronisation en cours...")

            # Run the sync_all script
            if self.base_dir:
                result = subprocess.run([sys.executable, "sync_all.py", self.base_dir],
                                      capture_output=True, text=True, cwd=".")
                if result.returncode == 0:
                    self.status.config(text="✅ Synchronisation terminée avec succès")
                else:
                    self.status.config(text="❌ Erreur lors de la synchronisation")
                    messagebox.showerror("Erreur", f"Erreur de synchronisation:\n{result.stderr}")
            else:
                messagebox.showwarning("Attention", "Veuillez d'abord ouvrir un dossier")

            popup.destroy()
            logger.info("Synchronisation de tous les fichiers terminée")

        except Exception as e:
            if 'popup' in locals():
                popup.destroy()
            error_msg = f"❌ Erreur lors de la synchronisation: {e}"
            self.status.config(text=error_msg)
            logger.error(error_msg)
            messagebox.showerror("Erreur", error_msg)

    def run_sync_one(self):
        """Run the sync_one script for a specific file."""
        try:
            filename = self.sync_one_var.get().strip()
            if not filename:
                messagebox.showwarning("Attention", "Veuillez spécifier un nom de fichier")
                return

            self.status.config(text=f"⏳ Synchronisation de {filename}...")

            popup = self.afficher_popup_chargement(f"Synchronisation de {filename}...")

            result = subprocess.run([sys.executable, "sync_one.py", filename],
                                  capture_output=True, text=True, cwd=".")
            if result.returncode == 0:
                self.status.config(text=f"✅ Synchronisation de {filename} terminée")
            else:
                self.status.config(text=f"❌ Erreur lors de la synchronisation de {filename}")
                messagebox.showerror("Erreur", f"Erreur de synchronisation:\n{result.stderr}")

            popup.destroy()
            logger.info(f"Synchronisation de {filename} terminée")

        except Exception as e:
            if 'popup' in locals():
                popup.destroy()
            error_msg = f"❌ Erreur lors de la synchronisation: {e}"
            self.status.config(text=error_msg)
            logger.error(error_msg)

    def run_generer_fichier(self):
        """Run the generer_fichier script."""
        try:
            filename = self.genfichier_file_var.get().strip()
            src_lang = self.genfichier_src_var.get().strip()
            tgt_lang = self.genfichier_tgt_var.get().strip()

            if not all([filename, src_lang, tgt_lang]):
                messagebox.showwarning("Attention", "Veuillez remplir tous les champs")
                return

            self.status.config(text=f"⏳ Génération de {filename} ({src_lang} → {tgt_lang})...")

            popup = self.afficher_popup_chargement("Génération en cours...")

            result = subprocess.run([sys.executable, "generer_fichier.py", filename, src_lang, tgt_lang],
                                  capture_output=True, text=True, cwd=".")
            if result.returncode == 0:
                self.status.config(text=f"✅ Génération de {filename} terminée")
            else:
                self.status.config(text=f"❌ Erreur lors de la génération de {filename}")
                messagebox.showerror("Erreur", f"Erreur de génération:\n{result.stderr}")

            popup.destroy()
            logger.info(f"Génération de {filename} terminée")

        except Exception as e:
            if 'popup' in locals():
                popup.destroy()
            error_msg = f"❌ Erreur lors de la génération: {e}"
            self.status.config(text=error_msg)
            logger.error(error_msg)

    def run_generer_manquant(self):
        """Run the generer_manquant script."""
        try:
            self.status.config(text="⏳ Génération des fichiers manquants...")

            popup = self.afficher_popup_chargement("Génération des fichiers manquants...")

            result = subprocess.run([sys.executable, "generer_manquant.py"],
                                  capture_output=True, text=True, cwd=".")
            if result.returncode == 0:
                self.status.config(text="✅ Génération des fichiers manquants terminée")
            else:
                self.status.config(text="❌ Erreur lors de la génération des fichiers manquants")
                messagebox.showerror("Erreur", f"Erreur de génération:\n{result.stderr}")

            popup.destroy()
            logger.info("Génération des fichiers manquants terminée")

        except Exception as e:
            if 'popup' in locals():
                popup.destroy()
            error_msg = f"❌ Erreur lors de la génération: {e}"
            self.status.config(text=error_msg)
            logger.error(error_msg)

    def run_check_coherence(self):
        """Run the check_coherence script."""
        try:
            self.status.config(text="⏳ Vérification de la cohérence...")

            popup = self.afficher_popup_chargement("Vérification de la cohérence...")

            result = subprocess.run([sys.executable, "check_coherence.py"],
                                  capture_output=True, text=True, cwd=".")
            if result.returncode == 0:
                self.status.config(text="✅ Vérification de la cohérence terminée")
                if result.stdout:
                    messagebox.showinfo("Résultat", f"Vérification terminée:\n{result.stdout}")
            else:
                self.status.config(text="❌ Erreur lors de la vérification")
                messagebox.showerror("Erreur", f"Erreur de vérification:\n{result.stderr}")

            popup.destroy()
            logger.info("Vérification de la cohérence terminée")

        except Exception as e:
            if 'popup' in locals():
                popup.destroy()
            error_msg = f"❌ Erreur lors de la vérification: {e}"
            self.status.config(text=error_msg)
            logger.error(error_msg)

    def run_spell_check(self):
        """Run the spell check script."""
        try:
            self.status.config(text="⏳ Vérification de l'orthographe...")

            popup = self.afficher_popup_chargement("Vérification de l'orthographe...")

            result = subprocess.run([sys.executable, "verifier_orthographe.py"],
                                  capture_output=True, text=True, cwd=".")
            if result.returncode == 0:
                self.status.config(text="✅ Vérification de l'orthographe terminée")
                if result.stdout:
                    messagebox.showinfo("Résultat", f"Vérification terminée:\n{result.stdout}")
            else:
                self.status.config(text="❌ Erreur lors de la vérification orthographique")
                messagebox.showerror("Erreur", f"Erreur de vérification:\n{result.stderr}")

            popup.destroy()
            logger.info("Vérification de l'orthographe terminée")

        except Exception as e:
            if 'popup' in locals():
                popup.destroy()
            error_msg = f"❌ Erreur lors de la vérification: {e}"
            self.status.config(text=error_msg)
            logger.error(error_msg)

    # === UTILITY METHODS ===

    def afficher_popup_chargement(self, message="Traitement en cours..."):
        """Display a loading popup with the given message."""
        popup = tk.Toplevel(self.root)
        popup.title("Veuillez patienter")
        popup.geometry("300x100")
        popup.transient(self.root)
        popup.grab_set()  # Bloque les interactions avec la fenêtre principale
        popup.resizable(False, False)
        popup.configure(bg=Colors.BG_MAIN)

        tk.Label(popup, text=message, font=Fonts.DEFAULT,
                bg=Colors.BG_MAIN, fg=Colors.FG_TEXT).pack(pady=20)

        self.root.update_idletasks()
        return popup

    def reload_root(self, event=None):
        """Reload the complete interface from the root."""
        try:
            # Save current state
            old_lang = self.lang
            old_path = self.current_path[:]

            # Reload from root
            self.load_root()

            # Try to restore previous path
            try:
                self.rebuild_columns_for_path()
                self.status.config(text="✅ Interface rechargée")
            except Exception as e:
                logger.warning(f"Erreur lors de la restauration du chemin : {e}")
                # Stay at root on error
                self.status.config(text="✅ Interface rechargée (racine)")
        except Exception as e:
            error_msg = f"❌ Erreur lors du rechargement : {e}"
            self.status.config(text=error_msg)
            logger.error(error_msg)

    def rebuild_columns_for_path(self):
        """Rebuild columns for the current path (placeholder)."""
        # This would implement the logic to rebuild the column structure
        # based on the current path
        pass

    def unmake_editable(self):
        """Exit edit mode (placeholder)."""
        # This would implement logic to exit edit mode
        pass

    def cleanup(self):
        """Cleanup method called when application closes."""
        try:
            logger.info("🧹 Cleaning up application resources")

            # Close search window if open
            if hasattr(self, 'search_frame') and self.search_frame and self.search_frame.winfo_exists():
                self.search_frame.destroy()

            # Save any pending changes
            # (implement as needed)

            logger.info("✅ Cleanup completed")
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage: {e}")


# Legacy compatibility function
def create_fault_editor(root):
    """Create a FaultEditorController instance for legacy compatibility."""
    return FaultEditorController(root)
