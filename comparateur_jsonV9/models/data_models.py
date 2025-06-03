#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modèles de données pour l'application Fault Editor

Ce module contient les classes qui représentent les données de l'application.
Utilisez ces classes pour structurer et valider les données.
"""

from typing import List, Dict, Any, Optional, Iterator
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class FaultData:
    """Représente une entrée de défaut dans les fichiers JSON"""
    fault_code: str
    description: str = ""
    severity: str = "info"
    category: str = "general"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FaultData':
        """Crée une instance FaultData à partir d'un dictionnaire"""
        return cls(
            fault_code=data.get("FaultCode", ""),
            description=data.get("Description", ""),
            severity=data.get("Severity", "info"),
            category=data.get("Category", "general")
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'instance en dictionnaire"""
        return {
            "FaultCode": self.fault_code,
            "Description": self.description,
            "Severity": self.severity,
            "Category": self.category
        }

    def __iter__(self) -> Iterator[Any]:
        """Rendre FaultData itérable."""
        yield self.fault_code
        yield self.description
        yield self.severity
        yield self.category

@dataclass
class FileMetadata:
    """Métadonnées d'un fichier JSON"""
    filename: str
    filepath: str
    last_modified: str
    file_size: int
    language: str
    path_components: List[int]

    def get_display_name(self) -> str:
        """Retourne le nom d'affichage du fichier"""
        return f"{self.filename} ({self.language})"

    def __iter__(self) -> Iterator[Any]:
        """Rendre FileMetadata itérable."""
        yield self.filename
        yield self.filepath
        yield self.last_modified
        yield self.file_size
        yield self.language
        yield from iter(self.path_components)

@dataclass
class SearchResult:
    """Résultat d'une recherche"""
    query: str
    file_path: str
    line_number: int
    context: str
    column_index: int
    row_index: int
    fault_data: FaultData
    match_text: str
    file_metadata: FileMetadata

    def __iter__(self) -> Iterator[Any]:
        """Rendre SearchResult itérable."""
        yield self.query
        yield self.file_path
        yield self.line_number
        yield self.context
        yield self.column_index
        yield self.row_index
        yield from iter(self.fault_data)
        yield self.match_text
        yield from iter(self.file_metadata)

@dataclass
class ApplicationState:
    """État global de l'application"""

    base_directory: Optional[str] = None
    current_language: str = "fr"
    selected_files: List[str] = field(default_factory=list)
    last_modified: Optional[datetime] = None
    editing_info: Optional[Dict[str, Any]] = None
    current_path: List[int] = field(default_factory=lambda: [0, 255, 255, 255])

    def __post_init__(self):
        if self.selected_files is None:
            self.selected_files = []
        if self.editing_info is None:
            self.editing_info = {}

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
