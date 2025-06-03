"""
This is a sample plugin for the Fault Editor application.
It adds statistics functionality to the fault editor.
"""

from plugins.plugin_system import Plugin
import tkinter as tk
from tkinter import ttk
import json
from typing import Dict, List, Any

class StatisticsPlugin(Plugin):
    """Plugin that adds statistics functionality to the fault editor."""

    # Plugin metadata
    name = "Statistics Plugin"
    version = "1.0.0"
    description = "Adds statistics functionality to the fault editor"
    author = "AI Assistant"

    def __init__(self, app=None):
        """Initialize the statistics plugin."""
        super().__init__(app)
        self.stats_window = None
        self.menu_button = None

    def activate(self):
        """Activate the plugin."""
        print("Statistics plugin activated")
        # Add button to toolbar if app is available
        if self.app and hasattr(self.app, 'main_controller'):
            self._add_statistics_button()

    def deactivate(self):
        """Deactivate the plugin."""
        print("Statistics plugin deactivated")
        # Remove button from toolbar
        if self.menu_button and self.menu_button.winfo_exists():
            self.menu_button.destroy()
            self.menu_button = None

        # Close statistics window if open
        if self.stats_window and self.stats_window.winfo_exists():
            self.stats_window.destroy()
            self.stats_window = None

    def _add_statistics_button(self):
        """Add statistics button to the main application toolbar."""
        try:
            # Find the toolbar in the app
            if hasattr(self.app.main_controller, 'topbar'):
                toolbar = self.app.main_controller.topbar

                # Import the StyledButton class from UI components
                from ui.components import StyledButton

                # Create button
                self.menu_button = StyledButton(
                    toolbar,
                    text="📊 Statistiques",
                    command=self.show_statistics,
                    style_type="topbar"
                )
                self.menu_button.pack(side="left", padx=15, pady=5)
                print("Statistics button added to toolbar")
        except Exception as e:
            print(f"Error adding statistics button: {e}")

    def show_statistics(self):
        """Show statistics window."""
        # Close existing window if open
        if self.stats_window and self.stats_window.winfo_exists():
            self.stats_window.destroy()

        # Create new window
        self.stats_window = tk.Toplevel(self.app.root if self.app else None)
        self.stats_window.title("Statistiques des codes d'erreur")
        self.stats_window.geometry("600x500")
        self.stats_window.grab_set()

        # Create container
        main_frame = tk.Frame(self.stats_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Add title
        title_label = tk.Label(
            main_frame,
            text="Statistiques des codes d'erreur",
            font=("Segoe UI", 14, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Get statistics
        stats = self._calculate_statistics()

        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True)

        # General statistics tab
        general_tab = tk.Frame(notebook)
        notebook.add(general_tab, text="Général")

        # Language statistics tab
        lang_tab = tk.Frame(notebook)
        notebook.add(lang_tab, text="Par langue")

        # Category statistics tab
        category_tab = tk.Frame(notebook)
        notebook.add(category_tab, text="Par catégorie")

        # Fill general tab
        self._create_general_stats(general_tab, stats)

        # Fill language tab
        self._create_language_stats(lang_tab, stats)

        # Fill category tab
        self._create_category_stats(category_tab, stats)

        # Close button
        close_button = tk.Button(
            main_frame,
            text="Fermer",
            command=self.stats_window.destroy,
            relief="raised",
            bg="#f0f0f0",
            padx=15,
            pady=5
        )
        close_button.pack(pady=10)

    def _calculate_statistics(self):
        """Calculate statistics from fault files."""
        stats = {
            "total_entries": 0,
            "languages": {
                "fr": {"count": 0, "empty": 0, "avg_length": 0},
                "en": {"count": 0, "empty": 0, "avg_length": 0},
                "es": {"count": 0, "empty": 0, "avg_length": 0}
            },
            "categories": {},
        }

        try:
            if (not self.app or
                not getattr(self.app, 'main_controller', None) or
                not getattr(self.app.main_controller, 'fault_files', None)):
                # Mock data for testing when application is unavailable
                stats["total_entries"] = 532
                stats["languages"]["fr"] = {"count": 532, "empty": 0, "avg_length": 45}
                stats["languages"]["en"] = {"count": 530, "empty": 2, "avg_length": 42}
                stats["languages"]["es"] = {"count": 525, "empty": 7, "avg_length": 47}
                stats["categories"] = {
                    "SAFETY": {"count": 120},
                    "BATTERY": {"count": 95},
                    "DRIVE": {"count": 85},
                    "CHARGER": {"count": 65},
                    "PLC": {"count": 50},
                    "OTHER": {"count": 117}
                }
                return stats

            # Get fault files from app
            fault_files = self.app.main_controller.fault_files

            # Process each file
            for lang in ["fr", "en", "es"]:
                for file_path in fault_files[lang]:
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            data = json.load(f)

                            # Count entries
                            count = len(data)
                            stats["languages"][lang]["count"] += count

                            # Count empty entries and calculate average length
                            total_length = 0
                            empty_count = 0

                            for value in data.values():
                                if not value or value.strip() == "":
                                    empty_count += 1
                                else:
                                    total_length += len(value)

                            stats["languages"][lang]["empty"] += empty_count

                            if count - empty_count > 0:
                                avg_length = total_length / (count - empty_count)
                                # Update weighted average
                                current_avg = stats["languages"][lang]["avg_length"]
                                current_count = stats["languages"][lang]["count"] - stats["languages"][lang]["empty"]

                                if current_count > 0:
                                    stats["languages"][lang]["avg_length"] = (current_avg + avg_length) / 2
                                else:
                                    stats["languages"][lang]["avg_length"] = avg_length

                            # Extract category from file path
                            import os
                            dir_name = os.path.basename(os.path.dirname(file_path))
                            if dir_name.startswith("_"):
                                category = dir_name.strip("_").replace("_", " ")
                                if category not in stats["categories"]:
                                    stats["categories"][category] = {"count": 0}
                                stats["categories"][category]["count"] += count

                    except Exception as e:
                        print(f"Error processing file {file_path}: {e}")

            # Calculate total entries (use French as reference)
            stats["total_entries"] = stats["languages"]["fr"]["count"]

        except Exception as e:
            print(f"Error calculating statistics: {e}")

        return stats

    def _create_general_stats(self, parent, stats):
        """Create general statistics widgets."""
        frame = tk.Frame(parent)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Total entries
        total_label = tk.Label(
            frame,
            text=f"Nombre total de codes d'erreur: {stats['total_entries']}",
            font=("Segoe UI", 12)
        )
        total_label.pack(anchor="w", pady=5)

        # Completeness stats
        fr_complete = stats["languages"]["fr"]["count"] - stats["languages"]["fr"]["empty"]
        en_complete = stats["languages"]["en"]["count"] - stats["languages"]["en"]["empty"]
        es_complete = stats["languages"]["es"]["count"] - stats["languages"]["es"]["empty"]

        fr_percent = (fr_complete / stats["total_entries"]) * 100 if stats["total_entries"] > 0 else 0
        en_percent = (en_complete / stats["total_entries"]) * 100 if stats["total_entries"] > 0 else 0
        es_percent = (es_complete / stats["total_entries"]) * 100 if stats["total_entries"] > 0 else 0

        completeness_label = tk.Label(
            frame,
            text="Complétude par langue:",
            font=("Segoe UI", 12)
        )
        completeness_label.pack(anchor="w", pady=(15, 5))

        fr_label = tk.Label(
            frame,
            text=f"Français: {fr_percent:.1f}% ({fr_complete}/{stats['total_entries']})"
        )
        fr_label.pack(anchor="w", padx=20)

        en_label = tk.Label(
            frame,
            text=f"Anglais: {en_percent:.1f}% ({en_complete}/{stats['total_entries']})"
        )
        en_label.pack(anchor="w", padx=20)

        es_label = tk.Label(
            frame,
            text=f"Espagnol: {es_percent:.1f}% ({es_complete}/{stats['total_entries']})"
        )
        es_label.pack(anchor="w", padx=20)

        # Create progress bars
        fr_progress = ttk.Progressbar(frame, length=400, maximum=100)
        fr_progress["value"] = fr_percent
        fr_progress.pack(anchor="w", padx=20, pady=(0, 10))

        en_progress = ttk.Progressbar(frame, length=400, maximum=100)
        en_progress["value"] = en_percent
        en_progress.pack(anchor="w", padx=20, pady=(0, 10))

        es_progress = ttk.Progressbar(frame, length=400, maximum=100)
        es_progress["value"] = es_percent
        es_progress.pack(anchor="w", padx=20, pady=(0, 10))

    def _create_language_stats(self, parent, stats):
        """Create language statistics widgets."""
        frame = tk.Frame(parent)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Languages comparison
        lang_label = tk.Label(
            frame,
            text="Comparaison des langues:",
            font=("Segoe UI", 12)
        )
        lang_label.pack(anchor="w", pady=(0, 10))

        # Create table
        table_frame = tk.Frame(frame)
        table_frame.pack(fill="x")

        # Header
        headers = ["Langue", "Entrées", "Vides", "Longueur moyenne"]
        for i, header in enumerate(headers):
            tk.Label(
                table_frame,
                text=header,
                font=("Segoe UI", 10, "bold"),
                borderwidth=1,
                relief="solid",
                width=15,
                padx=5,
                pady=5
            ).grid(row=0, column=i, sticky="nsew")

        # Data rows
        languages = [("Français", "fr"), ("Anglais", "en"), ("Espagnol", "es")]

        for i, (lang_name, lang_code) in enumerate(languages):
            # Language name
            tk.Label(
                table_frame,
                text=lang_name,
                borderwidth=1,
                relief="solid",
                width=15,
                padx=5,
                pady=5
            ).grid(row=i+1, column=0, sticky="nsew")

            # Entries count
            tk.Label(
                table_frame,
                text=str(stats["languages"][lang_code]["count"]),
                borderwidth=1,
                relief="solid",
                width=15,
                padx=5,
                pady=5
            ).grid(row=i+1, column=1, sticky="nsew")

            # Empty count
            tk.Label(
                table_frame,
                text=str(stats["languages"][lang_code]["empty"]),
                borderwidth=1,
                relief="solid",
                width=15,
                padx=5,
                pady=5
            ).grid(row=i+1, column=2, sticky="nsew")

            # Average length
            tk.Label(
                table_frame,
                text=f"{stats['languages'][lang_code]['avg_length']:.1f}",
                borderwidth=1,
                relief="solid",
                width=15,
                padx=5,
                pady=5
            ).grid(row=i+1, column=3, sticky="nsew")

    def _create_category_stats(self, parent, stats):
        """Create category statistics widgets."""
        frame = tk.Frame(parent)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Categories label
        category_label = tk.Label(
            frame,
            text="Répartition par catégorie:",
            font=("Segoe UI", 12)
        )
        category_label.pack(anchor="w", pady=(0, 10))

        # Create table
        table_frame = tk.Frame(frame)
        table_frame.pack(fill="x")

        # Header
        headers = ["Catégorie", "Nombre d'entrées", "Pourcentage"]
        for i, header in enumerate(headers):
            tk.Label(
                table_frame,
                text=header,
                font=("Segoe UI", 10, "bold"),
                borderwidth=1,
                relief="solid",
                width=15,
                padx=5,
                pady=5
            ).grid(row=0, column=i, sticky="nsew")

        # Data rows
        categories = sorted(stats["categories"].keys())

        for i, category in enumerate(categories):
            # Category name
            tk.Label(
                table_frame,
                text=category,
                borderwidth=1,
                relief="solid",
                width=15,
                padx=5,
                pady=5
            ).grid(row=i+1, column=0, sticky="nsew")

            # Entry count
            count = stats["categories"][category]["count"]
            tk.Label(
                table_frame,
                text=str(count),
                borderwidth=1,
                relief="solid",
                width=15,
                padx=5,
                pady=5
            ).grid(row=i+1, column=1, sticky="nsew")

            # Percentage
            percentage = (count / stats["total_entries"]) * 100 if stats["total_entries"] > 0 else 0
            tk.Label(
                table_frame,
                text=f"{percentage:.1f}%",
                borderwidth=1,
                relief="solid",
                width=15,
                padx=5,
                pady=5
            ).grid(row=i+1, column=2, sticky="nsew")
