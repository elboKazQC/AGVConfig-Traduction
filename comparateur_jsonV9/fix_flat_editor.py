#!/usr/bin/env python3
"""
Script to fix indentation, color constants, and formatting in the flat_editor.py file.
"""

import os
import re

def fix_flat_editor(file_path):
    """Fix indentation and formatting issues in flat_editor.py."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Fix the indentation of the setup_flat_editor_toolbar method
        pattern = r'translate_btn\.place\(relx=0\.38, rely=0\.2, width=20, height=20\)\s+def setup_flat_editor_toolbar'
        replacement = r'translate_btn.place(relx=0.38, rely=0.2, width=20, height=20)\n\n    def setup_flat_editor_toolbar'
        content = re.sub(pattern, replacement, content)

        # Fix missing newline before search_btn
        pattern = r'save_btn\.pack\(side="left", padx=15, pady=5\)\n\n        # Search button\s+search_btn'
        replacement = r'save_btn.pack(side="left", padx=15, pady=5)\n\n        # Search button\n        search_btn'
        content = re.sub(pattern, replacement, content)

        # Write fixed content back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Fixed indentation and formatting in {file_path}")
        return True

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function."""
    flat_editor = r"c:\Users\vcasaubon.NOOVELIA\OneDrive - Noovelia\Documents\GitHub\AGVConfig-Traduction\comparateur_jsonV9\ui\flat_editor.py"

    if os.path.exists(flat_editor):
        fix_flat_editor(flat_editor)
    else:
        print(f"File not found: {flat_editor}")

if __name__ == "__main__":
    main()
