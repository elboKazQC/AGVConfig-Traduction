# Gestionnaire de fichiers pour l'application Fault Editor
"""
Ce module gère toutes les opérations sur les fichiers JSON.
Utilisez ces fonctions pour charger, sauvegarder et manipuler les fichiers.
"""

import json
import os
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from models.data_models import FaultData, FileMetadata

logger = logging.getLogger(__name__)

class FileManager:
    """Gestionnaire principal pour les opérations sur fichiers"""

    def __init__(self):
        self.base_directory: Optional[str] = None
        self.file_map: Dict[str, str] = {}
        # Store lists of fault files grouped by language for easy access
        self.fault_files: Dict[str, List[str]] = {"fr": [], "en": [], "es": []}

    def initialize_directory(self, directory: str) -> bool:
        """Initialise le gestionnaire avec un répertoire de base"""
        try:
            self.base_directory = directory
            self.file_map = {}
            self._scan_directory(directory)
            logger.info(f"Répertoire initialisé : {directory}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du répertoire : {e}")
            return False

    def _scan_directory(self, directory: str):
        """Scanne le répertoire pour trouver les fichiers JSON"""
        # Reset fault file lists
        self.fault_files = {"fr": [], "en": [], "es": []}

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.json'):
                    full_path = os.path.join(root, file)
                    self.file_map[file] = full_path

                    # Detect language from filename pattern faults_*_<lang>.json
                    match = re.match(r".*_(fr|en|es)\.json$", file)
                    if match:
                        lang = match.group(1)
                        self.fault_files.setdefault(lang, []).append(full_path)

    def load_json_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """Charge un fichier JSON"""
        if filename not in self.file_map:
            logger.error(f"Fichier non trouvé : {filename}")
            return None

        try:
            with open(self.file_map[filename], "r", encoding="utf-8") as f:
                content = json.load(f)
            logger.info(f"Fichier chargé : {filename}")
            return content
        except Exception as e:
            logger.error(f"Erreur lors du chargement de {filename}: {e}")
            return None

    def save_json_file(self, filename: str, data: Dict[str, Any]) -> bool:
        """Sauvegarde un fichier JSON"""
        if filename not in self.file_map:
            logger.error(f"Impossible de sauvegarder : fichier non trouvé {filename}")
            return False

        try:
            with open(self.file_map[filename], "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Fichier sauvegardé : {filename}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de {filename}: {e}")
            return False

    def get_file_path(self, filename: str) -> Optional[str]:
        """Retourne le chemin complet d'un fichier"""
        return self.file_map.get(filename)

    def get_all_files(self) -> List[str]:
        """Retourne la liste de tous les fichiers trouvés"""
        return list(self.file_map.keys())

class FlatFileManager:
    """Gestionnaire spécialisé pour les fichiers JSON plats"""

    @staticmethod
    def load_flat_json_files(fr_path: str, en_path: str, es_path: str) -> Tuple[Dict[str, str], Dict[str, str], Dict[str, str], List[str]]:
        """Charge trois fichiers JSON plats et retourne les traductions et clés"""
        translations = {"fr": {}, "en": {}, "es": {}}

        # Charger les fichiers
        for lang, path in [("fr", fr_path), ("en", en_path), ("es", es_path)]:
            try:
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        translations[lang] = json.load(f)
                        logger.info(f"Fichier {lang} chargé : {path}")
                else:
                    logger.warning(f"Fichier {lang} non trouvé : {path}")
            except Exception as e:
                logger.error(f"Erreur lors du chargement du fichier {lang} : {e}")

        # Obtenir toutes les clés uniques
        all_keys = set()
        for trans in translations.values():
            all_keys.update(trans.keys())

        return translations["fr"], translations["en"], translations["es"], sorted(list(all_keys))

    @staticmethod
    def save_flat_json_files(fr_path: str, en_path: str, es_path: str,
                           fr_data: Dict[str, str], en_data: Dict[str, str], es_data: Dict[str, str]) -> bool:
        """Sauvegarde trois fichiers JSON plats"""
        try:
            files_to_save = [
                (fr_path, fr_data),
                (en_path, en_data),
                (es_path, es_data)
            ]

            for path, data in files_to_save:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info("Fichiers plats sauvegardés avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des fichiers plats : {e}")
            return False

def path_to_filename(path: List[int], language: str) -> str:
    """Convertit un chemin en nom de fichier"""
    return f"faults_{'_'.join(str(p).zfill(3) for p in path)}_{language}.json"

def filename_to_path(filename: str) -> Optional[List[int]]:
    """Convertit un nom de fichier en chemin"""
    try:
        # Exemple: faults_000_001_002_003_fr.json
        parts = filename.replace('.json', '').split('_')
        if len(parts) >= 5 and parts[0] == 'faults':
            return [int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])]
    except (ValueError, IndexError):
        pass
    return None
