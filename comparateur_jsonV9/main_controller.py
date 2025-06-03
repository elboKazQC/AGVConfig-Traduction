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

        # Add missing attributes
        self.file_manager = None  # File manager instance

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
                logger.info("Interface rechargée avec succès")
            except Exception as e:
                logger.warning(f"Erreur lors de la restauration du chemin : {e}")
                # Stay at root on error
                self.status.config(text="✅ Interface rechargée (racine)")
        except Exception as e:
            error_msg = f"❌ Erreur lors du rechargement : {e}"
            self.status.config(text=error_msg)
            logger.error(error_msg)

    def display_column(self, fault_list, path, filename, level):
        """Display a column of fault data in the interface."""
        try:
            # Create column frame
            col_frame = tk.Frame(self.columns_frame, bg=Colors.BG_COLUMN,
                               relief="raised", bd=1, width=300)
            col_frame.pack(side="left", fill="both", expand=False, padx=1)
            col_frame.pack_propagate(False)

            # Column header
            header = tk.Label(col_frame, text=f"{filename} ({len(fault_list)} items)",
                            bg=Colors.BG_TOPBAR, fg="white",
                            font=Fonts.TITLE, pady=5)
            header.pack(fill="x")

            # Scrollable content
            canvas = tk.Canvas(col_frame, bg=Colors.BG_COLUMN, highlightthickness=0)
            scrollbar = ttk.Scrollbar(col_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg=Colors.BG_COLUMN)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Display fault items
            for i, fault in enumerate(fault_list):
                row = tk.Frame(scrollable_frame, bg=Colors.BG_ROW if i % 2 == 0 else Colors.BG_ROW_ALT)
                row.pack(fill="x", pady=1, padx=2)

                self.render_row(row, fault, i, path, level, filename)

            self.columns.append(col_frame)
            logger.info(f"Colonne affichée: {filename} avec {len(fault_list)} éléments")

        except Exception as e:
            logger.error(f"Erreur lors de l'affichage de la colonne: {e}")
            self.status.config(text=f"❌ Erreur affichage colonne: {e}")

    def render_row(self, row, fault, idx, path, level, filename):
        """Render a row in readonly mode."""
        try:
            # Clear existing widgets
            for widget in row.winfo_children():
                widget.destroy()

            # Get display text
            if isinstance(fault, dict):
                display_text = fault.get("Description", fault.get("Name", f"Item {idx}"))
                fault_code = fault.get("FaultCode", "")
                if fault_code:
                    display_text = f"[{fault_code}] {display_text}"
            else:
                display_text = str(fault)

            # Create main label
            label = tk.Label(row, text=display_text[:100],
                           bg=row['bg'], fg=Colors.FG_TEXT,
                           font=Fonts.DEFAULT, anchor="w")
            label.pack(side="left", fill="x", expand=True, padx=5)

            # Bind click events
            def on_single_click(event):
                self.single_click_action(fault, idx, path, level, filename)

            def on_double_click(event):
                self.handle_double_click(fault, idx, path, level, filename, row, event)

            label.bind("<Button-1>", on_single_click)
            label.bind("<Double-1>", on_double_click)
            row.bind("<Button-1>", on_single_click)
            row.bind("<Double-1>", on_double_click)

        except Exception as e:
            logger.error(f"Erreur lors du rendu de la ligne: {e}")

    def single_click_action(self, fault, idx, path, level, filename):
        """Handle single click on a fault item."""
        try:
            logger.info(f"Single click sur l'item {idx} dans {filename}")
            # Update selection or perform single click action
            self.update_selected_file(filename)
        except Exception as e:
            logger.error(f"Erreur single click: {e}")

    def handle_double_click(self, fault, idx, path, level, filename, row, event):
        """Handle double click on a fault item."""
        try:
            logger.info(f"Double click sur l'item {idx} dans {filename}")
            # Make editable or navigate deeper
            if isinstance(fault, dict):
                # Check if this is a navigable item or editable item
                if "FaultDetailList" in fault:
                    # Navigate deeper
                    new_path = path + [fault.get("FaultCode", idx)]
                    self.load_level(new_path, level + 1)
                else:
                    # Make editable
                    self.make_editable(row, fault, idx, filename, path, level)
        except Exception as e:
            logger.error(f"Erreur double click: {e}")

    def make_editable(self, row, fault, idx, filename, path, level):
        """Make a row editable for fault modification."""
        try:
            # Store editing info
            self.editing_info = {
                "row": row,
                "fault": fault,
                "idx": idx,
                "filename": filename,
                "path": path,
                "level": level
            }

            # Clear existing widgets
            for widget in row.winfo_children():
                widget.destroy()

            # Create editable fields
            if isinstance(fault, dict):
                # Create entry for description
                desc_var = tk.StringVar(value=fault.get("Description", ""))
                desc_entry = tk.Entry(row, textvariable=desc_var,
                                    bg=Colors.EDIT_BG, fg=Colors.EDIT_FG,
                                    font=Fonts.DEFAULT)
                desc_entry.pack(side="left", fill="x", expand=True, padx=2)
                desc_entry.focus()                # Save button
                def save_changes():
                    fault["Description"] = desc_var.get()
                    self.save_file(filename)
                    self.unmake_editable()

                save_btn = tk.Button(row, text="💾", command=save_changes,
                                   bg=Colors.GREEN, fg=Colors.FG_TEXT,
                                   font=Fonts.DEFAULT)
                save_btn.pack(side="right", padx=2)

                # Cancel button
                cancel_btn = tk.Button(row, text="❌", command=self.unmake_editable,
                                     bg=Colors.RED, fg=Colors.FG_TEXT,
                                     font=Fonts.DEFAULT)
                cancel_btn.pack(side="right", padx=2)

                logger.info(f"Row {idx} made editable")

        except Exception as e:
            logger.error(f"Erreur make_editable: {e}")

    def save_file(self, filename):
        """Save changes to a JSON file."""
        try:
            if filename in self.data_map and filename in self.path_map:
                filepath = self.path_map[filename]
                content = self.data_map[filename]

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(content, f, ensure_ascii=False, indent=2)

                logger.info(f"Fichier sauvegardé: {filename}")
                self.status.config(text=f"✅ Sauvegardé: {filename}")
            else:
                logger.error(f"Fichier non trouvé dans les maps: {filename}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde: {e}")
            self.status.config(text=f"❌ Erreur sauvegarde: {e}")

    def update_selected_file(self, filename):
        """Update the selected file display."""
        try:
            if hasattr(self, 'selected_file_label') and self.selected_file_label:
                self.selected_file_label.config(text=f"Fichier sélectionné: {filename}")
                logger.debug(f"Fichier sélectionné mis à jour: {filename}")
        except Exception as e:
            logger.error(f"Erreur update_selected_file: {e}")

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
        """Rebuild columns for the current path (placeholder)."""
        # This would implement the logic to rebuild the column structure
        # based on the current path
        pass

    def unmake_editable(self):
        """Exit edit mode and restore row to readonly mode."""
        if not self.editing_info:
            return

        row = self.editing_info["row"]
        fault = self.editing_info["fault"]
        idx = self.editing_info["idx"]
        filename = self.editing_info["filename"]
        path = self.editing_info["path"]
        level = self.editing_info["level"]

        try:
            # Check if the widget still exists before trying to render it
            row.winfo_exists()
            self.render_row(row, fault, idx, path, level, filename)
            logger.info(f"🔙 Mode édition quitté pour l'item {idx} dans {filename}")
        except tk.TclError:
            # Widget has been destroyed (e.g., during language change), just clear the editing info
            logger.debug("Widget détruit pendant l'édition, nettoyage des infos d'édition")
            pass
        except Exception as e:
            logger.error(f"Erreur lors de l'édition: {e}")

        self.editing_info = None

    def load_flat_mode(self, file_path):
        """Load and display a flat JSON file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = json.load(f)
            logger.info(f"Fichier JSON plat chargé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du fichier JSON plat: {str(e)}")
            self.status.config(text=f"❌ Erreur lecture {file_path}")
            return

        self.data_map[file_path] = content
        self.path_map[file_path] = file_path
        self.clear_columns_from(0)

        # Affichage des données dans un tableau
        fault_list = content.get("FaultDetailList", [])
        logger.info(f"Nombre d'items dans FaultDetailList (mode plat) : {len(fault_list)}")
        self.display_flat_table(fault_list, file_path)

        self.root.after(100, lambda: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))
        self.main_canvas.yview_moveto(0.0)

    def reload_lang(self):
        """Reload the interface when language changes."""
        new_lang = self.lang_var.get()
        if new_lang == self.lang:
            return

        logger.info(f"🔄 Changement de langue: {self.lang} -> {new_lang}")
        self.lang = new_lang

        # Mettre à jour les textes des boutons et labels
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Button) or isinstance(widget, tk.Label):
                text = widget.cget("text")
                translated = self.translate_text(text, new_lang)
                widget.config(text=translated)

        # Recharger les données si un dossier est déjà ouvert
        if self.base_dir:
            self.initialize_file_map(self.base_dir)
            self.load_root()

        self.status.config(text=f"🌐 Langue changée en {new_lang.upper()}")
        logger.info(f"Langue changée en {new_lang.upper()}")

    def translate_text(self, text, target_lang):
        """Translate text to the target language using the traduire function."""
        if traduire:
            try:
                translated = traduire(text, target_lang=target_lang)
                logger.info(f"Texte traduit ({target_lang}): {translated}")
                return translated
            except Exception as e:
                logger.error(f"Erreur lors de la traduction: {e}")
        return text  # Return original text if translation fails

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

    def close_search_frame(self):
        """Safely close the search frame if it exists."""
        if self.search_frame and self.search_frame.winfo_exists():
            self.search_frame.destroy()
            self.search_frame = None

    def open_alarm_detail(self, fault, path):
        """Stub for open_alarm_detail method."""
        logger.warning("open_alarm_detail is not implemented yet.")

    def display_flat_table(self, fault_list, file_path):
        """Stub for display_flat_table method."""
        logger.warning("display_flat_table is not implemented yet.")

    def perform_search(self):
        """Perform the search based on the search mode (hierarchical or flat)."""
        query = self.search_var.get().strip()
        if not query:
            return

        logger.info(f"🔍 Recherche lancée: '{query}' (mode: {self.search_mode})")
        results = []
        if self.search_mode == "hierarchical":
            # Recherche hiérarchique dans les données
            for path, content in self.data_map.items():
                fault_list = content.get("FaultDetailList", [])
                for fault in fault_list:
                    if self.matches_query(fault, query):
                        results.append((path, fault))

        else:
            # Recherche dans les fichiers JSON à plat
            for filename, filepath in self.file_map.items():
                if re.search(query, filename, re.IGNORECASE):
                    results.append((filepath, None))

        self.show_search_results(results)

    def matches_query(self, fault, query):
        """Check if the fault matches the query (case-insensitive)."""
        query = query.lower()
        for key, value in fault.items():
            if isinstance(value, str) and query in value.lower():
                return True
        return False

    def show_search_results(self, results):
        """Display the search results in the search results box."""
        self.results_listbox.delete(0, tk.END)
        self.search_results = results

        for path, fault in results:
            if fault:
                # Résultat détaillé avec chemin
                self.results_listbox.insert(tk.END, f"{path} - {fault.get('FaultName', '')}")
            else:
                # Résultat de fichier
                self.results_listbox.insert(tk.END, f"{path}")

    def open_selected_result(self):
        """Open the selected search result."""
        try:
            selection = self.results_listbox.curselection()
            if not selection:
                return

            index = selection[0]
            path, fault = self.search_results[index]

            if fault:
                # Ouvrir le détail de l'alarme
                self.open_alarm_detail(fault, path)
            else:
                # Ouvrir le fichier JSON
                self.current_file_path = path
                self.load_flat_mode(path)

            self.close_search_frame()
        except Exception as e:
            logger.error(f"Erreur lors de l'ouverture du résultat: {e}")

    def search_next(self):
        """Navigate to the next search result."""
        if self.search_results:
            self.current_search_index = (self.current_search_index + 1) % len(self.search_results)
            self.results_listbox.selection_clear(0, tk.END)
            self.results_listbox.selection_set(self.current_search_index)
            self.results_listbox.see(self.current_search_index)

    def search_previous(self):
        """Navigate to the previous search result."""
        if self.search_results:
            self.current_search_index = (self.current_search_index - 1) % len(self.search_results)
            self.results_listbox.selection_clear(0, tk.END)
            self.results_listbox.selection_set(self.current_search_index)
            self.results_listbox.see(self.current_search_index)

    def run_sync_all(self):
        """Run the sync_all script."""
        logger.info("🔄 Synchronisation de tous les fichiers")
        if not self.base_dir:
            messagebox.showerror("Erreur", "Aucun dossier ouvert")
            return

        # Appel du script sync_all.py
        try:
            result = subprocess.run([sys.executable, "scripts/sync_all.py", self.base_dir],
                                   check=True, text=True, capture_output=True)
            output = result.stdout.strip()
            logger.info(f"Résultat de la synchronisation: {output}")
            messagebox.showinfo("Synchronisation terminée", output)
        except subprocess.CalledProcessError as e:
            logger.error(f"Erreur lors de la synchronisation: {e}")
            messagebox.showerror("Erreur", f"Erreur lors de la synchronisation: {e}")

    def run_sync_one(self):
        """Run the sync_one script for a specific file."""
        logger.info("🔄 Synchronisation d'un fichier spécifique")
        file_to_sync = self.sync_one_var.get().strip()
        if not file_to_sync or file_to_sync not in self.file_map:
            messagebox.showerror("Erreur", "Fichier invalide ou non trouvé")
            return

        file_path = self.file_map[file_to_sync]

        # Appel du script sync_one.py
        try:
            result = subprocess.run([sys.executable, "scripts/sync_one.py", file_path],
                                   check=True, text=True, capture_output=True)
            output = result.stdout.strip()
            logger.info(f"Résultat de la synchronisation: {output}")
            messagebox.showinfo("Synchronisation terminée", output)
        except subprocess.CalledProcessError as e:
            logger.error(f"Erreur lors de la synchronisation: {e}")
            messagebox.showerror("Erreur", f"Erreur lors de la synchronisation: {e}")

    def run_generer_fichier(self):
        """Run the generer_fichier script."""
        logger.info("📂 Génération d'un fichier")
        file_to_generate = self.genfichier_file_var.get().strip()
        src_lang = self.genfichier_src_var.get().strip()
        tgt_lang = self.genfichier_tgt_var.get().strip()

        if not file_to_generate or not src_lang or not tgt_lang:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
            return

        # Appel du script generer_fichier.py
        try:
            result = subprocess.run([sys.executable, "scripts/generer_fichier.py",
                                   file_to_generate, src_lang, tgt_lang],
                                   check=True, text=True, capture_output=True)
            output = result.stdout.strip()
            logger.info(f"Fichier généré avec succès: {output}")
            messagebox.showinfo("Génération terminée", f"Fichier généré: {output}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Erreur lors de la génération du fichier: {e}")
            messagebox.showerror("Erreur", f"Erreur lors de la génération du fichier: {e}")

    def run_generer_manquant(self):
        """Run the generer_manquant script."""
        logger.info("📂 Génération des fichiers manquants")
        # Appel du script generer_manquant.py
        try:
            result = subprocess.run([sys.executable, "scripts/generer_manquant.py"],
                                   check=True, text=True, capture_output=True)
            output = result.stdout.strip()
            logger.info(f"Fichiers manquants générés avec succès")
            messagebox.showinfo("Génération terminée", "Fichiers manquants générés")
        except subprocess.CalledProcessError as e:
            logger.error(f"Erreur lors de la génération des fichiers manquants: {e}")
            messagebox.showerror("Erreur", f"Erreur lors de la génération des fichiers manquants: {e}")

    def run_check_coherence(self):
        """Run the check_coherence script."""
        logger.info("✅ Vérification de la cohérence des fichiers")
        # Appel du script check_coherence.py
        try:
            result = subprocess.run([sys.executable, "scripts/check_coherence.py"],
                                   check=True, text=True, capture_output=True)
            output = result.stdout.strip()
            logger.info(f"Vérification de la cohérence terminée: {output}")
            messagebox.showinfo("Vérification terminée", output)
        except subprocess.CalledProcessError as e:
            logger.error(f"Erreur lors de la vérification de la cohérence: {e}")
            messagebox.showerror("Erreur", f"Erreur lors de la vérification de la cohérence: {e}")

    def run_spell_check(self):
        """Run the spell check script."""
        logger.info("🔍 Vérification de l'orthographe")
        # Appel du script spell_check.py
        try:
            result = subprocess.run([sys.executable, "scripts/spell_check.py"],
                                   check=True, text=True, capture_output=True)
            output = result.stdout.strip()
            logger.info(f"Vérification de l'orthographe terminée: {output}")
            messagebox.showinfo("Vérification terminée", output)
        except subprocess.CalledProcessError as e:
            logger.error(f"Erreur lors de la vérification de l'orthographe: {e}")
            messagebox.showerror("Erreur", f"Erreur lors de la vérification de l'orthographe: {e}")

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

    # Add missing methods
    def _open_folder(self):
        """Internal method to open folder (alias for open_folder)."""
        return self.open_folder()

    def _load_flat_json(self):
        """Internal method to load flat JSON (alias for load_flat_json)."""
        return self.load_flat_json()

    def _show_search(self):
        """Internal method to show search (alias for show_search)."""
        return self.show_search()


# Legacy compatibility function
def create_fault_editor(root):
    """Create a FaultEditorController instance for legacy compatibility."""
    return FaultEditorController(root)
