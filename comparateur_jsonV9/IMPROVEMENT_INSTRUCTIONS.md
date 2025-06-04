# Instructions pour appliquer les améliorations d'error handling

## Fichiers créés:
1. `exceptions.py` - Hiérarchie d'exceptions personnalisées
2. `error_utils.py` - Utilitaires pour la gestion d'erreurs
3. `apply_improvements.py` - Ce script

## Étapes pour appliquer les améliorations:

### 1. Sauvegarde automatique
Une sauvegarde de votre app.py actuelle sera créée automatiquement.

### 2. Améliorations à appliquer manuellement:

#### A. Remplacer les imports au début de app.py:
```python
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import json
import subprocess
from functools import partial
from translate import traduire
import re
import logging
from datetime import datetime

# Imports pour la gestion d'erreurs améliorée
from exceptions import (
    FaultEditorError, FileOperationError, JSONValidationError,
    TranslationError, UIError, ErrorCodes
)
from error_utils import (
    safe_execute, safe_ui_operation, show_error_to_user,
    safe_file_operation, validate_json_structure, robust_widget_destroy,
    retry_operation
)
```

#### B. Remplacer la configuration du logging:
```python

# Créer le dossier logs s'il n'existe pas
os.makedirs('logs', exist_ok=True)

# Configuration du logging améliorée
def setup_logging():
    """Configure le système de logging de manière robuste"""
    log_format = '[%(asctime)s] %(name)s - %(levelname)s: %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    # Configuration du logger principal
    logger = logging.getLogger('fault_editor')
    logger.setLevel(logging.INFO)

    # Éviter les doublons de handlers
    if logger.handlers:
        logger.handlers.clear()

    try:
        # Handler pour fichier
        file_handler = logging.FileHandler('logs/app_debug.log', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(log_format, date_format))
        logger.addHandler(file_handler)

        # Handler pour console (seulement les erreurs importantes)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(logging.Formatter(log_format, date_format))
        logger.addHandler(console_handler)

    except Exception as e:
        print(f"⚠️ Erreur configuration logging: {e}")
        # Fallback: logging basique
        logging.basicConfig(level=logging.INFO, format=log_format, datefmt=date_format)

    return logger

# Initialiser le logging
logger = setup_logging()
```

