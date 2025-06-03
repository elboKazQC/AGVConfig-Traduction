#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Synchronise en lot tous les fichiers JSON français d'un répertoire avec leurs
équivalents anglais et espagnols.

Usage
-----
```
python sync_all.py [chemin_du_repertoire] [--force-retranslate]
```

- *chemin_du_repertoire* : Répertoire racine contenant les fichiers JSON
  (par défaut ``../JSON``).
- ``--force-retranslate`` : Force la retraduction même si une traduction est
  déjà présente.
"""

import os
import sys
import json
import argparse
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
    """Point d'entrée principal du script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_dir = os.path.join(script_dir, '..', 'JSON')

    parser = argparse.ArgumentParser(
        description='Synchronise tous les fichiers JSON d\'un répertoire',
        epilog='Exemple: python sync_all.py ./JSON --force-retranslate'
    )
    parser.add_argument(
        'directory', nargs='?', default=default_dir,
        help='Répertoire contenant les fichiers JSON (par défaut ../JSON)'
    )
    parser.add_argument(
        '--force', '--force-retranslate', dest='force', action='store_true',
        help='Force la retraduction même si une traduction existe'
    )

    args = parser.parse_args()
    base_dir = args.directory

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

    if args.force:
        print("⚡ Mode retraduction forcée activé")

    # Synchroniser chaque fichier
    for i, french_file in enumerate(french_files, 1):
        print(f"\n🔄 [{i}/{len(french_files)}] Traitement de {os.path.basename(french_file)}")

        try:
            if sync_file(french_file, force_retranslate=args.force):
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
