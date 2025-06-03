#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour corriger les fichiers JSON qui ont un champ Language redondant à la fin.
"""

import os
import json
import sys

def fix_file(filepath):
    """Corrige un fichier JSON en supprimant le champ Language redondant."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = json.load(f)

        # Vérifier si le fichier a le champ Language redondant
        if 'Language' in content and 'Header' in content and 'Language' in content['Header']:
            # Supprimer le champ Language redondant
            del content['Language']

            # Sauvegarder le fichier
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
            print(f"✅ Corrigé: {filepath}")
            return True
    except Exception as e:
        print(f"❌ Erreur avec {filepath}: {e}")
        return False
    return False

def find_json_files(directory):
    """Trouve tous les fichiers JSON dans le répertoire et ses sous-répertoires."""
    json_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                json_files.append(os.path.join(root, file))
    return json_files

def main():
    """Point d'entrée principal du script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_dir = os.path.join(script_dir, '..', 'JSON')

    base_dir = sys.argv[1] if len(sys.argv) > 1 else default_dir

    if not os.path.exists(base_dir):
        print(f"❌ Répertoire JSON introuvable : {base_dir}")
        sys.exit(1)

    print(f"🔍 Recherche des fichiers JSON dans : {base_dir}")

    files = find_json_files(base_dir)
    if not files:
        print("❌ Aucun fichier JSON trouvé")
        sys.exit(1)

    print(f"📁 {len(files)} fichiers JSON trouvés")

    fixed_count = 0
    error_count = 0

    for filepath in files:
        if fix_file(filepath):
            fixed_count += 1
        else:
            error_count += 1

    print(f"\n📊 Résumé des corrections :")
    print(f"   ✅ Fichiers corrigés : {fixed_count}")
    print(f"   ❌ Erreurs : {error_count}")
    print(f"   📁 Total : {len(files)}")

if __name__ == '__main__':
    main()
