#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exceptions personnalisées pour l'application FaultEditor
"""

class FaultEditorError(Exception):
    """Exception de base pour toutes les erreurs de FaultEditor"""
    def __init__(self, message, error_code=None, details=None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message

class FileOperationError(FaultEditorError):
    """Erreurs liées aux opérations sur fichiers"""
    def __init__(self, message, filepath=None, operation=None, **kwargs):
        super().__init__(message, **kwargs)
        self.filepath = filepath
        self.operation = operation

class JSONValidationError(FaultEditorError):
    """Erreurs de validation des données JSON"""
    def __init__(self, message, field=None, expected=None, actual=None, **kwargs):
        super().__init__(message, **kwargs)
        self.field = field
        self.expected = expected
        self.actual = actual

class TranslationError(FaultEditorError):
    """Erreurs liées aux opérations de traduction"""
    def __init__(self, message, source_lang=None, target_lang=None, **kwargs):
        super().__init__(message, **kwargs)
        self.source_lang = source_lang
        self.target_lang = target_lang

class UIError(FaultEditorError):
    """Erreurs liées à l'interface utilisateur"""
    def __init__(self, message, widget=None, operation=None, **kwargs):
        super().__init__(message, **kwargs)
        self.widget = widget
        self.operation = operation

class ConfigurationError(FaultEditorError):
    """Erreurs de configuration de l'application"""
    pass

# Codes d'erreur standardisés
class ErrorCodes:
    # Erreurs de fichiers (1000-1999)
    FILE_NOT_FOUND = "E1001"
    FILE_READ_ERROR = "E1002"
    FILE_WRITE_ERROR = "E1003"
    FILE_PERMISSION_ERROR = "E1004"

    # Erreurs JSON (2000-2999)
    JSON_PARSE_ERROR = "E2001"
    JSON_VALIDATION_ERROR = "E2002"
    JSON_STRUCTURE_ERROR = "E2003"

    # Erreurs de traduction (3000-3999)
    TRANSLATION_SERVICE_ERROR = "E3001"
    LANGUAGE_NOT_SUPPORTED = "E3002"
    TRANSLATION_TIMEOUT = "E3003"

    # Erreurs UI (4000-4999)
    WIDGET_CREATION_ERROR = "E4001"
    UI_UPDATE_ERROR = "E4002"
    EVENT_HANDLER_ERROR = "E4003"

    # Erreurs de configuration (5000-5999)
    CONFIG_LOAD_ERROR = "E5001"
    CONFIG_SAVE_ERROR = "E5002"
    INVALID_CONFIG_VALUE = "E5003"
