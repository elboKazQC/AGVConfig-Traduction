# Éditeur hiérarchique pour l'application Fault Editor
"""
Ce module contient l'éditeur principal pour la vue hiérarchique des défauts.
Utilisez cette classe pour afficher et éditer les fichiers JSON hiérarchiques.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Optional, Callable, Tuple
from functools import partial
import logging

from config.constants import Colors, Fonts, Dimensions
from ui.components import StyledFrame, StyledLabel, ProgressDialog
from models.data_models import FaultData, ApplicationState, SearchResult
from search.search_manager import HierarchicalSearcher, SearchBarBuilder

logger = logging.getLogger(__name__)

class HierarchicalEditor:
    """Éditeur principal pour la vue hiérarchique"""
      def __init__(self, parent: tk.Widget, app_state: ApplicationState):
        self.parent = parent
        self.app_state = app_state
        self.columns: List[StyledFrame] = []
        self.main_canvas: tk.Canvas  # Suppression du Optional        self.columns_frame: StyledFrame  # Suppression du Optional
        self.searcher: Optional[HierarchicalSearcher] = None
        self.search_frame: Optional[tk.Frame] = None
        self._raw_search_results: List[Tuple[tk.Frame, tk.Frame]] = []  # Stockage des résultats bruts

        # Callbacks externes
        self.on_single_click: Optional[Callable] = None
        self.on_double_click: Optional[Callable] = None
        self.on_file_change: Optional[Callable] = None

        self._setup_canvas()

    def _setup_canvas(self):
        """Configure le canvas principal pour les colonnes"""
        # Conteneur pour le canvas et les scrollbars
        container = StyledFrame(self.parent)
        container.pack(fill="both", expand=True)

        # Canvas principal
        self.main_canvas = tk.Canvas(container, bg=Colors.BG_MAIN)
        self.main_canvas.pack(side="left", fill="both", expand=True)

        # Scrollbars
        scrollbar_y = ttk.Scrollbar(container, orient="vertical", command=self.main_canvas.yview)
        scrollbar_y.pack(side="right", fill="y")
        self.main_canvas.configure(yscrollcommand=scrollbar_y.set)

        scrollbar_x = ttk.Scrollbar(container, orient="horizontal", command=self.main_canvas.xview)
        scrollbar_x.pack(side="bottom", fill="x")
        self.main_canvas.configure(xscrollcommand=scrollbar_x.set)

        # Frame interne pour les colonnes
        self.columns_frame = StyledFrame(self.main_canvas)
        canvas_window = self.main_canvas.create_window((0, 0), window=self.columns_frame, anchor="nw")

        # Configuration des événements
        self.columns_frame.bind("<Configure>", self._on_frame_configure)
        self.main_canvas.bind("<Configure>", self._on_canvas_configure)

        # Scroll avec la molette
        self.main_canvas.bind_all("<MouseWheel>", self._on_mousewheel)        # Initialiser le searcher
        # On cast les StyledFrame en tk.Frame car ttk.Frame hérite de tk.Frame
        self.searcher = HierarchicalSearcher([col for col in self.columns])

    def _on_frame_configure(self, event):
        """Appelé quand la frame des colonnes change de taille"""
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Appelé quand le canvas change de taille"""
        canvas_width = event.width
        self.main_canvas.itemconfig(
            self.main_canvas.find_all()[0],
            width=max(canvas_width, self.columns_frame.winfo_reqwidth())
        )

    def _on_mousewheel(self, event):
        """Gère le scroll avec la molette"""
        if event.state & 0x4:  # Ctrl pressé
            return
        elif event.state & 0x1:  # Shift pressé
            self.main_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            self.main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def display_column(self, fault_list: List[Dict[str, Any]], path: List[int],
                      filename: str, level: int):
        """Affiche une colonne de défauts"""
        col_index = len(self.columns)

        # Créer la frame de la colonne
        column_frame = StyledFrame(self.columns_frame, style_type="default")
        column_frame.grid(row=0, column=col_index, padx=5, pady=10, sticky="nsew")
        self.columns_frame.grid_columnconfigure(col_index, minsize=Dimensions.MIN_COL_WIDTH)
        self.columns.append(column_frame)

        # Ajouter les éléments de défaut
        for idx, fault in enumerate(fault_list):
            self._create_fault_row(column_frame, fault, idx, path, level, filename)        # Mettre à jour l'affichage
        self.parent.update_idletasks()
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        self.main_canvas.yview_moveto(0.0)

    def _create_fault_row(self, parent: StyledFrame, fault: Dict[str, Any], idx: int,
                         path: List[int], level: int, filename: str):
        """Crée une ligne pour un défaut"""
        row = tk.Frame(parent, bg=Colors.BG_ROW, highlightthickness=0,
                      highlightbackground=Colors.HIGHLIGHT)
        row.pack(fill="x", padx=4, pady=3)

        # Effets de survol
        row.bind("<Enter>", lambda e: row.configure(highlightthickness=1))
        row.bind("<Leave>", lambda e: row.configure(highlightthickness=0))

        # Indicateur de type (point coloré)
        color = Colors.GREEN if fault.get("IsExpandable") else Colors.RED
        dot = tk.Canvas(row, width=14, height=14, bg=Colors.BG_ROW, highlightthickness=0)
        dot.create_oval(2, 2, 12, 12, fill=color, outline=color)
        dot.pack(side="left", padx=(6, 8))

        # Label de description
        label_text = f"{idx}: {fault.get('Description', '(vide)')}"
        label = tk.Label(row, text=label_text, fg=Colors.FG_TEXT, bg=Colors.BG_ROW,
                        anchor="w", font=Fonts.DEFAULT)
        label.pack(side="left", fill="x", expand=True)

        # Événements de clic
        if self.on_single_click:
            label.bind("<Button-1>", partial(self._handle_single_click, fault, idx, path, level, filename))

        if self.on_double_click:
            label.bind("<Double-1>", partial(self._handle_double_click, fault, idx, path, level, filename, row))

    def _handle_single_click(self, fault: Dict[str, Any], idx: int, path: List[int],
                           level: int, filename: str, event):
        """Gère le clic simple avec délai pour éviter les conflits avec le double-clic"""
        widget = event.widget
        # Annuler le job précédent s'il existe
        if hasattr(widget, '_click_job'):
            widget.after_cancel(widget._click_job)

        # Programmer l'action avec un délai
        widget._click_job = widget.after(300, lambda: self.on_single_click(fault, idx, path, level, filename))

    def _handle_double_click(self, fault: Dict[str, Any], idx: int, path: List[int],
                           level: int, filename: str, row: tk.Frame, event):
        """Gère le double-clic"""
        widget = event.widget
        # Annuler le clic simple en attente
        if hasattr(widget, '_click_job'):
            widget.after_cancel(widget._click_job)

        if self.on_double_click:
            self.on_double_click(fault, idx, path, level, filename, row)

    def render_row_readonly(self, row: tk.Frame, fault: Dict[str, Any], idx: int):
        """Affiche une ligne en mode lecture seule"""
        # Nettoyer la ligne
        for widget in row.winfo_children():
            widget.destroy()

        # Recréer les éléments en lecture seule
        color = Colors.GREEN if fault.get("IsExpandable") else Colors.RED
        dot = tk.Canvas(row, width=14, height=14, bg=Colors.BG_ROW, highlightthickness=0)
        dot.create_oval(2, 2, 12, 12, fill=color, outline=color)
        dot.pack(side="left", padx=(6, 8))

        label_text = f"{idx}: {fault.get('Description', '(vide)')}"
        label = tk.Label(row, text=label_text, fg=Colors.FG_TEXT, bg=Colors.BG_ROW,
                        anchor="w", font=Fonts.DEFAULT)
        label.pack(side="left", fill="x", expand=True)

    def make_row_editable(self, row: tk.Frame, fault: Dict[str, Any], idx: int,
                         save_callback: Callable):
        """Rend une ligne éditable"""
        # Nettoyer la ligne
        for widget in row.winfo_children():
            widget.destroy()

        # Champ d'édition pour la description
        desc_var = tk.StringVar(value=fault.get("Description", ""))
        desc_entry = tk.Entry(row, textvariable=desc_var, bg=Colors.EDIT_BG,
                             fg=Colors.EDIT_FG, highlightthickness=0, relief="flat",
                             font=Fonts.DEFAULT)
        desc_entry.pack(side="left", padx=5, fill="both", expand=True, ipady=4)
        desc_entry.focus_set()

        # Checkbox pour IsExpandable
        exp_var = tk.BooleanVar(value=fault.get("IsExpandable", False))
        exp_check = tk.Checkbutton(row, text="Expandable", variable=exp_var,
                                  bg=Colors.BG_ROW, fg=Colors.FG_TEXT,
                                  selectcolor=Colors.BG_ROW,
                                  activebackground=Colors.BG_ROW,
                                  highlightthickness=0, bd=0,
                                  font=Fonts.DEFAULT)
        exp_check.pack(side="left", padx=5)

        # Bouton de sauvegarde
        def save_edit():
            fault["Description"] = desc_var.get()
            fault["IsExpandable"] = exp_var.get()
            save_callback(fault, idx)

        tk.Button(row, text="✅", command=save_edit,
                 bg=Colors.BG_ROW, fg=Colors.FG_TEXT, relief="flat",
                 font=Fonts.DEFAULT).pack(side="left", padx=5)

        # Événement pour sauvegarder avec Entrée
        desc_entry.bind("<Return>", lambda e: save_edit())

        # Mettre à jour l'affichage
        row.update_idletasks()
        self.columns_frame.event_generate("<Configure>")

    def clear_columns_from(self, level: int):
        """Supprime toutes les colonnes à partir d'un niveau donné"""
        while len(self.columns) > level:
            column = self.columns.pop()
            column.destroy()

    def show_search_bar(self):
        """Affiche la barre de recherche hiérarchique"""
        if self.search_frame:
            self.search_frame.destroy()

        self.search_frame, search_var, results_label = SearchBarBuilder.create_search_bar(
            self.parent,
            on_search=lambda: self._perform_search(search_var.get(), results_label),
            on_next=lambda: self._next_search_result(results_label),
            on_prev=lambda: self._prev_search_result(results_label),
            on_close=self._close_search_bar
        )

        # Positionner la barre de recherche
        self.search_frame.pack(fill="x", before=self.main_canvas.master)    def _perform_search(self, search_text: str, results_label: tk.Label):
        """Effectue une recherche hiérarchique"""
        if not search_text.strip():
            self.app_state.reset_search()
            if self.searcher:
                self.searcher.clear_all_highlights()
            results_label.config(text="")
            return

        # Rechercher dans les colonnes
        if self.searcher:
            raw_results = self.searcher.search_in_columns(search_text.strip())
            # Convertir les résultats en SearchResult
            search_results = []
            for i, (column, row) in enumerate(raw_results):
                # Créer un SearchResult factice pour la compatibilité
                search_result = SearchResult(
                    column_index=self.columns.index(column) if column in self.columns else 0,
                    row_index=i,
                    fault_data=FaultData(),  # Données factices
                    match_text=search_text,
                    file_metadata=None  # Métadonnées factices
                )
                search_results.append(search_result)

            self.app_state.search_results = search_results
            # Stocker aussi les résultats bruts pour la navigation
            self._raw_search_results = raw_results

            if search_results:
                self.app_state.current_search_index = 0
                self._highlight_current_result(results_label)
            else:
                self.searcher.clear_all_highlights()
                results_label.config(text="0/0")
        else:
            results_label.config(text="0/0")

    def _next_search_result(self, results_label: tk.Label):
        """Passe au résultat suivant"""
        if not self.app_state.search_results:
            return

        self.app_state.current_search_index = (
            self.app_state.current_search_index + 1
        ) % len(self.app_state.search_results)
        self._highlight_current_result(results_label)

    def _prev_search_result(self, results_label: tk.Label):
        """Passe au résultat précédent"""
        if not self.app_state.search_results:
            return

        self.app_state.current_search_index = (
            self.app_state.current_search_index - 1
        ) % len(self.app_state.search_results)
        self._highlight_current_result(results_label)

    def _highlight_current_result(self, results_label: tk.Label):
        """Met en évidence le résultat de recherche actuel"""
        if not self.app_state.search_results or self.app_state.current_search_index < 0:
            return

        column, row = self.app_state.search_results[self.app_state.current_search_index]
        self.searcher.highlight_result(column, row)

        # Mettre à jour le compteur
        current = self.app_state.current_search_index + 1
        total = len(self.app_state.search_results)
        results_label.config(text=f"{current}/{total}")

        # S'assurer que le résultat est visible
        self._ensure_result_visible(row)

    def _ensure_result_visible(self, row: tk.Frame):
        """S'assure qu'un résultat est visible dans le canvas"""
        # Calculer la position de la ligne
        bbox = self.main_canvas.bbox("all")
        if not bbox:
            return

        widget_y = row.winfo_y()
        canvas_height = self.main_canvas.winfo_height()

        # Obtenir la vue actuelle
        current_view_top = self.main_canvas.yview()[0] * bbox[3]
        current_view_bottom = self.main_canvas.yview()[1] * bbox[3]

        # Vérifier si le widget est visible
        if widget_y < current_view_top or widget_y + row.winfo_height() > current_view_bottom:
            # Calculer la nouvelle position pour centrer le résultat
            new_y = (widget_y - (canvas_height / 2)) / bbox[3]
            new_y = max(0, min(1, new_y))
            self.main_canvas.yview_moveto(new_y)

    def _close_search_bar(self):
        """Ferme la barre de recherche"""
        if self.search_frame:
            self.search_frame.destroy()
            self.search_frame = None

        self.app_state.reset_search()
        self.searcher.clear_all_highlights()

    def set_single_click_callback(self, callback: Callable):
        """Définit le callback pour les clics simples"""
        self.on_single_click = callback

    def set_double_click_callback(self, callback: Callable):
        """Définit le callback pour les double-clics"""
        self.on_double_click = callback

    def set_file_change_callback(self, callback: Callable):
        """Définit le callback pour les changements de fichier"""
        self.on_file_change = callback

    def load_data(self, base_directory: str, current_language: str, file_metadata: Any):
        """Load JSON data for hierarchical display"""
        try:
            # Store the data in app state for reference
            self.app_state.base_directory = base_directory
            self.app_state.current_language = current_language

            # Clear existing columns
            for column in self.columns:
                column.destroy()
            self.columns.clear()

            # This would typically load and display the root level of the hierarchy
            # For now, just update the status
            logger.info(f"Hierarchical editor loaded data from {base_directory}")

        except Exception as e:
            logger.error(f"Error loading data in hierarchical editor: {e}")
            raise
