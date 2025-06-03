# Fonctionnalités de recherche pour l'application Fault Editor
"""
Ce module gère toutes les fonctionnalités de recherche dans l'application.
Utilisez ces classes pour implémenter des recherches hiérarchiques et plates.
"""

import tkinter as tk
from typing import List, Tuple, Callable, Optional
from models.data_models import SearchResult, FaultData
from config.constants import Colors

class SearchManager:
    """Gestionnaire principal pour les fonctionnalités de recherche"""

    def __init__(self):
        self.search_results: List[SearchResult] = []
        self.current_index = -1
        self.search_frame: Optional[tk.Frame] = None
        self.search_var: Optional[tk.StringVar] = None
        self.results_label: Optional[tk.Label] = None

    def show_search_bar(self, parent: tk.Widget, callback: Callable):
        """Affiche la barre de recherche pour la vue hiérarchique"""
        # Fermer la barre de recherche existante si elle existe
        if self.search_frame:
            self.search_frame.destroy()
            self.search_frame = None

        # Créer la barre de recherche en utilisant le builder
        self.search_frame, self.search_var, self.results_label = SearchBarBuilder.create_search_bar(
            parent=parent,
            on_search=self._perform_search,
            on_next=self.next_result,
            on_prev=self.previous_result,
            on_close=self.close_search_bar
        )
          # Positionner la barre de recherche
        children = parent.winfo_children()
        if children:
            self.search_frame.pack(fill="x", after=children[0])
        else:
            self.search_frame.pack(fill="x")

        # Sauvegarder le callback pour les résultats
        self._search_callback = callback

        # Initialiser les variables de recherche
        self.reset_search()

    def close_search_bar(self):
        """Ferme la barre de recherche"""
        if self.search_frame:
            self.search_frame.destroy()
            self.search_frame = None
        self.reset_search()

    def reset_search(self):
        """Réinitialise les résultats de recherche"""
        self.search_results = []
        self.current_index = -1

    def get_current_result(self) -> Optional[SearchResult]:
        """Retourne le résultat de recherche actuel"""
        if 0 <= self.current_index < len(self.search_results):
            return self.search_results[self.current_index]
        return None

    def next_result(self) -> Optional[SearchResult]:
        """Passe au résultat suivant"""
        if not self.search_results:
            return None
        self.current_index = (self.current_index + 1) % len(self.search_results)
        return self.get_current_result()

    def previous_result(self) -> Optional[SearchResult]:
        """Passe au résultat précédent"""
        if not self.search_results:
            return None
        self.current_index = (self.current_index - 1) % len(self.search_results)
        return self.get_current_result()

    def _perform_search(self):
        """Effectue la recherche et appelle le callback avec les résultats"""
        if not self.search_var:
            return

        search_text = self.search_var.get().strip()
        if not search_text:
            self.reset_search()
            if self.results_label:
                self.results_label.config(text="")
            return

        # Pour l'instant, on simule des résultats vides
        # Cette méthode sera overridée ou complétée selon les besoins
        results = []

        if hasattr(self, '_search_callback') and self._search_callback:
            self._search_callback(results)

        # Mettre à jour le compteur
        if self.results_label:
            if results:
                self.results_label.config(text=f"1/{len(results)}")
            else:
                self.results_label.config(text="0/0")

class HierarchicalSearcher:
    """Gestionnaire de recherche pour la vue hiérarchique"""

    def __init__(self, columns: List[tk.Frame]):
        self.columns = columns

    def search_in_columns(self, search_text: str) -> List[Tuple[tk.Frame, tk.Frame]]:
        """Recherche dans toutes les colonnes hiérarchiques"""
        results = []
        search_lower = search_text.lower()

        for column in self.columns:
            for row in column.winfo_children():
                if isinstance(row, tk.Frame):
                    # Rechercher dans les labels de la ligne
                    for widget in row.winfo_children():
                        if isinstance(widget, tk.Label):
                            text = widget.cget("text")
                            if search_lower in text.lower():
                                results.append((column, row))
                                break

        return results

    def highlight_result(self, column: tk.Frame, row: tk.Frame):
        """Met en évidence un résultat de recherche"""
        self.clear_all_highlights()

        # Mettre en surbrillance la ligne trouvée
        row.configure(bg=Colors.SEARCH_HIGHLIGHT)
        for widget in row.winfo_children():
            if isinstance(widget, (tk.Label, tk.Canvas)):
                widget.configure(bg=Colors.SEARCH_HIGHLIGHT)

    def clear_all_highlights(self):
        """Supprime tous les surlignages de recherche"""
        for column in self.columns:
            for idx, row in enumerate(column.winfo_children()):
                if isinstance(row, tk.Frame):
                    # Restaurer la couleur d'origine basée sur l'index
                    original_color = Colors.BG_ROW if idx % 2 == 0 else Colors.BG_ROW_ALT
                    row.configure(bg=original_color)
                    for widget in row.winfo_children():
                        if isinstance(widget, (tk.Label, tk.Canvas)):
                            widget.configure(bg=original_color)

