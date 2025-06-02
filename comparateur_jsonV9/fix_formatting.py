#!/usr/bin/env python3
"""Script pour corriger les problèmes de formatage dans app.py"""

import re

def fix_formatting(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Patterns de corrections pour les lignes collées
    patterns = [
        # Corriger les lignes avec pack() suivi directement d'autre code
        (r'\.pack\([^)]*\)(\s*)(tk\.)', r'.pack(\1)\n        \3'),
        (r'\.pack\([^)]*\)(\s*)(ttk\.)', r'.pack(\1)\n        \3'),
        (r'\.pack\([^)]*\)(\s*)(btn_)', r'.pack(\1)\n        \3'),
        (r'\.pack\([^)]*\)(\s*)(self\.)', r'.pack(\1)\n        \3'),

        # Corriger les return suivis directement d'autre code
        (r'return(\s+)([a-zA-Z#])', r'return\n        \2'),

        # Corriger les except collés
        (r'# type: ignore(\s*)(except)', r'# type: ignore\n            \2'),

        # Corriger les fonctions définitions collées
        (r'\)(\s*)(def )', r')\n\n    \3'),

        # Corriger les try/except collés
        (r'ignore(\s*)(except)', r'ignore\n            \2'),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    # Corrections spécifiques pour les variables
    content = re.sub(r'= tk\.StringVar\([^)]*\)(\s*)(tk\.)', r'= tk.StringVar(\1)\n        \3', content)
    content = re.sub(r'= tk\.StringVar\([^)]*\)(\s*)(ttk\.)', r'= tk.StringVar(\1)\n        \3', content)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

    print("Formatage corrigé!")

if __name__ == "__main__":
    fix_formatting("app.py")
