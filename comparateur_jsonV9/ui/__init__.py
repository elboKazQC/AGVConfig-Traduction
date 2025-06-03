# UI components package for Fault Editor
from .components import (
    StyledFrame,
    StyledButton,
    StyledLabel,
    ProgressDialog,
    LanguageSelector,
    FileInfoBar,
    ToolbarBuilder,
    ResultsDialog,
    ConfirmationDialog
)
# Avoid importing heavy modules at package import time
try:
    from .hierarchical_editor import HierarchicalEditor
except Exception:  # pragma: no cover - may fail in minimal environments
    HierarchicalEditor = None

try:
    from .flat_editor import FlatEditor
except Exception:  # pragma: no cover
    FlatEditor = None

__all__ = [
    'StyledFrame',
    'StyledButton',
    'StyledLabel',
    'ProgressDialog',
    'LanguageSelector',
    'FileInfoBar',
    'ToolbarBuilder',
    'ResultsDialog',
    'ConfirmationDialog',
    'HierarchicalEditor',
    'FlatEditor'
]
