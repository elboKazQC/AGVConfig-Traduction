#!/usr/bin/env python3
"""
Script to fix color constant references in Python files.
"""

import os
import re

def fix_color_constants(file_path):
    """Fix color constant references in a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
          # Replace color constants
        replacements = {
            'COL_BG_TOPBAR': 'Colors.BG_TOPBAR',
            'COL_BG_SECONDARY': 'Colors.BG_COLUMN',
            'COL_BG_MAIN': 'Colors.BG_MAIN',
            'COL_BG_ROW': 'Colors.BG_ROW',
            'COL_BG_ROW_ALT': 'Colors.BG_ROW_ALT',
            'COL_BG_BUTTON': 'Colors.BG_COLUMN',
            'COL_EDIT_BG': 'Colors.EDIT_BG',
            'COL_EDIT_FG': 'Colors.EDIT_FG',
            'COL_FG_TEXT': 'Colors.FG_TEXT',
            'COL_AMBER': 'Colors.AMBER',
            'COL_GREEN': 'Colors.GREEN',
            'COL_RED': 'Colors.RED',
            'COL_SEARCH_HIGHLIGHT': 'Colors.SEARCH_HIGHLIGHT',
            'FONT_DEFAULT': 'Fonts.DEFAULT',
            'FONT_BOLD': 'Fonts.TITLE'
        }

        for old, new in replacements.items():
            content = content.replace(old, new)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed color constants in {file_path}")
            return True
        else:
            print(f"No changes needed in {file_path}")
            return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function."""
    # Fix main_controller.py
    main_controller = r"c:\Users\vcasaubon.NOOVELIA\OneDrive - Noovelia\Documents\GitHub\AGVConfig-Traduction\comparateur_jsonV9\main_controller.py"
    flat_editor = r"c:\Users\vcasaubon.NOOVELIA\OneDrive - Noovelia\Documents\GitHub\AGVConfig-Traduction\comparateur_jsonV9\ui\flat_editor.py"

    files_to_fix = [main_controller, flat_editor]

    for file_path in files_to_fix:
        if os.path.exists(file_path):
            fix_color_constants(file_path)
        else:
            print(f"File not found: {file_path}")

if __name__ == "__main__":
    main()
