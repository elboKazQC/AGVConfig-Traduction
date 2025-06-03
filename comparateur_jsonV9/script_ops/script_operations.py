"""
Script Operations Module

This module handles external script execution for the Fault Editor application.
It provides utilities for running Python scripts, handling their output,
and managing script-related UI interactions.

Author: AI Assistant
Created: 2024
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Dict, List, Optional, Tuple, Any, Callable

# Import modules
from config.constants import Colors, Fonts
from models.data_models import ApplicationState
from ui.components import ProgressDialog

# Configure logging
logger = logging.getLogger(__name__)


class ScriptRunner:
    """
    Handles execution of external Python scripts with progress tracking and error handling.
    """

    def __init__(self, parent, status_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize the script runner.

        Args:
            parent: Parent tkinter widget
            status_callback: Optional callback function to update status messages
        """
        self.parent = parent
        self.status_callback = status_callback
        self.script_dir = os.path.dirname(os.path.abspath(__file__))

    def run_command(self, cmd: List[str], desc: str = "") -> bool:
        """
        Run a command with progress tracking and error handling.

        Args:
            cmd: Command list to execute
            desc: Description of the operation

        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"Exécution de la commande: {' '.join(cmd)}")
        self._set_tools_enabled("disabled")

        # Show loading popup
        progress_dialog = ProgressDialog(
            self.parent,
            title="Exécution en cours",
            message=f"{desc} en cours...",
            total=100,
            indeterminate=True
        )

        try:
            # Get script directory
            script_dir = os.path.dirname(os.path.abspath(__file__))

            # Modify command to include full script path
            if cmd[0] == "python":
                cmd[1] = os.path.join(script_dir, cmd[1])

            self._update_status(f"⏳ Exécution : {desc} ...")

            # Set up environment
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"

            logger.info(f"Exécution dans le dossier: {script_dir}")

            # Run the command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                cwd=script_dir
            )

            # Display script output in console
            if result.stdout:
                print(f"\n📋 Sortie de {desc}:")
                print("=" * 50)
                print(result.stdout)
                print("=" * 50)

            if result.returncode == 0:
                logger.info(f"Commande terminée avec succès: {desc}")
                logger.debug(f"Sortie de la commande:\n{result.stdout}")

                # Analyze output for translation indicators
                success_indicators = ["✅", "🎉", "mis à jour", "terminée avec succès"]
                warning_indicators = ["⚠️", "aucune", "déjà", "identique"]

                # Show results in dialog
                if result.stdout:
                    self._show_script_results(f"✅ {desc} - Terminé", result.stdout, True)

                if any(indicator in result.stdout for indicator in success_indicators):
                    if any(indicator in result.stdout for indicator in warning_indicators):
                        self._update_status(f"⚠️ {desc} - Voir détails dans la fenêtre")
                    else:
                        self._update_status(f"✅ {desc} - Traductions effectuées")
                else:
                    self._update_status(f"⚠️ {desc} - Aucune traduction détectée")

                return True

            else:
                logger.error(f"Erreur lors de l'exécution de {desc}: {result.stderr}")

                # Prepare complete error message
                error_message = f"Code de retour: {result.returncode}\n\n"
                if result.stderr:
                    error_message += f"Erreur:\n{result.stderr}\n\n"
                if result.stdout:
                    error_message += f"Sortie:\n{result.stdout}"
                else:
                    error_message += "Aucune sortie disponible"

                print(f"\n❌ Erreur lors de {desc}:")
                print("=" * 50)
                print(error_message)
                print("=" * 50)

                # Show error in dialog
                self._show_script_results(f"❌ Erreur - {desc}", error_message, False)
                self._update_status(f"❌ Erreur : {desc}")
                return False

        except Exception as e:
            logger.error(f"Exception lors de l'exécution de {desc}: {str(e)}")
            print(f"\n❌ Exception lors de {desc}: {str(e)}")
            self._update_status(f"❌ Exception : {desc}")
            return False

        finally:
            progress_dialog.close()
            self._set_tools_enabled("normal")

    def run_command_with_fix_option(self, cmd: List[str], base_dir: str, desc: str = "") -> bool:
        """
        Run a command with automatic error fixing option.

        Args:
            cmd: Command list to execute
            base_dir: Base directory for operations
            desc: Description of the operation

        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"Exécution de la commande: {' '.join(cmd)}")
        self._set_tools_enabled("disabled")

        # Show loading popup
        progress_dialog = ProgressDialog(
            self.parent,
            title="Vérification en cours",
            message=f"{desc} en cours...",
            total=100,
            indeterminate=True
        )

        try:
            # Get script directory
            script_dir = os.path.dirname(os.path.abspath(__file__))

            # Modify command to include full script path
            if cmd[0] == "python":
                cmd[1] = os.path.join(script_dir, cmd[1])

            self._update_status(f"⏳ Exécution : {desc} ...")

            # Set up environment
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"

            logger.info(f"Exécution dans le dossier: {script_dir}")

            # Run the command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                cwd=script_dir
            )

            # Display script output in console
            if result.stdout:
                print(f"\n📋 Sortie de {desc}:")
                print("=" * 50)
                print(result.stdout)
                print("=" * 50)

            if result.returncode == 0:
                logger.info(f"Commande terminée avec succès: {desc}")
                self._update_status(f"✅ {desc} - Aucune erreur détectée")

                # Show results in dialog
                if result.stdout:
                    self._show_script_results(f"✅ {desc} - Terminé", result.stdout, True)
                return True

            else:
                logger.warning(f"Erreurs détectées lors de {desc}")

                # Analyze output for metadata errors
                has_metadata_errors = ("🟠 Erreurs métadonnées" in result.stdout and
                                     "Erreurs métadonnées : 0" not in result.stdout)

                if has_metadata_errors:
                    # Close loading popup
                    progress_dialog.close()

                    # Offer to fix automatically
                    response = messagebox.askyesnocancel(
                        "Erreurs détectées",
                        f"Des erreurs de cohérence ont été détectées.\n\n"
                        f"Voulez-vous :\n"
                        f"• OUI : Corriger automatiquement les erreurs de métadonnées\n"
                        f"• NON : Voir seulement le rapport d'erreurs\n"
                        f"• ANNULER : Fermer",
                        icon='question'
                    )

                    if response is True:  # YES - Fix automatically
                        return self.run_fix_coherence_errors(base_dir)
                    elif response is False:  # NO - Show report
                        pass  # Continue to show report
                    else:  # CANCEL
                        self._update_status("❌ Vérification annulée")
                        return False

                # Prepare complete error message
                error_message = f"Code de retour: {result.returncode}\n\n"
                if result.stderr:
                    error_message += f"Erreur:\n{result.stderr}\n\n"
                if result.stdout:
                    error_message += f"Sortie:\n{result.stdout}"
                else:
                    error_message += "Aucune sortie disponible"

                # Show error in dialog
                self._show_script_results(f"⚠️ Erreurs détectées - {desc}", error_message, False)
                self._update_status(f"⚠️ Erreurs détectées : {desc}")
                return False

        except Exception as e:
            logger.error(f"Exception lors de l'exécution de {desc}: {str(e)}")
            print(f"\n❌ Exception lors de {desc}: {str(e)}")
            self._update_status(f"❌ Exception : {desc}")
            return False

        finally:
            progress_dialog.close()
            self._set_tools_enabled("normal")

    def run_sync_script(self, file_path: str) -> bool:
        """
        Run synchronization script for a specific file.

        Args:
            file_path: Path to the file to synchronize

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not file_path:
                self._update_status("❌ Aucun fichier sélectionné")
                print("❌ Aucun fichier sélectionné pour la synchronisation")
                return False

            # Use full file path
            source_file = file_path

            if not os.path.exists(source_file):
                error_msg = f"❌ Fichier introuvable : {source_file}"
                self._update_status("❌ Fichier introuvable")
                print(error_msg)
                return False

            source_dir = os.path.dirname(source_file)
            print(f"📂 Répertoire de travail pour la synchronisation : {source_dir}")

            # Call sync_one.py with full file path
            script_dir = os.path.dirname(os.path.abspath(__file__))
            result = subprocess.run(
                ["python", os.path.join(script_dir, "sync_one.py"), source_file],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=source_dir
            )

            if result.returncode == 0:
                self._update_status("✅ Synchronisation réussie")
                print("\nSortie du script :")
                print(result.stdout)
                return True
            else:
                self._update_status("❌ Erreur lors de la synchronisation")
                print("\nErreur lors de la synchronisation :")
                print(result.stderr)
                return False

        except Exception as e:
            self._update_status("❌ Erreur de synchronisation")
            print(f"\n❌ Erreur lors de la synchronisation : {e}")
            return False

    def run_fix_coherence_errors(self, base_dir: str) -> bool:
        """
        Run coherence error fixing script.

        Args:
            base_dir: Base directory for operations

        Returns:
            bool: True if successful, False otherwise
        """
        cmd = ["python", "fix_coherence_errors.py", base_dir]
        return self.run_command(cmd, desc="Correction des erreurs de cohérence")

    def _show_script_results(self, title: str, content: str, is_success: bool = True):
        """
        Show script results in a dialog window.

        Args:
            title: Dialog title
            content: Content to display
            is_success: Whether the operation was successful
        """
        popup = tk.Toplevel(self.parent)
        popup.title(title)
        popup.geometry("800x600")
        popup.transient(self.parent)
        popup.resizable(True, True)

        # Configure background color based on success
        bg_color = Colors.BG_MAIN
        text_color = Colors.FG_TEXT if is_success else Colors.RED
        popup.configure(bg=bg_color)

        # Title frame
        title_frame = tk.Frame(popup, bg=bg_color)
        title_frame.pack(fill="x", padx=10, pady=5)

        title_label = tk.Label(
            title_frame,
            text=title,
            font=Fonts.TITLE,
            bg=bg_color,
            fg=text_color
        )
        title_label.pack()

        # Text area with scrollbar
        text_frame = tk.Frame(popup, bg=bg_color)
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

        # Insert content
        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)

        # Close button
        button_frame = tk.Frame(popup, bg=bg_color)
        button_frame.pack(fill="x", padx=10, pady=5)

        close_btn = ttk.Button(button_frame, text="Fermer", command=popup.destroy)
        close_btn.pack(side="right")

        # Center the window
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
        y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")

    def _update_status(self, message: str):
        """Update status message."""
        if self.status_callback:
            self.status_callback(message)

    def _set_tools_enabled(self, state: str):
        """Enable/disable tools in the parent interface."""
        # This would be implemented based on the parent's interface
        # For now, we'll pass since this is handled by the main application
        pass


class ScriptOperations:
    """
    High-level operations using various scripts.
    """

    def __init__(self, parent, base_dir: str, status_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize script operations.

        Args:
            parent: Parent tkinter widget
            base_dir: Base directory for operations
            status_callback: Optional callback function to update status messages
        """
        self.parent = parent
        self.base_dir = base_dir
        self.runner = ScriptRunner(parent, status_callback)

    def sync_all_files(self) -> bool:
        """Synchronize all files."""
        if not self.base_dir:
            if self.runner.status_callback:
                self.runner.status_callback("❌ Aucun dossier ouvert")
            return False

        cmd = ["python", "sync_all.py", self.base_dir]
        return self.runner.run_command(cmd, desc="Synchroniser tous les fichiers")

    def sync_one_file(self, filename: str) -> bool:
        """
        Synchronize a single file.

        Args:
            filename: Name of the file to synchronize

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.base_dir:
            if self.runner.status_callback:
                self.runner.status_callback("❌ Aucun dossier ouvert")
            return False

        if not filename.strip():
            if self.runner.status_callback:
                self.runner.status_callback("❌ Nom de fichier manquant")
            return False

        cmd = ["python", "sync_one_consolidated.py", self.base_dir, filename.strip()]
        return self.runner.run_command(cmd, desc=f"Synchroniser {filename}")

    def generate_file(self, filename: str, source_lang: str, target_lang: str) -> bool:
        """
        Generate a file in target language from source language.

        Args:
            filename: Name of the file
            source_lang: Source language code
            target_lang: Target language code

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.base_dir:
            if self.runner.status_callback:
                self.runner.status_callback("❌ Aucun dossier ouvert")
            return False

        if not (filename and source_lang and target_lang):
            if self.runner.status_callback:
                self.runner.status_callback("❌ Arguments generer_fichier manquants")
            return False

        cmd = ["python", "generer_fichier.py", self.base_dir, filename, source_lang, target_lang]
        return self.runner.run_command(cmd, desc=f"Générer fichier {filename} {source_lang}->{target_lang}")

    def generate_missing_files(self) -> bool:
        """Generate missing files."""
        if not self.base_dir:
            if self.runner.status_callback:
                self.runner.status_callback("❌ Aucun dossier ouvert")
            return False

        cmd = ["python", "generer_manquant.py", self.base_dir]
        return self.runner.run_command(cmd, desc="Générer les fichiers manquants")

    def check_coherence(self) -> bool:
        """Check file coherence."""
        if not self.base_dir:
            if self.runner.status_callback:
                self.runner.status_callback("❌ Aucun dossier ouvert")
            return False

        cmd = ["python", "check_coherence.py", self.base_dir]
        return self.runner.run_command_with_fix_option(cmd, self.base_dir, desc="Vérifier la cohérence")

    def check_spelling(self) -> bool:
        """Check spelling."""
        if not self.base_dir:
            if self.runner.status_callback:
                self.runner.status_callback("❌ Aucun dossier ouvert")
            return False

        cmd = ["python", "check_spelling.py", self.base_dir]
        return self.runner.run_command(cmd, desc="Vérification orthographique")

    def fix_headers(self) -> bool:
        """Fix file headers."""
        if not self.base_dir:
            if self.runner.status_callback:
                self.runner.status_callback("❌ Aucun dossier ouvert")
            return False

        cmd = ["python", "fix_headers.py", self.base_dir]
        return self.runner.run_command(cmd, desc="Corriger les headers")

    def sync_specific_file(self, file_path: str) -> bool:
        """
        Synchronize a specific file by path.

        Args:
            file_path: Full path to the file to synchronize

        Returns:
            bool: True if successful, False otherwise
        """
        return self.runner.run_sync_script(file_path)
