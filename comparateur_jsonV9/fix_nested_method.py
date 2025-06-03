#!/usr/bin/env python3
"""
Script to fix the setup_flat_editor_toolbar method indentation in flat_editor.py
"""

import re
import sys

def fix_nested_method(file_path):
    """Fix nested method indentation in a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find the nested method and extract it
        setup_toolbar_pattern = r'(\s+)def translate_row\(self.*?_reset_row_color\(row_idx\)\)\n(\s+)def setup_flat_editor_toolbar\(self, editor_window, toolbar\):(.*?)((?:\n\s+)def \w+)'
        match = re.search(setup_toolbar_pattern, content, re.DOTALL)

        if not match:
            print("Could not find nested method pattern. Looking for simpler pattern...")
            # Try a simpler pattern
            setup_toolbar_pattern = r'(\s+)translate_btn.place.*?\n(\s+)def setup_flat_editor_toolbar\(self, editor_window, toolbar\):(.*?)((?:\n\s+)def show_flat_search)'
            match = re.search(setup_toolbar_pattern, content, re.DOTALL)

        if match:
            # Extract the nested method
            leading_whitespace = match.group(1)
            nested_method = f"{leading_whitespace}def setup_flat_editor_toolbar(self, editor_window, toolbar):{match.group(3)}"

            # Remove the nested method from its current position
            content = content.replace(f"{leading_whitespace}def setup_flat_editor_toolbar(self, editor_window, toolbar):{match.group(3)}", "")

            # Add a blank line before the next method if needed
            next_method_start = match.group(4)
            if not content.endswith('\n\n'):
                content = content.replace(next_method_start, f"\n{next_method_start}")

            # Insert the method at the proper position
            # Look for the _create_data_grid method
            end_of_create_data_grid = re.search(r'def _create_data_grid.*?translate_btn.place.*?relx=0.38, rely=0.2, width=20, height=20\)', content, re.DOTALL)

            if end_of_create_data_grid:
                end_pos = end_of_create_data_grid.end()
                content = f"{content[:end_pos]}\n{nested_method}\n{content[end_pos:]}"

                # Write the fixed content back to the file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                print(f"Successfully fixed nested method in {file_path}")
                return True
            else:
                print("Could not find insertion point. Manual fix required.")
                return False
        else:
            print("Could not find nested method. Manual fix required.")
            return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

if __name__ == "__main__":
    file_path = r"c:\Users\vcasaubon.NOOVELIA\OneDrive - Noovelia\Documents\GitHub\AGVConfig-Traduction\comparateur_jsonV9\ui\flat_editor.py"
    fix_nested_method(file_path)