class FlatSearcher:
    """Gestionnaire de recherche pour l'éditeur de fichiers plats"""

    def __init__(self, all_keys: List[str], entry_vars: dict):
        self.all_keys = all_keys
        self.entry_vars = entry_vars

    def search_in_flat_data(self, search_text: str) -> List[int]:
        """Recherche dans les données plates"""
        results = []
        search_lower = search_text.lower()

        for row_idx, key in enumerate(self.all_keys, start=1):
            # Rechercher dans la clé
            if search_lower in key.lower():
                results.append(row_idx)
                continue
              # Rechercher dans les valeurs
            for lang in ["fr", "en", "es"]:
                var = self.entry_vars.get((row_idx, lang))
                if var and search_lower in var.get().lower():
                    results.append(row_idx)
                    break

        return results

    def highlight_row(self, grid_frame: tk.Frame, row_idx: int):
        """Met en évidence une ligne spécifique"""
        self.clear_all_highlights(grid_frame)

        # Mettre en surbrillance la ligne trouvée
        for widget in grid_frame.grid_slaves(row=row_idx):
            if hasattr(widget, 'config'):
                widget.config(bg=Colors.SEARCH_HIGHLIGHT)

    def clear_all_highlights(self, grid_frame: tk.Frame):
        """Supprime tous les surlignages dans la grille"""
        for row_idx in range(1, len(self.all_keys) + 1):
            for widget in grid_frame.grid_slaves(row=row_idx):
                if hasattr(widget, 'config'):
                    original_color = Colors.BG_ROW if row_idx % 2 == 1 else Colors.BG_ROW_ALT
                    widget.config(bg=original_color)

class SearchBarBuilder:
    """Constructeur pour les barres de recherche"""

    @staticmethod
    def create_search_bar(parent: tk.Widget, on_search: Callable, on_next: Callable,
                         on_prev: Callable, on_close: Callable) -> Tuple[tk.Frame, tk.StringVar, tk.Label]:
        """Crée une barre de recherche standardisée"""

        # Créer la barre de recherche
        search_frame = tk.Frame(parent, bg=Colors.BG_TOPBAR)

        # Container gauche pour le champ de recherche
        search_container = tk.Frame(search_frame, bg=Colors.BG_TOPBAR)
        search_container.pack(side="left", fill="x", expand=True)

        # Container droit pour les boutons
        buttons_container = tk.Frame(search_frame, bg=Colors.BG_TOPBAR)
        buttons_container.pack(side="right", fill="x")

        # Icône et champ de recherche
        search_label = tk.Label(search_container, text="🔍", bg=Colors.BG_TOPBAR,
                               fg="white", font=("Segoe UI", 12))
        search_label.pack(side="left", padx=(10, 0))

        search_var = tk.StringVar()
        search_entry = tk.Entry(search_container, textvariable=search_var, width=40,
                               bg=Colors.EDIT_BG, fg=Colors.EDIT_FG,
                               insertbackground="white")
        search_entry.pack(side="left", padx=10)

        # Compteur de résultats
        results_label = tk.Label(search_container, text="", bg=Colors.BG_TOPBAR,
                                fg="white")
        results_label.pack(side="left", padx=10)

        # Style commun pour les boutons
        button_style = {
            "bg": Colors.BG_TOPBAR,
            "fg": "white",
            "relief": "flat",
            "padx": 10,
            "pady": 5
        }

        # Boutons de navigation
        tk.Button(buttons_container, text="◀", command=on_prev, **button_style).pack(side="left", padx=2)
        tk.Button(buttons_container, text="▶", command=on_next, **button_style).pack(side="left", padx=2)

        # Bouton fermer
        tk.Button(buttons_container, text="✖", command=on_close, **button_style).pack(side="left", padx=(10, 5))

        # Configuration des événements
        search_var.trace_add("write", lambda *args: on_search())
        search_entry.bind("<Return>", lambda e: on_next())
        search_entry.bind("<Escape>", lambda e: on_close())

        # Focus sur le champ de recherche
        search_entry.focus_set()

        return search_frame, search_var, results_label
