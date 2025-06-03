# Modèles de données pour l'application Fault Editor
"""
Ce module contient les classes qui représentent les données de l'application.
Utilisez ces classes pour structurer et valider les données.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class FaultData:
    """Représente une entrée de défaut dans les fichiers JSON"""
    description: str = ""
    is_expandable: bool = False
    fault_id: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FaultData':
        """Crée une instance FaultData à partir d'un dictionnaire"""
        return cls(
            description=data.get("Description", ""),
            is_expandable=data.get("IsExpandable", False),
            fault_id=data.get("Id", 0)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'instance en dictionnaire"""
        return {
            "Description": self.description,
            "IsExpandable": self.is_expandable,
            "Id": self.fault_id
        }

@dataclass
class FileMetadata:
    """Métadonnées d'un fichier JSON"""
    filename: str
    filepath: str
    language: str
    path_components: List[int]

    def get_display_name(self) -> str:
        """Retourne le nom d'affichage du fichier"""
        return f"{self.filename} ({self.language})"

@dataclass
class SearchResult:
    """Résultat d'une recherche"""
    column_index: int
    row_index: int
    fault_data: FaultData
    match_text: str
    file_metadata: FileMetadata

class ApplicationState:
    """État global de l'application"""

    def __init__(self):
        self.current_language = "fr"
        self.current_path = [0, 255, 255, 255]
        self.base_directory: Optional[str] = None
        self.current_file_path: Optional[str] = None
        self.file_map: Dict[str, str] = {}
        self.data_map: Dict[str, Dict[str, Any]] = {}
        self.path_map: Dict[str, str] = {}
        self.editing_info: Optional[Dict[str, Any]] = None
        self.search_results: List[SearchResult] = []
        self.current_search_index = -1

    def is_editing(self) -> bool:
        """Vérifie si une édition est en cours"""
        return self.editing_info is not None

    def get_current_filename(self) -> str:
        """Génère le nom de fichier basé sur le chemin actuel"""
        return f"faults_{'_'.join(str(p).zfill(3) for p in self.current_path)}_{self.current_language}.json"

    def reset_search(self):
        """Réinitialise les résultats de recherche"""
        self.search_results = []
        self.current_search_index = -1
