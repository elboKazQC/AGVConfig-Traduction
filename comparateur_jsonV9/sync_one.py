#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour synchroniser un fichier JSON avec ses équivalents dans d'autres langues.
Utilise l'API OpenAI pour traduire les textes.
Version améliorée avec détection de langue et traduction forcée.
"""

import os
import sys
import json
import argparse
import re
from datetime import datetime
from translate import traduire

# Support pour la détection de langue (optionnel)
try:
    from langdetect import detect
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    print("⚠️ langdetect non disponible. Installez avec: pip install langdetect")

# Support des couleurs pour une meilleure lisibilité
def supporte_couleur():
    return os.name != 'nt' or 'WT_SESSION' in os.environ or 'TERM' in os.environ

if supporte_couleur():
    ROUGE = "\033[91m"
    VERT = "\033[92m"
    JAUNE = "\033[93m"
    BLEU = "\033[94m"
    RESET = "\033[0m"
else:
    ROUGE = VERT = JAUNE = BLEU = RESET = ""

def log_changement(langue, index, ancien, nouveau, fichier):
    """Enregistre les changements dans un fichier de log."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(script_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    chemin_log = os.path.join(logs_dir, "log.txt")
    with open(chemin_log, "a", encoding="utf-8") as log:
        log.write(f"[{datetime.now().isoformat(sep=' ', timespec='seconds')}] {fichier} - {langue.upper()}[index {index}]\n")
        log.write(f"  Ancien : {ancien}\n")
        log.write(f"  Nouveau : {nouveau}\n\n")

def est_code_technique(texte):
    """Détermine si un texte est un code technique qui ne doit pas être traduit."""
    if not texte or not isinstance(texte, str):
        return False

    texte = texte.strip()

    # Codes numériques purs
    if texte.isdigit():
        return True

    # Codes techniques courts (lettres majuscules, chiffres, symboles limités)
    if re.match(r"^[A-Z0-9 .:_/-]{1,10}$", texte):
        return True

    return False

def detecter_langue(texte):
    """Détecte la langue d'un texte (si langdetect est disponible)."""
    if not LANGDETECT_AVAILABLE or not texte or len(texte.strip()) < 3:
        return None

    try:
        return detect(texte)
    except Exception:
        return None

def sync_file(source_file_path, force_retranslate=False):    """
    Synchronise un fichier JSON source avec ses équivalents dans d'autres langues.

    Args:
        source_file_path (str): Chemin vers le fichier JSON source
        force_retranslate (bool): Force la retraduction même si une traduction existe
    """
    print(f"🔄 Synchronisation de {source_file_path}")

    if force_retranslate:
        print(f"{JAUNE}⚡ Mode retraduction forcée activé{RESET}")

    if not os.path.exists(source_file_path):
        print(f"{ROUGE}❌ Fichier source introuvable : {source_file_path}{RESET}")
        return False

    # Déterminer la langue source à partir du nom de fichier
    basename = os.path.basename(source_file_path)
    if basename.endswith('_fr.json'):
        source_lang = 'fr'
        target_langs = ['en', 'es']
    elif basename.endswith('_en.json'):
        source_lang = 'en'
        target_langs = ['fr', 'es']
    elif basename.endswith('_es.json'):
        source_lang = 'es'
        target_langs = ['fr', 'en']
    else:
        print(f"❌ Impossible de déterminer la langue du fichier : {basename}")
        return False

    print(f"📝 Langue source détectée : {source_lang}")
    print(f"🎯 Langues cibles : {', '.join(target_langs)}")

    try:
        # Charger le fichier source
        with open(source_file_path, 'r', encoding='utf-8') as f:
            source_data = json.load(f)

        # Pour chaque langue cible
        for target_lang in target_langs:
            target_file = source_file_path.replace(f'_{source_lang}.json', f'_{target_lang}.json')
            print(f"\n🌐 Traduction vers {target_lang} : {os.path.basename(target_file)}")

            # Charger le fichier cible s'il existe, sinon créer une structure vide
            target_data = {}
            if os.path.exists(target_file):
                try:
                    with open(target_file, 'r', encoding='utf-8') as f:
                        target_data = json.load(f)
                except:
                    print(f"⚠️ Erreur lors de la lecture de {target_file}, création d'un nouveau fichier")
                    target_data = {}

            # Synchroniser les données
            target_data = sync_data_structure(source_data, target_data, source_lang, target_lang)

            # Sauvegarder le fichier cible
            os.makedirs(os.path.dirname(target_file), exist_ok=True)
            with open(target_file, 'w', encoding='utf-8') as f:
                json.dump(target_data, f, ensure_ascii=False, indent=2)

            print(f"✅ Fichier {os.path.basename(target_file)} mis à jour")

        print(f"\n🎉 Synchronisation terminée avec succès !")
        return True

    except Exception as e:
        print(f"❌ Erreur lors de la synchronisation : {e}")
        return False

def sync_data_structure(source_data, target_data, source_lang, target_lang):
    """
    Synchronise récursivement les structures de données.
    """
    if isinstance(source_data, dict):
        if not isinstance(target_data, dict):
            target_data = {}

        for key, value in source_data.items():
            if key == "Description" and isinstance(value, str) and value.strip():
                # Traduire la description si elle n'existe pas ou est vide
                if key not in target_data or not target_data[key].strip():
                    print(f"  🔤 Traduction de '{value[:50]}...' vers {target_lang}")
                    target_data[key] = traduire(value, target_lang)
                else:
                    # Garder la traduction existante
                    target_data[key] = target_data[key]
            elif key in ["Id", "IsExpandable", "CategoryId", "SubCategoryId", "FaultId"]:
                # Copier les valeurs numériques et booléennes directement
                target_data[key] = value
            else:
                # Synchroniser récursivement
                target_data[key] = sync_data_structure(value, target_data.get(key, {}), source_lang, target_lang)

    elif isinstance(source_data, list):
        if not isinstance(target_data, list):
            target_data = []

        # S'assurer que la liste cible a la même longueur
        while len(target_data) < len(source_data):
            target_data.append({})

        # Synchroniser chaque élément
        for i, source_item in enumerate(source_data):
            if i < len(target_data):
                target_data[i] = sync_data_structure(source_item, target_data[i], source_lang, target_lang)
            else:
                target_data.append(sync_data_structure(source_item, {}, source_lang, target_lang))

    else:
        # Pour les types primitifs, copier directement
        return source_data

    return target_data

def main():
    parser = argparse.ArgumentParser(description='Synchronise un fichier JSON avec ses équivalents dans d\'autres langues')
    parser.add_argument('source_file', help='Chemin vers le fichier JSON source')

    args = parser.parse_args()

    if not args.source_file:
        print("❌ Aucun fichier source spécifié")
        sys.exit(1)

    success = sync_file(args.source_file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
