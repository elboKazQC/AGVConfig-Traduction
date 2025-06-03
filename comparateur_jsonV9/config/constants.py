# Configuration et constantes pour l'application Fault Editor
"""
Ce module contient toutes les constantes de configuration de l'application.
Modifiez ces valeurs pour personnaliser l'apparence et le comportement.
"""

# Couleurs de l'interface
class Colors:
    """Constantes de couleurs pour l'interface utilisateur"""
    # Couleurs de fond
    BG_MAIN = "#2b2b2b"           # Fond principal
    BG_TOPBAR = "#1e1e1e"         # Barre supérieure
    BG_COLUMN = "#3c3c3c"         # Colonnes
    BG_ROW = "#4a4a4a"            # Lignes
    BG_ROW_ALT = "#555555"        # Lignes alternées
    BG_STATUSBAR = "#1e1e1e"      # Fond de la barre d'état

    # Couleurs du texte
    FG_TEXT = "#ffffff"           # Texte blanc

    # Couleurs d'édition
    EDIT_BG = "#ffffff"           # Fond d'édition
    EDIT_BG_FOCUS = "#ffffcc"     # Fond d'édition avec focus
    EDIT_FG = "#000000"           # Texte d'édition noir

    # Couleurs des boutons
    GREEN = "#4caf50"             # Vert pour les éléments extensibles
    RED = "#f44336"               # Rouge pour les alertes
    YELLOW = "#ffc107"             # Ambre pour les avertissements
    HIGHLIGHT = "#505050"         # Contour de survol plus visible
    SEARCH_HIGHLIGHT = "#ffab00"  # Couleur de surbrillance pour la recherche    SEARCH_BG = "#3a3a3a"         # Fond pour la barre de recherche
    BG_ROW_HOVER = "#606060"       # Couleur de survol des lignes

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
