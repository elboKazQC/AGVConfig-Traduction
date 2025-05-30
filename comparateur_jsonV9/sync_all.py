#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour synchroniser tous les fichiers JSON français avec leurs équivalents anglais et espagnols.
"""

import os
import sys
import json
from sync_one import sync_file

def find_json_files(directory):
    """
    Trouve tous les fichiers JSON français dans le répertoire et ses sous-répertoires.
    """
    json_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('_fr.json'):
                json_files.append(os.path.join(root, file))
    return json_files

def main():
    # Répertoire de base - répertoire parent du script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(script_dir, '..', 'JSON')

    if not os.path.exists(base_dir):
        print(f"❌ Répertoire JSON introuvable : {base_dir}")
        sys.exit(1)

    print(f"🔍 Recherche des fichiers JSON dans : {base_dir}")

    # Trouver tous les fichiers JSON français
    french_files = find_json_files(base_dir)

    if not french_files:
        print("❌ Aucun fichier JSON français trouvé")
        sys.exit(1)

    print(f"📁 {len(french_files)} fichiers JSON français trouvés")

    success_count = 0
    error_count = 0

    # Synchroniser chaque fichier
    for i, french_file in enumerate(french_files, 1):
        print(f"\n🔄 [{i}/{len(french_files)}] Traitement de {os.path.basename(french_file)}")

        try:
            if sync_file(french_file):
                success_count += 1
            else:
                error_count += 1
        except Exception as e:
            print(f"❌ Erreur lors du traitement de {french_file}: {e}")
            error_count += 1

    print(f"\n📊 Résumé de la synchronisation :")
    print(f"   ✅ Réussies : {success_count}")
    print(f"   ❌ Erreurs  : {error_count}")
    print(f"   📁 Total    : {len(french_files)}")

    if error_count == 0:
        print("🎉 Synchronisation globale terminée avec succès !")
    else:
        print("⚠️ Synchronisation terminée avec des erreurs")

    sys.exit(0 if error_count == 0 else 1)

if __name__ == "__main__":
    main()
