# Configuration et constantes pour l'application Fault Editor
"""
Ce module contient toutes les constantes de configuration de l'application.
Modifiez ces valeurs pour personnaliser l'apparence et le comportement.
"""

# Couleurs de l'interface
class Colors:
    """Constantes de couleurs pour l'interface utilisateur"""
    BG_MAIN = "#2a2a2a"           # Fond principal plus foncé
    BG_TOPBAR = "#1c1c1c"         # Barre supérieure plus foncée
    BG_COLUMN = "#2a2a2a"         # Colonnes plus foncées
    BG_ROW = "#333333"            # Lignes plus foncées
    BG_ROW_ALT = "#3a3a3a"        # Lignes alternées plus foncées
    BG_ROW_HOVER = "#404040"      # Survol plus foncé
    FG_TEXT = "#ffffff"           # Texte blanc
    EDIT_BG = "#404040"           # Fond d'édition plus foncé
    EDIT_FG = "#ffffff"           # Texte d'édition blanc
    EDIT_BG_FOCUS = "#505050"     # Fond d'édition avec focus
    GREEN = "#4caf50"             # Vert pour les éléments extensibles
    RED = "#f44336"               # Rouge pour les alertes
    AMBER = "#ffc107"             # Ambre pour les avertissements
    HIGHLIGHT = "#505050"         # Contour de survol plus visible
    SEARCH_HIGHLIGHT = "#ffab00"  # Couleur de surbrillance pour la recherche
    SEARCH_BG = "#3a3a3a"         # Fond pour la barre de recherche

# Polices
class Fonts:
    """Constantes de polices pour l'interface utilisateur"""
    DEFAULT = ("Segoe UI", 11)
    TOPBAR = ("Segoe UI", 12, "bold")
    TITLE = ("Segoe UI", 14, "bold")

# Dimensions
class Dimensions:
    """Constantes de dimensions pour l'interface utilisateur"""
    MIN_COL_WIDTH = 400
    MAIN_WINDOW_SIZE = "1400x800"
    TOOLBAR_HEIGHT = 50
    TOPBAR_HEIGHT = 60

# Messages et textes
class Messages:
    """Messages et textes utilisés dans l'application"""
    APP_TITLE = "Fault Editor - Auto Reload"
    READY = "Prêt"
    LOADING = "Chargement en cours..."
    ERROR_FATAL = "❌ Erreur fatale au démarrage"
    SUCCESS_LOAD = "✅ Interface utilisateur initialisée"
    FILE_NOT_FOUND = "❌ Introuvable"
    ERROR_READING = "❌ Erreur lecture"
    SUCCESS_SAVED = "✅ Fichiers sauvegardés"

# Configuration de logging
class LogConfig:
    """Configuration du système de logging"""
    LOG_DIR = "logs"
    LOG_FILE = "app_debug.log"
    LOG_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
