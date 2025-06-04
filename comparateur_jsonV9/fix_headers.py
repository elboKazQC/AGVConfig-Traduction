#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour corriger automatiquement les erreurs de header détectées par check_coherence.py
"""

import os
import sys
import json
import argparse
import traceback
from pathlib import Path

def fix_header_metadata(file_path):
    """Corrige les métadonnées du header d'un fichier JSON."""
    try:
        # Charger le fichier
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if 'Header' not in data:
            print(f"⚠️ Pas de Header dans {file_path}")
            return False

        filename = os.path.basename(file_path)

        # Extraire la langue du nom de fichier
        if filename.endswith('_fr.json'):
            language = 'fr'
        elif filename.endswith('_en.json'):
            language = 'en'
        elif filename.endswith('_es.json'):
            language = 'es'
        else:
            print(f"⚠️ Impossible d'extraire la langue de {filename}")
            return False

        # Vérifier si des corrections sont nécessaires
        header = data['Header']
        corrections_needed = False

        # Corriger la langue
        if header.get('Language') != language:
            print(f"  🔧 Correction Language: {header.get('Language')} → {language}")
            header['Language'] = language
            corrections_needed = True

        # Corriger le nom de fichier
        if header.get('Filename') != filename:
            print(f"  🔧 Correction Filename: {header.get('Filename')} → {filename}")
            header['Filename'] = filename
            corrections_needed = True

        # Sauvegarder si des corrections ont été faites
        if corrections_needed:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True

        return False

    except (OSError, json.JSONDecodeError) as e:
        print(f"❌ Erreur lors de la correction de {file_path}: {e}")  # handled for visibility
        traceback.print_exc()
        return False

def find_all_json_files(base_dir):
    """Trouve tous les fichiers JSON de traduction."""
    json_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(('_fr.json', '_en.json', '_es.json')):
                json_files.append(os.path.join(root, file))
    return json_files

def main():
    parser = argparse.ArgumentParser(description='Corrige automatiquement les erreurs de header')
    parser.add_argument('base_dir', help='Répertoire de base à corriger')
    parser.add_argument('--dry-run', action='store_true', help='Mode simulation (pas de modifications)')

    args = parser.parse_args()

    if not os.path.exists(args.base_dir):
        print(f"❌ Répertoire introuvable : {args.base_dir}")
        sys.exit(1)

    print(f"🔧 Correction des headers dans : {args.base_dir}")
    if args.dry_run:
        print("📋 Mode simulation activé - aucune modification ne sera effectuée")

    # Trouver tous les fichiers JSON
    json_files = find_all_json_files(args.base_dir)

    if not json_files:
        print("❌ Aucun fichier JSON de traduction trouvé")
        sys.exit(1)

    print(f"📁 {len(json_files)} fichiers trouvés")

    corrected_count = 0
    error_count = 0

    # Corriger chaque fichier
    for file_path in json_files:
        print(f"\n🔍 Vérification : {os.path.relpath(file_path, args.base_dir)}")

        if args.dry_run:
            # En mode simulation, on simule juste la vérification
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                filename = os.path.basename(file_path)
                language = 'fr' if filename.endswith('_fr.json') else 'en' if filename.endswith('_en.json') else 'es'

                header = data.get('Header', {})
                if header.get('Language') != language or header.get('Filename') != filename:
                    print(f"  ⚠️ Corrections nécessaires détectées")
                    corrected_count += 1
                else:
                    print(f"  ✅ Header correct")

            except (OSError, json.JSONDecodeError) as e:
                print(f"  ❌ Erreur : {e}")  # handled for visibility
                traceback.print_exc()
                error_count += 1
        else:
            # Mode correction réelle
            if fix_header_metadata(file_path):
                corrected_count += 1
                print(f"  ✅ Corrigé avec succès")
            else:
                print(f"  ℹ️ Aucune correction nécessaire")

    print(f"\n📊 Résumé :")
    print(f"   📁 Fichiers traités     : {len(json_files)}")
    print(f"   🔧 Fichiers corrigés    : {corrected_count}")
    print(f"   ❌ Erreurs rencontrées  : {error_count}")

    if args.dry_run and corrected_count > 0:
        print(f"\n💡 Relancez sans --dry-run pour effectuer les corrections")

if __name__ == "__main__":
    main()
