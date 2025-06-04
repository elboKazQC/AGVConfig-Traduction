#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitaires pour la gestion robuste des erreurs
"""

import logging
import functools
import traceback
import tkinter as tk
from tkinter import messagebox
from typing import Callable, Any, Optional, Dict
from exceptions import FaultEditorError, ErrorCodes, UIError

# Configuration du logger pour les erreurs
error_logger = logging.getLogger('fault_editor.errors')

def safe_execute(operation_name: str, show_user_error: bool = True,
                default_return=None, error_code: str = None):
    """
    Décorateur pour exécuter des opérations de manière sécurisée

    Args:
        operation_name: Nom de l'opération pour les logs
        show_user_error: Si True, affiche l'erreur à l'utilisateur
        default_return: Valeur à retourner en cas d'erreur
        error_code: Code d'erreur à utiliser
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except FaultEditorError as e:
                # Erreurs métier connues
                error_logger.error(f"{operation_name} failed: {e}")
                if show_user_error:
                    show_error_to_user(f"Erreur dans {operation_name}", str(e))
                return default_return
            except Exception as e:
                # Erreurs inattendues
                error_msg = f"Erreur inattendue dans {operation_name}: {str(e)}"
                error_logger.error(error_msg, exc_info=True)
                if show_user_error:
                    show_error_to_user(
                        f"Erreur inattendue dans {operation_name}",
                        f"Une erreur inattendue s'est produite.\n\nDétails: {str(e)}\n\nVeuillez consulter les logs pour plus d'informations."
                    )
                return default_return
        return wrapper
    return decorator

def safe_ui_operation(operation_name: str):
    """
    Décorateur spécialisé pour les opérations de l'interface utilisateur
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except tk.TclError as e:
                error_msg = f"Erreur Tkinter dans {operation_name}: {str(e)}"
                error_logger.error(error_msg)
                # Ne pas montrer les erreurs Tkinter à l'utilisateur car souvent temporaires
                return None
            except Exception as e:
                error_msg = f"Erreur dans {operation_name}: {str(e)}"
                error_logger.error(error_msg, exc_info=True)
                raise UIError(error_msg, operation=operation_name) from e
        return wrapper
    return decorator

def show_error_to_user(title: str, message: str, error_type: str = "error"):
    """
    Affiche une erreur à l'utilisateur de manière robuste

    Args:
        title: Titre de la boîte de dialogue
        message: Message d'erreur
        error_type: Type d'erreur ('error', 'warning', 'info')
    """
    try:
        if error_type == "warning":
            messagebox.showwarning(title, message)
        elif error_type == "info":
            messagebox.showinfo(title, message)
        else:
            messagebox.showerror(title, message)
    except Exception as e:
        # Si même l'affichage d'erreur échoue, logger seulement
        error_logger.critical(f"Impossible d'afficher l'erreur à l'utilisateur: {e}")
        error_logger.critical(f"Erreur originale - {title}: {message}")

def show_file_error(title: str, filepath: str, cause: str):
    """Affiche une erreur liée à un fichier avec la cause probable"""
    message = f"Fichier : {filepath}"
    if cause:
        message += f"\n\nCause possible : {cause}"
    show_error_to_user(title, message)

def safe_file_operation(filepath: str, operation: str):
    """
    Context manager pour les opérations sur fichiers sécurisées

    Usage:
        with safe_file_operation("file.json", "lecture") as safe_op:
            if safe_op.is_safe():
                # faire l'opération
    """
    class SafeFileOperation:
        def __init__(self, filepath: str, operation: str):
            self.filepath = filepath
            self.operation = operation
            self.error = None

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type:
                self.error = exc_val
                error_logger.error(f"Erreur lors de {self.operation} de {self.filepath}: {exc_val}")
                return True  # Supprime l'exception
            return False

        def is_safe(self) -> bool:
            return self.error is None

        def get_error(self) -> Optional[Exception]:
            return self.error

    return SafeFileOperation(filepath, operation)

def validate_json_structure(data: Dict, required_fields: Dict[str, type]) -> bool:
    """
    Valide la structure d'un dictionnaire JSON

    Args:
        data: Données à valider
        required_fields: Dictionnaire {nom_champ: type_attendu}

    Returns:
        True si valide, raise JSONValidationError sinon
    """
    from exceptions import JSONValidationError

    if not isinstance(data, dict):
        raise JSONValidationError(
            "Les données doivent être un dictionnaire",
            expected="dict",
            actual=type(data).__name__,
            error_code=ErrorCodes.JSON_STRUCTURE_ERROR
        )

    for field_name, expected_type in required_fields.items():
        if field_name not in data:
            raise JSONValidationError(
                f"Champ requis manquant: {field_name}",
                field=field_name,
                expected=expected_type.__name__,
                error_code=ErrorCodes.JSON_VALIDATION_ERROR
            )

        if not isinstance(data[field_name], expected_type):
            raise JSONValidationError(
                f"Type incorrect pour le champ {field_name}",
                field=field_name,
                expected=expected_type.__name__,
                actual=type(data[field_name]).__name__,
                error_code=ErrorCodes.JSON_VALIDATION_ERROR
            )

    return True

def robust_widget_destroy(widget):
    """
    Détruit un widget Tkinter de manière robuste
    """
    if widget is None:
        return

    try:
        if hasattr(widget, 'winfo_exists') and widget.winfo_exists():
            widget.destroy()
    except tk.TclError:
        # Widget déjà détruit ou invalide
        traceback.print_exc()  # handled for visibility
    except Exception as e:
        error_logger.warning(f"Erreur lors de la destruction du widget: {e}")

def retry_operation(max_retries: int = 3, delay: float = 0.5):
    """
    Décorateur pour retry automatique des opérations
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        error_logger.warning(f"Tentative {attempt + 1} échouée pour {func.__name__}: {e}")
                        import time
                        time.sleep(delay)
                    else:
                        error_logger.error(f"Toutes les tentatives échouées pour {func.__name__}: {e}")

            raise last_error
        return wrapper
    return decorator
