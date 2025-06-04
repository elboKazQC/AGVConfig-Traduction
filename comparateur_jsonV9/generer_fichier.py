#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour générer un fichier JSON dans une langue cible à partir d'un fichier source.
"""

import os
import sys
import json
import argparse
import traceback
import openai
from translate import traduire

def generer_fichier(base_dir, filename_pattern, source_lang, target_lang):
    """
    Génère un fichier JSON dans la langue cible à partir du fichier source.

    Args:
        base_dir (str): Répertoire de base
        filename_pattern (str): Pattern du nom de fichier (sans l'extension de langue)
        source_lang (str): Langue source (fr, en, es)
        target_lang (str): Langue cible (fr, en, es)
    """
    print(f"🔄 Génération de fichier : {filename_pattern} ({source_lang} → {target_lang})")

    # Construire les chemins des fichiers
    if filename_pattern.endswith(f'_{source_lang}.json'):
        source_file = os.path.join(base_dir, filename_pattern)
        target_file = os.path.join(base_dir, filename_pattern.replace(f'_{source_lang}.json', f'_{target_lang}.json'))
    else:
        # Si le pattern ne contient pas l'extension, l'ajouter
        source_file = os.path.join(base_dir, f"{filename_pattern}_{source_lang}.json")
        target_file = os.path.join(base_dir, f"{filename_pattern}_{target_lang}.json")

    print(f"📂 Fichier source : {source_file}")
    print(f"📂 Fichier cible  : {target_file}")

    if not os.path.exists(source_file):
        print(f"❌ Fichier source introuvable : {source_file}")
        return False

    try:
        # Charger le fichier source
        with open(source_file, 'r', encoding='utf-8') as f:
            source_data = json.load(f)

        print(f"✅ Fichier source chargé")

        # Créer les données cibles en traduisant
        target_data = translate_data_structure(source_data, source_lang, target_lang)

        # Créer le répertoire cible si nécessaire
        os.makedirs(os.path.dirname(target_file), exist_ok=True)

        # Sauvegarder le fichier cible
        with open(target_file, 'w', encoding='utf-8') as f:
            json.dump(target_data, f, ensure_ascii=False, indent=2)

        print(f"✅ Fichier généré : {target_file}")
        return True

    except (OSError, json.JSONDecodeError, openai.OpenAIError) as e:
        print(f"❌ Erreur lors de la génération : {e}")  # handled for visibility
        traceback.print_exc()
        return False

def translate_data_structure(data, source_lang, target_lang):
    """
    Traduit récursivement les structures de données.
    """
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if key == "Description" and isinstance(value, str) and value.strip():
                # Traduire la description
                print(f"  🔤 Traduction : '{value[:50]}...'")
                result[key] = traduire(value, target_lang)
            else:
                # Traiter récursivement
                result[key] = translate_data_structure(value, source_lang, target_lang)
        return result

    elif isinstance(data, list):
        return [translate_data_structure(item, source_lang, target_lang) for item in data]

    else:
        # Pour les types primitifs, retourner directement
        return data

def main():
    parser = argparse.ArgumentParser(description='Génère un fichier JSON traduit')
    parser.add_argument('base_dir', help='Répertoire de base')
    parser.add_argument('filename', help='Nom du fichier (avec ou sans extension de langue)')
    parser.add_argument('source_lang', help='Langue source (fr, en, es)')
    parser.add_argument('target_lang', help='Langue cible (fr, en, es)')

    args = parser.parse_args()

    if args.source_lang == args.target_lang:
        print("❌ La langue source et la langue cible sont identiques")
        sys.exit(1)

    success = generer_fichier(args.base_dir, args.filename, args.source_lang, args.target_lang)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