#### C. Ajouter les méthodes améliorées dans la classe FaultEditor:
```python

    @safe_execute("Chargement de fichier", show_user_error=True)
    def load_json_file(self, filename):
        """Charge un fichier JSON de manière sécurisée"""
        if not filename:
            raise FileOperationError(
                "Nom de fichier non spécifié",
                error_code=ErrorCodes.FILE_NOT_FOUND
            )

        if not os.path.exists(filename):
            raise FileOperationError(
                f"Le fichier {filename} n'existe pas",
                filepath=filename,
                operation="lecture",
                error_code=ErrorCodes.FILE_NOT_FOUND
            )

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validation de la structure
            self._validate_json_structure(data)

            self.json_data = data
            self.current_file = filename

            logger.info(f"Fichier chargé avec succès: {filename}")
            self.update_info_frame()
            self.populate_tree()

            return True

        except json.JSONDecodeError as e:
            raise JSONValidationError(
                f"Fichier JSON invalide: {str(e)}",
                filepath=filename,
                error_code=ErrorCodes.JSON_PARSE_ERROR
            )
        except UnicodeDecodeError as e:
            raise FileOperationError(
                f"Erreur d'encodage du fichier: {str(e)}",
                filepath=filename,
                operation="lecture",
                error_code=ErrorCodes.FILE_READ_ERROR
            )
        except PermissionError as e:
            raise FileOperationError(
                f"Permissions insuffisantes: {str(e)}",
                filepath=filename,
                operation="lecture",
                error_code=ErrorCodes.FILE_PERMISSION_ERROR
            )

    def _validate_json_structure(self, data):
        """Valide la structure du JSON chargé"""
        required_structure = {
            "Header": dict,
            "FaultDetailList": list
        }

        validate_json_structure(data, required_structure)

        # Validation plus spécifique du Header
        if "Header" in data:
            header_required = {
                "Language": str,
                "FileName": str
            }
            validate_json_structure(data["Header"], header_required)

    @safe_execute("Sauvegarde de fichier", show_user_error=True)
    def save_json_file(self, filename=None):
        """Sauvegarde le fichier JSON de manière sécurisée"""
        if not self.json_data:
            raise FileOperationError(
                "Aucune donnée à sauvegarder",
                error_code=ErrorCodes.JSON_STRUCTURE_ERROR
            )

        target_file = filename or self.current_file
        if not target_file:
            raise FileOperationError(
                "Nom de fichier non spécifié pour la sauvegarde",
                error_code=ErrorCodes.FILE_WRITE_ERROR
            )

        # Créer une sauvegarde temporaire
        backup_file = target_file + ".backup"

        try:
            # Valider les données avant sauvegarde
            self._validate_json_structure(self.json_data)

            # Sauvegarder dans un fichier temporaire d'abord
            temp_file = target_file + ".tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.json_data, f, indent=2, ensure_ascii=False)

            # Si la sauvegarde temporaire réussit, remplacer le fichier original
            if os.path.exists(target_file):
                shutil.move(target_file, backup_file)

            shutil.move(temp_file, target_file)

            # Supprimer la sauvegarde si tout s'est bien passé
            if os.path.exists(backup_file):
                os.remove(backup_file)

            logger.info(f"Fichier sauvegardé avec succès: {target_file}")
            show_error_to_user("Sauvegarde", "Fichier sauvegardé avec succès", "info")
            return True

        except Exception as e:
            # Restaurer depuis la sauvegarde en cas d'erreur
            if os.path.exists(backup_file):
                if os.path.exists(target_file):
                    os.remove(target_file)
                shutil.move(backup_file, target_file)

            # Nettoyer le fichier temporaire
            if os.path.exists(temp_file):
                os.remove(temp_file)

            raise FileOperationError(
                f"Erreur lors de la sauvegarde: {str(e)}",
                filepath=target_file,
                operation="écriture",
                error_code=ErrorCodes.FILE_WRITE_ERROR
            )


    @safe_ui_operation("Création des widgets")
    def create_widgets(self):
        """Crée les widgets de l'interface de manière sécurisée"""
        try:
            # Code existant de création des widgets...
            # (Cette méthode sera mise à jour pour inclure la gestion d'erreurs robuste)

            # Exemple d'amélioration pour la création de widgets
            self._create_menu_bar()
            self._create_toolbar()
            self._create_main_content()
            self._create_status_bar()

        except Exception as e:
            logger.error(f"Erreur lors de la création des widgets: {e}")
            raise UIError(
                f"Impossible de créer l'interface: {str(e)}",
                operation="création des widgets",
                error_code=ErrorCodes.WIDGET_CREATION_ERROR
            )

    @safe_ui_operation("Mise à jour de l'interface")
    def update_info_frame(self):
        """Met à jour les informations affichées de manière sécurisée"""
        try:
            if not hasattr(self, 'info_frame') or not self.info_frame:
                return

            # Nettoyer les anciens widgets de manière robuste
            for child in self.info_frame.winfo_children():
                robust_widget_destroy(child)

            # Mettre à jour les informations
            if self.json_data and "Header" in self.json_data:
                header = self.json_data["Header"]

                # Affichage sécurisé des informations
                self._display_safe_info("Langue", header.get("Language", "Non spécifiée"))
                self._display_safe_info("Fichier", header.get("FileName", "Non spécifié"))

                # Compter les éléments de manière sécurisée
                fault_count = 0
                if "FaultDetailList" in self.json_data:
                    fault_count = len(self.json_data["FaultDetailList"])

                self._display_safe_info("Nombre de défauts", str(fault_count))

        except Exception as e:
            logger.warning(f"Erreur lors de la mise à jour de l'interface: {e}")
            # Ne pas faire échouer l'application pour une erreur d'affichage

    def _display_safe_info(self, label, value):
        """Affiche une information de manière sécurisée"""
        try:
            info_label = tk.Label(
                self.info_frame,
                text=f"{label}: {value}",
                bg=COL_BG_MAIN,
                fg=COL_FG_TEXT,
                font=FONT_DEFAULT
            )
            info_label.pack(anchor="w", padx=5, pady=2)
        except Exception as e:
            logger.warning(f"Impossible d'afficher {label}: {e}")

    def safe_destroy(self):
        """Détruit l'application de manière sécurisée"""
        try:
            logger.info("Fermeture de l'application...")

            # Sauvegarder les paramètres si nécessaire
            self._save_user_preferences()

            # Nettoyer les ressources
            self._cleanup_resources()

            # Détruire la fenêtre principale
            if hasattr(self, 'root') and self.root:
                robust_widget_destroy(self.root)

        except Exception as e:
            logger.error(f"Erreur lors de la fermeture: {e}")
            # Forcer la fermeture même en cas d'erreur
            try:
                if hasattr(self, 'root') and self.root:
                    self.root.quit()
            except:
                pass

    def _save_user_preferences(self):
        """Sauvegarde les préférences utilisateur"""
        try:
            # Code pour sauvegarder les préférences
            pass
        except Exception as e:
            logger.warning(f"Impossible de sauvegarder les préférences: {e}")

    def _cleanup_resources(self):
        """Nettoie les ressources de l'application"""
        try:
            # Fermer les connexions, nettoyer les fichiers temporaires, etc.
            pass
        except Exception as e:
            logger.warning(f"Erreur lors du nettoyage des ressources: {e}")
```

### 3. Modifications des méthodes existantes:

#### A. Dans `__init__`:
- Ajouter un try/except autour de `create_widgets()`
- Ajouter une gestion d'erreur pour l'initialisation

#### B. Dans les gestionnaires d'événements:
- Entourer le code avec `@safe_ui_operation`
- Remplacer les `except Exception` génériques par des exceptions spécifiques

#### C. Dans les opérations de traduction:
- Utiliser `TranslationError` au lieu d'`Exception`
- Ajouter des retry pour les échecs temporaires

### 4. Test des améliorations:

Après avoir appliqué les modifications:
1. Lancer l'application pour vérifier qu'elle démarre
2. Tester le chargement d'un fichier valide
3. Tester le chargement d'un fichier invalide (doit afficher une erreur claire)
4. Tester la sauvegarde
5. Vérifier les logs dans le dossier `logs/`

### 5. Bénéfices attendus:

- ✅ Erreurs plus claires et spécifiques
- ✅ Récupération automatique des erreurs temporaires
- ✅ Logging structuré et détaillé
- ✅ Interface qui ne crash plus en cas d'erreur
- ✅ Sauvegardes automatiques pour éviter la perte de données
- ✅ Validation robuste des données JSON

### 6. Surveillance:

Après déploiement, surveillez le fichier `logs/app_debug.log` pour:
- Identifier les erreurs récurrentes
- Optimiser les opérations problématiques
- Améliorer l'expérience utilisateur

---
Généré le: 2025-06-04 07:14:47
