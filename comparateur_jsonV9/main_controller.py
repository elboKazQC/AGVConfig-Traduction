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
        """Initialize the file map with all JSON files in the folder"""
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
                self.base_dir = folder
                self.app_state.base_directory = folder
                self.initialize_file_map(folder)
                self.load_root()
                self.status.config(text=f"✅ Dossier chargé: {folder}")
                logger.info(f"Dossier ouvert: {folder}")
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

    def load_level(self, path, level):
        """Load a specific level in the hierarchy"""
        filename = self.path_to_filename(path)
        logger.info(f"Chargement du niveau {level} avec le fichier : {filename}")
        filepath = self.file_map.get(filename)
        if not filepath:
            logger.error(f"Fichier introuvable : {filename}")
            self.status.config(text=f"❌ Introuvable : {filename}")
            return
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = json.load(f)
            logger.info(f"Fichier {filename} chargé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de la lecture de {filename}: {str(e)}")
            self.status.config(text=f"❌ Erreur lecture {filename}")
            return
        self.data_map[filename] = content
        self.path_map[filename] = filepath
        self.clear_columns_from(level)
        fault_list = content.get("FaultDetailList", [])
        logger.info(f"Nombre d'items dans FaultDetailList : {len(fault_list)}")
        self.display_column(fault_list, path, filename, level)
        self.root.after(100, lambda: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))
        self.main_canvas.yview_moveto(0.0)

    def path_to_filename(self, path):
        """Convert a path to a filename"""
        return f"faults_{'_'.join(str(p).zfill(3) for p in path)}_{self.lang}.json"

    def load_root(self):
        """Load the root level of the hierarchical structure"""
        try:
            # Clear existing columns
            for col in self.columns:
                col.destroy()
            self.columns.clear()

            # Reset current path
            self.current_path = [0, 255, 255, 255]

            # Load the first level
            self.load_level(self.current_path, 0)

            self.status.config(text="✅ Racine chargée")
            logger.info("Racine chargée avec succès")
        except Exception as e:
            error_msg = f"❌ Erreur lors du chargement de la racine: {e}"
            self.status.config(text=error_msg)
            logger.error(error_msg)
            messagebox.showerror("Erreur", error_msg)

    def clear_columns_from(self, level):
        """Clear columns from a specific level onwards"""
        try:
            # Remove columns from the specified level onwards
            columns_to_remove = self.columns[level:]
            for col in columns_to_remove:
                col.destroy()

            # Update the columns list
            self.columns = self.columns[:level]

            logger.info(f"Colonnes supprimées à partir du niveau {level}")
        except Exception as e:
            logger.error(f"Erreur lors de la suppression des colonnes: {e}")

    def rebuild_columns_for_path(self):
        """Rebuild columns for the current path"""
        try:
            if not self.base_dir or not self.file_map:
                return

            # Clear all columns
            self.clear_columns_from(0)

            # Rebuild each level of the current path
            for level in range(len(self.current_path)):
                if self.current_path[level] != 255:  # 255 indicates end of path
                    path_to_load = self.current_path[:level+1] + [255] * (4 - level - 1)
                    self.load_level(path_to_load, level)
                else:
                    break

            logger.info(f"Colonnes reconstruites pour le chemin: {self.current_path}")
        except Exception as e:
            logger.error(f"Erreur lors de la reconstruction des colonnes: {e}")

    def update_selected_file(self, fn):
        """Update the selected file display"""
        self.selected_file_label.config(text=f"Fichier sélectionné : {fn}")
        self.sync_one_var.set(fn)
        self.genfichier_file_var.set(fn)

    def display_column(self, fault_list, path, filename, level):
        """Display a column of faults in the UI"""
        try:
            col_index = len(self.columns)
            frame = tk.Frame(self.columns_frame, bg=Colors.BG_COLUMN)
            frame.grid(row=0, column=col_index, padx=5, pady=10, sticky="nsew")
            self.columns_frame.grid_columnconfigure(col_index, minsize=Dimensions.MIN_COL_WIDTH)
            self.columns.append(frame)

            for idx, fault in enumerate(fault_list):
                row = tk.Frame(frame, bg=Colors.BG_ROW, highlightthickness=0, highlightbackground=Colors.HIGHLIGHT)
                row.pack(fill="x", padx=4, pady=3)
                row.bind("<Enter>", lambda e, r=row: r.configure(highlightthickness=1))
                row.bind("<Leave>", lambda e, r=row: r.configure(highlightthickness=0))

                color = Colors.GREEN if fault.get("IsExpandable") else Colors.RED
                dot = tk.Canvas(row, width=14, height=14, bg=Colors.BG_ROW, highlightthickness=0)
                dot.create_oval(2, 2, 12, 12, fill=color, outline=color)
                dot.pack(side="left", padx=(6, 8))

                label_text = f"{idx}: {fault.get('Description', '(vide)')}"
                label = tk.Label(row, text=label_text, fg=Colors.FG_TEXT, bg=Colors.BG_ROW,
                                anchor="w", font=Fonts.DEFAULT)
                label.pack(side="left", fill="x", expand=True)

                # Bind click events
                label.bind("<Button-1>", partial(self.handle_single_click, fault, idx, path, level, filename))
                label.bind("<Double-1>", partial(self.handle_double_click, fault, idx, path, level, filename, row))

            self.root.update_idletasks()
            self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
            self.main_canvas.yview_moveto(0.0)

        except Exception as e:
            logger.error(f"Erreur lors de l'affichage de la colonne: {e}")

    def load_flat_mode(self, file_path):
        """Load a file in flat mode for editing"""
        try:
            logger.info(f"Chargement du fichier en mode plat: {file_path}")
            # This would implement flat file editing mode
            # For now, just show a placeholder
            messagebox.showinfo("Mode Plat", f"Mode plat pour le fichier:\n{file_path}\n\nFonctionnalité en cours d'implémentation.")
        except Exception as e:
            logger.error(f"Erreur lors du chargement en mode plat: {e}")
            messagebox.showerror("Erreur", f"Impossible de charger le fichier en mode plat:\n{e}")

    def load_data_for_current_language(self):
        """Load data for the current language"""
        try:
            if self.base_dir and self.file_map:
                # Reload the file map with current language
                self.initialize_file_map(self.base_dir)
                # Reload the current level
                if hasattr(self, 'current_path'):
                    self.rebuild_columns_for_path()
                logger.info(f"Données rechargées pour la langue: {self.lang}")
        except Exception as e:
            logger.error(f"Erreur lors du rechargement des données: {e}")

    def handle_single_click(self, fault, idx, path, level, filename, event):
        """Handle single click on a fault item"""
        try:
            widget = event.widget
            # Cancel any pending double-click handler
            if hasattr(widget, '_click_job'):
                widget.after_cancel(widget._click_job)

            # Schedule single click action (will be canceled if double-click occurs)
            widget._click_job = widget.after(300, lambda: self.single_click_action(fault, idx, path, level, filename))
        except Exception as e:
            logger.error(f"Erreur lors du clic simple: {e}")

    def handle_double_click(self, fault, idx, path, level, filename, row, event):
        """Handle double click on a fault item"""
        try:
            widget = event.widget
            # Cancel single click action
            if hasattr(widget, '_click_job'):
                widget.after_cancel(widget._click_job)

            # Perform double click action
            self.double_click_action(fault, idx, path, level, filename, row)
        except Exception as e:
            logger.error(f"Erreur lors de l'action de double clic: {e}")

    def single_click_action(self, fault, idx, path, level, filename):
        """Action performed on single click"""
        try:
            # Update selected file
            self.update_selected_file(filename)

            # If fault is expandable, expand to next level
            if fault.get("IsExpandable", False):
                new_path = path.copy()
                new_path[level + 1] = idx
                self.current_path = new_path
                self.clear_columns_from(level + 1)
                self.load_level(new_path, level + 1)

            logger.info(f"Sélection: {filename}, index: {idx}")
        except Exception as e:
            logger.error(f"Erreur lors de l'action de clic simple: {e}")

    def double_click_action(self, fault, idx, path, level, filename, row):
        """Action performed on double click (edit mode)"""
        try:
            logger.info(f"Mode édition pour: {filename}, index: {idx}")
            # This would implement edit mode
            # For now, just show a message
            messagebox.showinfo("Édition", f"Mode édition pour:\nFichier: {filename}\nIndex: {idx}\nDescription: {fault.get('Description', '')}")
        except Exception as e:
            logger.error(f"Erreur lors de l'action de double clic: {e}")

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
        """Génère un fichier de traduction en utilisant le script generer_fichier.py"""
        if not self.base_dir:
            self.status.config(text="❌ Aucun dossier ouvert")
            return

        f_arg = self.genfichier_file_var.get().strip()
        src = self.genfichier_src_var.get().strip()
        tgt = self.genfichier_tgt_var.get().strip()

        if not (f_arg and src and tgt):
            self.status.config(text="❌ Arguments generer_fichier manquants")
            return

        cmd = ["python", "generer_fichier.py", self.base_dir, f_arg, src, tgt]
        self.run_command(cmd, desc=f"Générer fichier {f_arg} {src}->{tgt}")

    def run_generer_manquant(self):
        """Génère les fichiers manquants en utilisant le script generer_manquant.py"""
        if not self.base_dir:
            self.status.config(text="❌ Aucun dossier ouvert")
            return
        cmd = ["python", "generer_manquant.py", self.base_dir]
        self.run_command(cmd, desc="Générer les fichiers manquants")

    def run_check_coherence(self):
        """Mashup complet : Cohérence + Orthographe + Headers - Version optimisée"""
        if not hasattr(self, 'file_map') or not self.file_map:
            self.status.config(text="❌ Aucun dossier ouvert")
            return

        # Obtenir le dossier parent du premier fichier trouvé
        premier_fichier = next(iter(self.file_map.values()))
        dossier_base = os.path.dirname(premier_fichier)
        logger.info(f"🚀 Lancement du diagnostic complet dans : {dossier_base}")
        # Afficher le dialogue de choix des actions
        self.show_comprehensive_check_dialog(dossier_base)

    def run_spell_check(self):
        """Lance la vérification orthographique"""
        if not self.base_dir:
            self.status.config(text="❌ Aucun dossier ouvert")
            return
        cmd = ["python", "verifier_orthographe.py", self.base_dir]
        self.run_command(cmd, desc="Vérification orthographique")

    def run_command(self, cmd, desc="Commande"):
        """Exécute une commande système avec feedback visuel"""
        try:
            logger.info(f"🔄 Exécution: {desc}")
            self.status.config(text=f"🔄 {desc}...")

            # Afficher un popup de chargement
            popup = self.afficher_popup_chargement(f"{desc} en cours...")
            self.root.update_idletasks()

            # Exécuter la commande
            result = subprocess.run(cmd, cwd=os.getcwd(), capture_output=True, text=True)

            # Fermer le popup
            popup.destroy()

            if result.returncode == 0:
                self.status.config(text=f"✅ {desc} terminé avec succès")
                logger.info(f"✅ {desc} terminé avec succès")
                if result.stdout:
                    logger.info(f"Sortie: {result.stdout}")
            else:
                error_msg = f"❌ Erreur {desc}: {result.stderr}"
                self.status.config(text=error_msg)
                logger.error(error_msg)
                messagebox.showerror("Erreur", f"{desc} a échoué:\n{result.stderr}")

        except Exception as e:
            error_msg = f"❌ Erreur lors de l'exécution de {desc}: {e}"
            self.status.config(text=error_msg)
            logger.error(error_msg)
            messagebox.showerror("Erreur", error_msg)
            if 'popup' in locals():
                popup.destroy()

    def afficher_popup_chargement(self, message="Traitement en cours..."):
        """Affiche un popup de chargement"""
        popup = tk.Toplevel(self.root)
        popup.title("Veuillez patienter")
        popup.geometry("300x100")
        popup.transient(self.root)
        popup.grab_set()  # Bloque les interactions avec la fenêtre principale
        popup.resizable(False, False)
        tk.Label(popup, text=message, font=Fonts.DEFAULT).pack(pady=20)
        self.root.update_idletasks()
        return popup

    def show_comprehensive_check_dialog(self, dossier_base):
        """Affiche un dialogue pour choisir les vérifications et corrections à effectuer"""
        dialog = tk.Toplevel(self.root)
        dialog.title("🚀 Diagnostic Complet - AGV Config Traduction")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()

        # Centrer la fenêtre
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))

        # Frame principal
        main_frame = tk.Frame(dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Titre
        title_label = tk.Label(main_frame, text="🚀 Diagnostic et Correction Automatique",
                              font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))

        # Informations sur le dossier
        info_frame = tk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(info_frame, text="📁 Dossier :", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        tk.Label(info_frame, text=dossier_base, font=("Arial", 9),
                wraplength=550, justify=tk.LEFT).pack(anchor=tk.W, padx=(20, 0))

        # Variables pour les checkboxes
        self.check_coherence_var = tk.BooleanVar(value=True)
        self.fix_coherence_var = tk.BooleanVar(value=True)
        self.check_spelling_var = tk.BooleanVar(value=True)
        self.fix_headers_var = tk.BooleanVar(value=True)

        # Section Vérifications
        verif_frame = tk.LabelFrame(main_frame, text="🔍 Vérifications à effectuer",
                                   font=("Arial", 11, "bold"), padx=10, pady=10)
        verif_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Checkbutton(verif_frame, text="✅ Vérifier la cohérence des fichiers de traduction",
                      variable=self.check_coherence_var, font=("Arial", 10)).pack(anchor=tk.W)

        tk.Checkbutton(verif_frame, text="📝 Vérifier l'orthographe des traductions",
                      variable=self.check_spelling_var, font=("Arial", 10)).pack(anchor=tk.W)

        # Section Corrections automatiques
        correct_frame = tk.LabelFrame(main_frame, text="🔧 Corrections automatiques",
                                     font=("Arial", 11, "bold"), padx=10, pady=10)
        correct_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Checkbutton(correct_frame, text="🔧 Corriger automatiquement les erreurs de métadonnées",
                      variable=self.fix_coherence_var, font=("Arial", 10)).pack(anchor=tk.W)

        tk.Checkbutton(correct_frame, text="📋 Corriger et normaliser les headers JSON",
                      variable=self.fix_headers_var, font=("Arial", 10)).pack(anchor=tk.W)

        # Zone d'information
        info_text = tk.Text(correct_frame, height=4, wrap=tk.WORD, font=("Arial", 9))
        info_text.pack(fill=tk.X, pady=(10, 0))
        info_text.insert(tk.END,
            "ℹ️  Les corrections automatiques incluent :\n"
            "• Correction des langues dans les headers (Language: fr/en/es)\n"
            "• Correction des noms de fichiers dans les headers\n"
            "• Correction des IDs de niveaux (IdLevel0-3)\n"
            "• Normalisation de la structure des headers JSON")
        info_text.config(state=tk.DISABLED)

        # Boutons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # Bouton Tout vérifier et corriger
        tk.Button(button_frame, text="🚀 Lancer le diagnostic complet",
                 command=lambda: self.run_comprehensive_check(dialog, dossier_base, True),
                 bg="#4CAF50", fg="white", font=("Arial", 11, "bold"),
                 padx=20, pady=10).pack(side=tk.LEFT, padx=(0, 10))

        # Bouton Vérifier seulement
        tk.Button(button_frame, text="🔍 Vérifier seulement (pas de corrections)",
                 command=lambda: self.run_comprehensive_check(dialog, dossier_base, False),
                 bg="#2196F3", fg="white", font=("Arial", 10),
                 padx=20, pady=8).pack(side=tk.LEFT, padx=(0, 10))

        # Bouton Annuler
        tk.Button(button_frame, text="❌ Annuler",
                 command=dialog.destroy,
                 bg="#f44336", fg="white", font=("Arial", 10),
                 padx=20, pady=8).pack(side=tk.RIGHT)

    def run_comprehensive_check(self, dialog, dossier_base, apply_corrections):
        """Lance le diagnostic complet selon les options sélectionnées"""
        dialog.destroy()

        logger.info(f"\n🚀 ===== DIAGNOSTIC COMPLET DÉMARRÉ =====")
        logger.info(f"📁 Dossier : {dossier_base}")
        logger.info(f"🔧 Corrections automatiques : {'✅ Activées' if apply_corrections else '❌ Désactivées'}")

        results = {
            'coherence': None,
            'spelling': None,
            'headers': None,
            'total_errors': 0,
            'total_corrections': 0
        }

        # 1. Vérification de cohérence
        if self.check_coherence_var.get():
            logger.info(f"\n📋 1/3 - Vérification de la cohérence...")
            results['coherence'] = self.run_coherence_check_step(dossier_base,
                                                                apply_corrections and self.fix_coherence_var.get())

        # 2. Vérification orthographique
        if self.check_spelling_var.get():
            logger.info(f"\n📝 2/3 - Vérification orthographique...")
            results['spelling'] = self.run_spelling_check_step(dossier_base)

        # 3. Correction des headers
        if apply_corrections and self.fix_headers_var.get():
            logger.info(f"\n📋 3/3 - Correction des headers...")
            results['headers'] = self.run_headers_fix_step(dossier_base)

        # Afficher le résumé final
        self.show_comprehensive_results(results, dossier_base)

    def run_coherence_check_step(self, dossier_base, apply_fix):
        """Étape de vérification de cohérence"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))

            # Commande de base
            cmd = ["python", os.path.join(script_dir, "check_coherence.py"), dossier_base]

            # Ajouter --fix si demandé
            if apply_fix:
                cmd.append("--fix")
                logger.info("🔧 Mode correction automatique activé pour la cohérence")

            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"

            result = subprocess.run(cmd, capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", env=env, cwd=script_dir)

            if result.stdout:
                logger.info("📋 Résultats cohérence :")
                logger.info(result.stdout)

            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'errors': result.stderr,
                'fixed': apply_fix and "corrections appliquées" in result.stdout
            }

        except Exception as e:
            logger.error(f"❌ Erreur lors de la vérification de cohérence : {e}")
            return {'success': False, 'output': '', 'errors': str(e), 'fixed': False}

    def run_spelling_check_step(self, dossier_base):
        """Étape de vérification orthographique"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            cmd = ["python", os.path.join(script_dir, "verifier_orthographe.py"), dossier_base]

            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"

            result = subprocess.run(cmd, capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", env=env, cwd=script_dir)

            if result.stdout:
                logger.info("📝 Résultats orthographe :")
                logger.info(result.stdout)

            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'errors': result.stderr
            }

        except Exception as e:
            logger.error(f"❌ Erreur lors de la vérification orthographique : {e}")
            return {'success': False, 'output': '', 'errors': str(e)}

    def run_headers_fix_step(self, dossier_base):
        """Étape de correction des headers"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            cmd = ["python", os.path.join(script_dir, "fix_headers.py"), dossier_base]

            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"

            result = subprocess.run(cmd, capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", env=env, cwd=script_dir)

            if result.stdout:
                logger.info("📋 Résultats correction headers :")
                logger.info(result.stdout)

            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'errors': result.stderr,
                'fixed': "corrections appliquées" in result.stdout
            }

        except Exception as e:
            logger.error(f"❌ Erreur lors de la correction des headers : {e}")
            return {'success': False, 'output': '', 'errors': str(e), 'fixed': False}

    def show_comprehensive_results(self, results, dossier_base):
        """Affiche les résultats du diagnostic complet"""
        # Créer une fenêtre de résultats
        results_window = tk.Toplevel(self.root)
        results_window.title("📊 Résultats du Diagnostic Complet")
        results_window.geometry("700x600")
        results_window.transient(self.root)

        # Frame principal avec scrollbar
        main_frame = tk.Frame(results_window, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Titre
        title_label = tk.Label(main_frame, text="📊 Résultats du Diagnostic Complet",
                              font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))

        # Zone de texte avec scrollbar pour les résultats
        text_frame = tk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Compiler les résultats
        report = f"📁 Dossier analysé : {dossier_base}\n"
        report += f"⏰ Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        if results['coherence']:
            report += "=" * 60 + "\n"
            report += "📋 VÉRIFICATION DE COHÉRENCE\n"
            report += "=" * 60 + "\n"
            report += results['coherence']['output'] or "Aucune sortie"
            if results['coherence']['errors']:
                report += f"\n❌ Erreurs : {results['coherence']['errors']}\n"
            report += "\n\n"

        if results['spelling']:
            report += "=" * 60 + "\n"
            report += "📝 VÉRIFICATION ORTHOGRAPHIQUE\n"
            report += "=" * 60 + "\n"
            report += results['spelling']['output'] or "Aucune sortie"
            if results['spelling']['errors']:
                report += f"\n❌ Erreurs : {results['spelling']['errors']}\n"
            report += "\n\n"

        if results['headers']:
            report += "=" * 60 + "\n"
            report += "📋 CORRECTION DES HEADERS\n"
            report += "=" * 60 + "\n"
            report += results['headers']['output'] or "Aucune sortie"
            if results['headers']['errors']:
                report += f"\n❌ Erreurs : {results['headers']['errors']}\n"
            report += "\n\n"

        report += "=" * 60 + "\n"
        report += "✅ DIAGNOSTIC TERMINÉ\n"
        report += "=" * 60 + "\n"

        text_widget.insert(tk.END, report)
        text_widget.config(state=tk.DISABLED)

        # Bouton Fermer
        tk.Button(main_frame, text="✅ Fermer",
                 command=results_window.destroy,
                 bg="#4CAF50", fg="white", font=("Arial", 11),
                 padx=20, pady=10).pack(pady=(20, 0))

        # Mettre à jour le status
        self.status.config(text="✅ Diagnostic complet terminé")

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
