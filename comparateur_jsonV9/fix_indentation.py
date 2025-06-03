#!/usr/bin/env python3
"""
Script to fix indentation issues in the flat_editor.py file.
"""

import os
import re

def fix_indentation(file_path):
    """Fix indentation in a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Detect setup_flat_editor_toolbar method that's improperly indented
        in_method = False
        proper_indentation = False
        fixed_lines = []
        buffer = []

        for line in lines:
            # Check for the improperly indented method definition
            if '    def setup_flat_editor_toolbar(self, editor_window, toolbar):' in line:
                in_method = True
                buffer.append(line)
                continue

            # Collect the improperly indented method
            if in_method and not proper_indentation:
                # Check if we've reached the next proper method
                if re.match(r'^    def ', line):
                    # Found next method, flush buffer with proper indentation
                    for buffered_line in buffer:
                        fixed_lines.append(buffered_line)
                    buffer = []
                    in_method = False
                    fixed_lines.append(line)
                    continue

                # Still in improperly indented method, add to buffer
                buffer.append(line)
                continue

            fixed_lines.append(line)

        # If buffer still has content, append it
        for line in buffer:
            fixed_lines.append(line)

        # Write fixed content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)

        print(f"Fixed indentation in {file_path}")
        return True

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function."""
    flat_editor = r"c:\Users\vcasaubon.NOOVELIA\OneDrive - Noovelia\Documents\GitHub\AGVConfig-Traduction\comparateur_jsonV9\ui\flat_editor.py"

    if os.path.exists(flat_editor):
        fix_indentation(flat_editor)
    else:
        print(f"File not found: {flat_editor}")

if __name__ == "__main__":
    main()
