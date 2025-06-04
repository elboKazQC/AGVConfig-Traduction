#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour générer tous les fichiers de traduction manquants dans un répertoire.
"""

import os
import sys
import json
import argparse
import traceback
from generer_fichier import generer_fichier

def find_missing_translations(base_dir):
    """
    Trouve tous les fichiers de traduction manquants.

    Returns:
        list: Liste de tuples (base_filename, existing_lang, missing_langs)
    """
    # Scanner tous les fichiers JSON
    json_files = {}

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.json'):
                # Extraire le nom de base et la langue
                if file.endswith('_fr.json'):
                    base_name = file[:-7]  # Enlever '_fr.json'
                    lang = 'fr'
                elif file.endswith('_en.json'):
                    base_name = file[:-7]  # Enlever '_en.json'
                    lang = 'en'
                elif file.endswith('_es.json'):
                    base_name = file[:-7]  # Enlever '_es.json'
                    lang = 'es'
                else:
                    continue  # Ignorer les fichiers sans suffixe de langue

                full_path = os.path.join(root, file)
                relative_dir = os.path.relpath(root, base_dir)

                key = (base_name, relative_dir)
                if key not in json_files:
                    json_files[key] = {}

                json_files[key][lang] = full_path

    # Identifier les traductions manquantes
    missing_translations = []
    all_langs = {'fr', 'en', 'es'}

    for (base_name, rel_dir), lang_files in json_files.items():
        existing_langs = set(lang_files.keys())
        missing_langs = all_langs - existing_langs

        if missing_langs:
            # Prendre le premier fichier existant comme source
            source_lang = list(existing_langs)[0]
            source_file = lang_files[source_lang]

            for missing_lang in missing_langs:
                target_file = source_file.replace(f'_{source_lang}.json', f'_{missing_lang}.json')
                missing_translations.append({
                    'source_file': source_file,
                    'target_file': target_file,
                    'source_lang': source_lang,
                    'target_lang': missing_lang,
                    'base_name': base_name
                })

    return missing_translations

def main():
    parser = argparse.ArgumentParser(description='Génère tous les fichiers de traduction manquants')
    parser.add_argument('base_dir', help='Répertoire de base à scanner')

    args = parser.parse_args()

    if not os.path.exists(args.base_dir):
        print(f"❌ Répertoire introuvable : {args.base_dir}")
        sys.exit(1)

    print(f"🔍 Recherche des traductions manquantes dans : {args.base_dir}")

    # Trouver les traductions manquantes
    missing_translations = find_missing_translations(args.base_dir)

    if not missing_translations:
        print("✅ Aucune traduction manquante trouvée !")
        sys.exit(0)

    print(f"📋 {len(missing_translations)} traductions manquantes trouvées :")

    for translation in missing_translations:
        print(f"  • {translation['base_name']} ({translation['source_lang']} → {translation['target_lang']})")

    # Demander confirmation
    response = input(f"\n🤔 Voulez-vous générer ces {len(missing_translations)} traductions ? (o/N) : ")
    if response.lower() not in ['o', 'oui', 'y', 'yes']:
        print("❌ Opération annulée")
        sys.exit(0)

    # Générer les traductions
    success_count = 0
    error_count = 0

    for i, translation in enumerate(missing_translations, 1):
        print(f"\n🔄 [{i}/{len(missing_translations)}] {translation['base_name']} ({translation['source_lang']} → {translation['target_lang']})")

        try:
            # Extraire le répertoire et le nom de fichier
            source_dir = os.path.dirname(translation['source_file'])
            filename_pattern = f"{translation['base_name']}_{translation['source_lang']}.json"

            if generer_fichier(source_dir, filename_pattern, translation['source_lang'], translation['target_lang']):
                success_count += 1
            else:
                error_count += 1
        except Exception as e:
            print(f"❌ Erreur : {e}")  # handled for visibility
            traceback.print_exc()
            error_count += 1

    print(f"\n📊 Résumé :")
    print(f"   ✅ Réussies : {success_count}")
    print(f"   ❌ Erreurs  : {error_count}")
    print(f"   📁 Total    : {len(missing_translations)}")

    if error_count == 0:
        print("🎉 Génération des traductions manquantes terminée avec succès !")
    else:
        print("⚠️ Génération terminée avec des erreurs")

    sys.exit(0 if error_count == 0 else 1)

if __name__ == "__main__":
    main()
