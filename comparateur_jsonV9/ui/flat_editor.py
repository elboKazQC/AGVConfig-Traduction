"""
Flat JSON Editor Module

This module provides a flat JSON editor interface for the Fault Editor application.
It handles the display, editing, searching, and translation of flat JSON files.

Author: AI Assistant
Created: 2024
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
from typing import Dict, List, Optional, Tuple, Any

# Import modules
from config.constants import *
from models.data_models import ApplicationState
from translation.translation_manager import TranslationManager
from ui.components import StyledFrame, StyledButton, ProgressDialog


class FlatEditor:
    """
    Handles flat JSON file editing interface with search and translation capabilities.
    """

    def __init__(self, parent, translation_manager: TranslationManager):
        """
        Initialize the flat editor.

        Args:
            parent: Parent tkinter widget
            translation_manager: Translation manager instance
        """
        self.parent = parent
        self.translation_manager = translation_manager
        self.editor_window: Optional[tk.Toplevel] = None

        # Search state
        self.search_frame: Optional[tk.Frame] = None
        self.search_var: Optional[tk.StringVar] = None
        self.search_results: List[int] = []
        self.current_search_index: int = -1
        self.results_label: Optional[tk.Label] = None

    def load_flat_json(self, fr_path: str, en_path: str, es_path: str):
        """
        Load flat JSON files and show the editor.

        Args:
            fr_path: Path to French JSON file
            en_path: Path to English JSON file
            es_path: Path to Spanish JSON file
        """
        try:
            print(f"Chargement des fichiers plats: {fr_path}, {en_path}, {es_path}")

            # Load JSON files
            with open(fr_path, "r", encoding="utf-8") as f:
                fr_data = json.load(f)
            with open(en_path, "r", encoding="utf-8") as f:
                en_data = json.load(f)
            with open(es_path, "r", encoding="utf-8") as f:
                es_data = json.load(f)

            # Get all unique keys
            all_keys = set(fr_data.keys()) | set(en_data.keys()) | set(es_data.keys())
            all_keys = sorted(list(all_keys))

            print(f"Nombre de clés trouvées: {len(all_keys)}")
            self.show_flat_json_editor(fr_path, en_path, es_path, fr_data, en_data, es_data, all_keys)

        except Exception as e:
            print(f"Erreur lors du chargement des fichiers JSON plats: {e}")
            messagebox.showerror("Erreur", f"Impossible de charger les fichiers JSON: {e}")

    def show_flat_json_editor(self, fr_path: str, en_path: str, es_path: str,
                             fr_data: Dict, en_data: Dict, es_data: Dict, all_keys: List[str]):
        """
        Display the flat JSON editor window.

        Args:
            fr_path: Path to French JSON file
            en_path: Path to English JSON file
            es_path: Path to Spanish JSON file
            fr_data: French data dictionary
            en_data: English data dictionary
            es_data: Spanish data dictionary
            all_keys: List of all unique keys
        """
        # Create editor window
        self.editor_window = tk.Toplevel(self.parent)
        self.editor_window.title("Éditeur de fichiers JSON plats")
        self.editor_window.geometry("1200x800")
        self.editor_window.configure(bg=Colors.BG_MAIN)

        # Store paths and data
        self.editor_window.fr_path = fr_path
        self.editor_window.en_path = en_path
        self.editor_window.es_path = es_path
        self.editor_window.all_keys = all_keys

        # Create toolbar
        toolbar = StyledFrame(self.editor_window, bg=Colors.BG_TOPBAR)
        toolbar.pack(fill="x")
        self.setup_flat_editor_toolbar(self.editor_window, toolbar)

        # Create main scrollable area
        main_frame = tk.Frame(self.editor_window, bg=Colors.BG_MAIN)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Canvas and scrollbar for scrolling
        canvas = tk.Canvas(main_frame, bg=Colors.BG_MAIN, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Colors.BG_MAIN)

        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Store canvas reference
        self.editor_window.canvas = canvas
        self.editor_window.grid_frame = scrollable_frame

        # Create header
        self._create_header(scrollable_frame)

        # Create data grid
        self.editor_window.entry_vars = {}
        self._create_data_grid(scrollable_frame, fr_data, en_data, es_data, all_keys)

        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<MouseWheel>", _on_mousewheel)
        self.editor_window.bind("<MouseWheel>", _on_mousewheel)

        # Create status bar
        status_frame = tk.Frame(self.editor_window, bg=Colors.BG_MAIN)
        status_frame.pack(fill="x", side="bottom")

        self.editor_window.status_bar = tk.Label(
            status_frame,
            text=f"✅ {len(all_keys)} entrées chargées",
            bg=Colors.BG_MAIN,
            fg=Colors.FG_TEXT,
            font=Fonts.DEFAULT,
            anchor="w"
        )
        self.editor_window.status_bar.pack(fill="x", padx=10, pady=5)

        # Bind keyboard shortcuts
        self._bind_keyboard_shortcuts()

        print(f"Éditeur de fichiers plats affiché avec {len(all_keys)} entrées")

    def _create_header(self, parent):
        """Create the header row for the flat editor."""
        header_frame = tk.Frame(parent, bg=Colors.BG_TOPBAR, height=40)
        header_frame.pack(fill="x", pady=(0, 5))
        header_frame.pack_propagate(False)

        # Header labels
        headers = [("Clé", 0.4), ("Français", 0.2), ("Anglais", 0.2), ("Espagnol", 0.2)]

        for i, (text, width) in enumerate(headers):
            label = tk.Label(
                header_frame,
                text=text,
                bg=Colors.BG_TOPBAR,
                fg="white",
                font=Fonts.TITLE,
                anchor="w",
                padx=10
            )
            label.place(relx=sum(h[1] for h in headers[:i]), rely=0, relwidth=width, relheight=1)

    def _create_data_grid(self, parent, fr_data: Dict, en_data: Dict, es_data: Dict, all_keys: List[str]):
        """Create the data grid for editing values."""
        for row_idx, key in enumerate(all_keys, start=1):
            # Create row frame
            row_frame = tk.Frame(parent, bg=Colors.BG_ROW if row_idx % 2 == 1 else Colors.BG_ROW_ALT, height=35)
            row_frame.pack(fill="x", pady=1)
            row_frame.pack_propagate(False)

            # Key label
            key_label = tk.Label(
                row_frame,
                text=key,
                bg=Colors.BG_ROW if row_idx % 2 == 1 else Colors.BG_ROW_ALT,
                fg=Colors.FG_TEXT,
                font=Fonts.DEFAULT,
                anchor="w",
                padx=10
            )
            key_label.place(relx=0, rely=0, relwidth=0.4, relheight=1)

            # Create entry variables and widgets
            languages = [("fr", fr_data), ("en", en_data), ("es", es_data)]
            x_positions = [0.4, 0.6, 0.8]

            for i, (lang, data) in enumerate(languages):
                var = tk.StringVar(value=data.get(key, ""))
                self.editor_window.entry_vars[(row_idx, lang)] = var

                entry = tk.Entry(
                    row_frame,
                    textvariable=var,
                    bg=Colors.EDIT_BG,
                    fg=Colors.EDIT_FG,
                    font=Fonts.DEFAULT,
                    relief="flat",
                    bd=1
                )
                entry.place(relx=x_positions[i], rely=0.1, relwidth=0.19, relheight=0.8)

                # Add translation button for French entries
                if lang == "fr":
                    translate_btn = tk.Button(
                        row_frame,
                        text="🌐",
                        command=lambda r=row_idx: self.translate_row(r),
                        bg=Colors.BG_COLUMN,
                        fg="white",
                        font=("Segoe UI", 8),
                        relief="flat",
                        width=2,
                        height=1
                    )
                    translate_btn.place(relx=0.38, rely=0.2, width=20, height=20)

    def setup_flat_editor_toolbar(self, editor_window, toolbar):
        """Setup the toolbar for the flat editor."""
        # Save button
        save_btn = StyledButton(
            toolbar,
            text="💾 Sauvegarder",
            command=lambda: self.save_flat_files(editor_window),
            style_type="topbar"
        )
        save_btn.pack(side="left", padx=15, pady=5)

        # Search button
        search_btn = StyledButton(
            toolbar,
            text="🔍 Rechercher",
            command=lambda: self.show_flat_search(editor_window),
            style_type="topbar"
        )
        search_btn.pack(side="left", padx=15, pady=5)

        # Translate all button
        translate_all_btn = StyledButton(
            toolbar,
            text="🌐 Traduire tout",
            command=lambda: self.translate_all(editor_window),
            style_type="topbar"
        )
        translate_all_btn.pack(side="left", padx=15, pady=5)

    def show_flat_search(self, editor_window):
        """Show the search bar for the flat editor."""
        # Close existing search bar if it exists
        if hasattr(editor_window, 'search_frame') and editor_window.search_frame:
            editor_window.search_frame.destroy()
            editor_window.search_frame = None

        # Create search bar
        editor_window.search_frame = tk.Frame(editor_window, bg=Colors.BG_TOPBAR)
        editor_window.search_frame.pack(fill="x", after=editor_window.winfo_children()[0])

        # Left container for search field
        search_container = tk.Frame(editor_window.search_frame, bg=Colors.BG_TOPBAR)
        search_container.pack(side="left", fill="x", expand=True)

        # Right container for buttons
        buttons_container = tk.Frame(editor_window.search_frame, bg=Colors.BG_TOPBAR)
        buttons_container.pack(side="right", fill="x")

        # Search icon and field
        search_label = tk.Label(search_container, text="🔍", bg=Colors.BG_TOPBAR, fg="white",
                               font=("Segoe UI", 12))
        search_label.pack(side="left", padx=(10, 0))

        editor_window.search_var = tk.StringVar()
        search_entry = tk.Entry(search_container, textvariable=editor_window.search_var, width=40,
                               bg=Colors.EDIT_BG, fg=Colors.EDIT_FG, font=Fonts.DEFAULT,
                               insertbackground="white")
        search_entry.pack(side="left", padx=10)

        # Results counter
        editor_window.results_label = tk.Label(search_container, text="", bg=Colors.BG_TOPBAR,
                                              fg="white", font=Fonts.DEFAULT)
        editor_window.results_label.pack(side="left", padx=10)

        # Button style
        button_style = {
            "bg": Colors.BG_TOPBAR,
            "fg": "white",
            "font": Fonts.DEFAULT,
            "relief": "flat",
            "padx": 10,
            "pady": 5
        }

        # Navigation buttons
        tk.Button(buttons_container, text="◀", command=lambda: self.prev_flat_search_result(editor_window),
                 **button_style).pack(side="left", padx=2)
        tk.Button(buttons_container, text="▶", command=lambda: self.next_flat_search_result(editor_window),
                 **button_style).pack(side="left", padx=2)

        # Close button
        tk.Button(buttons_container, text="✖", command=lambda: self.close_flat_search(editor_window),
                 **button_style).pack(side="left", padx=(10, 5))

        # Configure real-time search
        editor_window.search_var.trace_add("write", lambda *args: self.flat_search_as_you_type(editor_window))
        search_entry.bind("<Return>", lambda e: self.next_flat_search_result(editor_window))
        search_entry.bind("<Escape>", lambda e: self.close_flat_search(editor_window))

        # Initialize search variables
        editor_window.search_results = []
        editor_window.current_search_index = -1

        # Focus on search field
        search_entry.focus_set()
        print("Flat search bar displayed")

    def close_flat_search(self, editor_window):
        """Close the search bar for the flat editor."""
        if hasattr(editor_window, 'search_frame') and editor_window.search_frame:
            editor_window.search_frame.destroy()
            editor_window.search_frame = None
        editor_window.search_results = []
        editor_window.current_search_index = -1
        self.clear_flat_search_highlights(editor_window)

    def clear_flat_search_highlights(self, editor_window):
        """Clear search highlights in the flat editor."""
        for row_idx in range(1, len(editor_window.all_keys) + 1):
            for widget in editor_window.grid_frame.grid_slaves(row=row_idx):
                widget.config(bg=Colors.BG_ROW if row_idx % 2 == 1 else Colors.BG_ROW_ALT)

    def flat_search_as_you_type(self, editor_window):
        """Real-time search in the flat editor."""
        search_text = editor_window.search_var.get().strip()
        if not search_text:
            editor_window.search_results = []
            editor_window.current_search_index = -1
            self.clear_flat_search_highlights(editor_window)
            editor_window.results_label.config(text="")
            return

        # Search in keys and values
        results = []
        for row_idx, key in enumerate(editor_window.all_keys, start=1):
            if search_text.lower() in key.lower():
                results.append(row_idx)
            else:
                # Check values
                for lang in ["fr", "en", "es"]:
                    var = editor_window.entry_vars.get((row_idx, lang))
                    if var and search_text.lower() in var.get().lower():
                        results.append(row_idx)
                        break

        editor_window.search_results = results
        if results:
            editor_window.current_search_index = 0
            self.highlight_flat_search_result(editor_window, results[0])
            editor_window.results_label.config(text=f"1/{len(results)}")
        else:
            self.clear_flat_search_highlights(editor_window)
            editor_window.results_label.config(text="0/0")

    def highlight_flat_search_result(self, editor_window, row_idx):
        """Highlight a specific search result and scroll to it if necessary."""
        self.clear_flat_search_highlights(editor_window)

        # Find and highlight the row
        row_frames = [child for child in editor_window.grid_frame.winfo_children()
                     if isinstance(child, tk.Frame)]

        if row_idx <= len(row_frames):
            target_frame = row_frames[row_idx]  # Accounting for header
            target_frame.config(bg=Colors.SEARCH_HIGHLIGHT)

            # Highlight all widgets in the row
            for widget in target_frame.winfo_children():
                if isinstance(widget, (tk.Label, tk.Entry)):
                    widget.config(bg=Colors.SEARCH_HIGHLIGHT)

            # Scroll to make visible
            self._ensure_flat_result_visible(editor_window, target_frame)

        # Update results counter
        total_results = len(editor_window.search_results)
        current_index = editor_window.current_search_index + 1
        if total_results > 0:
            editor_window.results_label.config(text=f"{current_index}/{total_results}")

    def _ensure_flat_result_visible(self, editor_window, target_frame):
        """Ensure a search result is visible on screen."""
        # Calculate widget coordinates in canvas
        widget_y = target_frame.winfo_y()
        canvas_height = editor_window.canvas.winfo_height()

        # Get current view coordinates
        try:
            frame_height = editor_window.grid_frame.winfo_height()
            if frame_height > 0:
                current_view_top = editor_window.canvas.yview()[0] * frame_height
                current_view_bottom = editor_window.canvas.yview()[1] * frame_height

                # If widget is not completely visible, scroll to it
                if widget_y < current_view_top or widget_y + target_frame.winfo_height() > current_view_bottom:
                    # Calculate new scroll position to center the result
                    new_y = (widget_y - (canvas_height / 2)) / frame_height
                    # Limit position between 0 and 1
                    new_y = max(0, min(1, new_y))
                    editor_window.canvas.yview_moveto(new_y)
        except:
            pass  # Ignore scroll errors

        editor_window.update_idletasks()

    def next_flat_search_result(self, editor_window):
        """Go to next search result in flat editor."""
        if not editor_window.search_results:
            return

        editor_window.current_search_index = (editor_window.current_search_index + 1) % len(editor_window.search_results)
        self.highlight_flat_search_result(editor_window, editor_window.search_results[editor_window.current_search_index])

    def prev_flat_search_result(self, editor_window):
        """Go to previous search result in flat editor."""
        if not editor_window.search_results:
            return

        editor_window.current_search_index = (editor_window.current_search_index - 1) % len(editor_window.search_results)
        self.highlight_flat_search_result(editor_window, editor_window.search_results[editor_window.current_search_index])

    def translate_row(self, row_idx):
        """Translate a specific row from French to English and Spanish."""
        fr_text = self.editor_window.entry_vars.get((row_idx, "fr"))
        if fr_text and fr_text.get().strip():
            try:
                # Visual effect for translation start
                row_frames = [child for child in self.editor_window.grid_frame.winfo_children()
                             if isinstance(child, tk.Frame)]

                if row_idx < len(row_frames):
                    target_frame = row_frames[row_idx]
                    target_frame.config(bg=Colors.AMBER)
                    for widget in target_frame.winfo_children():
                        if isinstance(widget, (tk.Label, tk.Entry)):
                            widget.config(bg=Colors.AMBER)
                    self.editor_window.update_idletasks()

                # Translate to English
                en_translation = self.translation_manager.translate_text(fr_text.get(), "en")
                self.editor_window.entry_vars[(row_idx, "en")].set(en_translation)

                # Translate to Spanish
                es_translation = self.translation_manager.translate_text(fr_text.get(), "es")
                self.editor_window.entry_vars[(row_idx, "es")].set(es_translation)

                # Visual effect for success
                target_frame.config(bg=Colors.GREEN)
                for widget in target_frame.winfo_children():
                    if isinstance(widget, (tk.Label, tk.Entry)):
                        widget.config(bg=Colors.GREEN)

                self.editor_window.after(500, lambda: self._reset_row_color(row_idx))

                # Update status
                if hasattr(self.editor_window, 'status_bar'):
                    self.editor_window.status_bar.config(text=f"✅ Ligne {row_idx} traduite avec succès")

            except Exception as e:
                print(f"Erreur lors de la traduction de la ligne {row_idx}: {e}")
                # Visual effect for error
                if row_idx < len(row_frames):
                    target_frame = row_frames[row_idx]
                    target_frame.config(bg=Colors.RED)
                    for widget in target_frame.winfo_children():
                        if isinstance(widget, (tk.Label, tk.Entry)):
                            widget.config(bg=Colors.RED)

                    self.editor_window.after(500, lambda: self._reset_row_color(row_idx))

                if hasattr(self.editor_window, 'status_bar'):
                    self.editor_window.status_bar.config(text=f"❌ Erreur de traduction ligne {row_idx}")

    def _reset_row_color(self, row_idx):
        """Reset row color to original."""
        row_frames = [child for child in self.editor_window.grid_frame.winfo_children()
                     if isinstance(child, tk.Frame)]

        if row_idx < len(row_frames):
            original_bg = Colors.BG_ROW if row_idx % 2 == 1 else Colors.BG_ROW_ALT
            target_frame = row_frames[row_idx]
            target_frame.config(bg=original_bg)

            for widget in target_frame.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.config(bg=original_bg)
                elif isinstance(widget, tk.Entry):
                    widget.config(bg=Colors.EDIT_BG)

    def translate_all(self, editor_window):
        """Translate all French values to English and Spanish."""
        if not hasattr(editor_window, 'all_keys') or not editor_window.all_keys:
            return

        # Confirm operation
        if not messagebox.askyesno("Confirmation",
                                  "Voulez-vous traduire toutes les entrées françaises vers l'anglais et l'espagnol?"):
            return

        # Show progress dialog
        progress_dialog = ProgressDialog(
            editor_window,
            title="Traduction en cours",
            message="Traduction des entrées...",
            total=len(editor_window.all_keys)
        )

        try:
            translated = 0
            total = len(editor_window.all_keys)

            # For each key
            for row_idx, key in enumerate(editor_window.all_keys, start=1):
                # Get French text
                fr_text = editor_window.entry_vars.get((row_idx, "fr"))
                if fr_text and fr_text.get().strip():
                    try:
                        # Translate to English
                        en_translation = self.translation_manager.translate_text(fr_text.get(), "en")
                        editor_window.entry_vars[(row_idx, "en")].set(en_translation)

                        # Translate to Spanish
                        es_translation = self.translation_manager.translate_text(fr_text.get(), "es")
                        editor_window.entry_vars[(row_idx, "es")].set(es_translation)

                        translated += 1

                        # Update progress
                        progress_dialog.update_progress(
                            translated,
                            f"Traduction en cours... ({translated}/{total})"
                        )

                    except Exception as e:
                        print(f"Erreur lors de la traduction de '{fr_text.get()}': {e}")

            # Update final status
            editor_window.status_bar.config(text=f"✅ {translated} sur {total} entrées traduites")

        except Exception as e:
            editor_window.status_bar.config(text=f"❌ Erreur lors de la traduction: {e}")
            print(f"Erreur lors de la traduction: {e}")
        finally:
            # Close progress dialog
            progress_dialog.close()

    def save_flat_files(self, editor_window):
        """Save flat JSON files."""
        try:
            # Collect data
            fr_data = {}
            en_data = {}
            es_data = {}

            for row_idx, key in enumerate(editor_window.all_keys, start=1):
                fr_data[key] = editor_window.entry_vars[(row_idx, "fr")].get()
                en_data[key] = editor_window.entry_vars[(row_idx, "en")].get()
                es_data[key] = editor_window.entry_vars[(row_idx, "es")].get()

            # Save files
            files_to_save = [
                (editor_window.fr_path, fr_data),
                (editor_window.en_path, en_data),
                (editor_window.es_path, es_data)
            ]

            for path, data in files_to_save:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

            editor_window.status_bar.config(text="✅ Fichiers plats sauvegardés")
            print("Flat JSON files saved successfully")

        except Exception as e:
            editor_window.status_bar.config(text=f"❌ Erreur lors de la sauvegarde: {str(e)}")
            print(f"Erreur lors de la sauvegarde des fichiers plats: {e}")

    def _bind_keyboard_shortcuts(self):
        """Bind keyboard shortcuts for the flat editor."""
        if self.editor_window:
            # Search shortcut
            self.editor_window.bind("<Control-f>", lambda e: self.show_flat_search(self.editor_window))

            # Save shortcut
            self.editor_window.bind("<Control-s>", lambda e: self.save_flat_files(self.editor_window))

            # Close window shortcut
            def on_editor_close():
                if hasattr(self.parent, 'bind'):
                    self.parent.bind("<Control-f>", lambda e: None)  # Restore parent shortcuts
                self.editor_window.destroy()

            self.editor_window.protocol("WM_DELETE_WINDOW", on_editor_close)
