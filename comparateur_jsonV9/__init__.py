"""
AGVConfig-Traduction Package

A comprehensive tool for translating and managing AGV configuration fault codes.
Provides GUI and command-line utilities for multi-language JSON file management.

Main modules:
- app: GUI application for interactive fault code management
- translate: OpenAI-powered translation module
- sync_one: Single file synchronization utilities
- sync_all: Batch synchronization utilities
- generer_manquant: Missing file generation utilities
- check_coherence: File coherence validation utilities

Author: Noovelia
License: MIT
"""

__version__ = "1.3.0"
__author__ = "Noovelia"
__license__ = "MIT"

# Main imports for package-level access
import logging
import traceback

logger = logging.getLogger(__name__)

try:
    from .translate import traduire, OPENAI_API_KEY
except ImportError as e:
    logger.warning(f"Impossible d'importer translate: {e}")
    traceback.print_exc()

# Supported languages
SUPPORTED_LANGUAGES = ['fr', 'en', 'es']

# Default file naming patterns
DEFAULT_FILE_PATTERN = r'faults_\d{3}_\d{3}_\d{3}_\d{3}_(fr|en|es)\.json'
