#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour synchroniser un fichier JSON avec ses équivalents dans d'autres langues.
Version combinant les meilleures parties des deux approches :
- Détection de codes techniques de l'ancienne version
- Gestion des cas spéciaux comme balayeur/laser scanner de la nouvelle version
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
    from langdetect.lang_detect_exception import LangDetectException
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

def special_translations(text, target_lang):
    """Gère les cas spéciaux de traduction qui nécessitent des règles particulières."""

    # Liste de traductions spéciales
    translations = {
        "balayeur": {"en": "laser scanner", "es": "escáner láser"},
        "gauche": {"en": "left", "es": "izquierdo"},
        "droit": {"en": "right", "es": "derecho"},
        "avant": {"en": "front", "es": "delantero"},
        "arrière": {"en": "rear", "es": "trasero"}
    }

    text_lower = text.lower()

    # Si le texte contient "balayeur"
    if "balayeur" in text_lower:
        result = translations["balayeur"][target_lang]

        # Ajouter la position si elle est présente
        for position in ["gauche", "droit", "avant", "arrière"]:
            if position in text_lower:
                if target_lang == "en":
                    # En anglais, la position va avant "laser scanner"
                    result = f"{translations[position][target_lang]} {result}"
                else:
                    # En espagnol, la position va après "escáner láser"
                    result = f"{result} {translations[position][target_lang]}"
                break

        # Gérer la majuscule initiale si le texte source commence par une majuscule
        if text[0].isupper():
            result = result[0].upper() + result[1:]

        return result

    # Si aucun cas spécial n'est trouvé, on retourne None pour utiliser la traduction normale
    return None

def sync_file(source_file_path, force_retranslate=False):
    """
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
        print(f"{ROUGE}❌ Impossible de déterminer la langue du fichier : {basename}{RESET}")
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
                except (json.JSONDecodeError, OSError) as e:
                    print(f"⚠️ Erreur lors de la lecture de {target_file}, création d'un nouveau fichier: {e}")
                    target_data = {}

            # Synchroniser les données
            modifications = 0
            for i, source_item in enumerate(source_data.get("FaultDetailList", [])):
                if i >= len(target_data.get("FaultDetailList", [])):
                    # Étendre la liste cible si nécessaire
                    if "FaultDetailList" not in target_data:
                        target_data["FaultDetailList"] = []
                    target_data["FaultDetailList"].append({})

                source_desc = source_item.get("Description", "").strip()
                target_desc = target_data["FaultDetailList"][i].get("Description", "").strip()

                # Copier les champs non textuels
                for key in ["Id", "IsExpandable", "CategoryId", "SubCategoryId", "FaultId"]:
                    if key in source_item:
                        target_data["FaultDetailList"][i][key] = source_item[key]

                # Si pas de description source, passer
                if not source_desc:
                    continue

                # 1. Vérifier si c'est un code technique
                if source_desc.isdigit():
                    if target_desc != source_desc:
                        print(f"{JAUNE}🔢 Correction nombre [{target_lang.upper()}][index {i}] : {target_desc} → {source_desc}{RESET}")
                        log_changement(target_lang, i, target_desc, source_desc, basename)
                        target_data["FaultDetailList"][i]["Description"] = source_desc
                        modifications += 1
                    continue

                if re.match(r"^[A-Z0-9 .:_/-]{1,10}$", source_desc):
                    if target_desc != source_desc:
                        print(f"{JAUNE}🔡 Correction code technique [{target_lang.upper()}][index {i}] : {target_desc} → {source_desc}{RESET}")
                        log_changement(target_lang, i, target_desc, source_desc, basename)
                        target_data["FaultDetailList"][i]["Description"] = source_desc
                        modifications += 1
                    continue

                # 2. Vérifier si c'est une traduction spéciale (comme "balayeur")
                special_translation = special_translations(source_desc, target_lang)
                if special_translation:
                    if target_desc != special_translation:
                        print(f"{BLEU}🔧 Correction spéciale [{target_lang.upper()}][index {i}]{RESET}")
                        print(f"    Source ({source_lang}) : {source_desc}")
                        print(f"    Ancien : {target_desc}")
                        print(f"    Nouveau : {special_translation}")
                        log_changement(target_lang, i, target_desc, special_translation, basename)
                        target_data["FaultDetailList"][i]["Description"] = special_translation
                        modifications += 1
                    continue

                # 3. Traduction normale si nécessaire
                should_translate = force_retranslate or not target_desc

                if not should_translate and LANGDETECT_AVAILABLE:
                    try:
                        detected_lang = detect(target_desc)
                        if detected_lang != target_lang:
                            should_translate = True
                    except LangDetectException:
                        pass

                if should_translate:
                    new_translation = traduire(source_desc, target_lang).strip()
                    if new_translation != target_desc:
                        print(f"{BLEU}🔄 [{target_lang.upper()}][index {i}]{RESET}")
                        print(f"    Source ({source_lang}) : {source_desc}")
                        print(f"    Ancien : {target_desc}")
                        print(f"    Nouveau : {new_translation}")
                        log_changement(target_lang, i, target_desc, new_translation, basename)
                        target_data["FaultDetailList"][i]["Description"] = new_translation
                        modifications += 1

            # Mettre à jour l'en-tête de langue
            if target_data.get("Language") != target_lang:
                print(f"{JAUNE}🔧 Correction en-tête langue : {target_data.get('Language')} → {target_lang}{RESET}")
                target_data["Language"] = target_lang
                modifications += 1

            # Sauvegarder le fichier cible
            os.makedirs(os.path.dirname(target_file), exist_ok=True)
            with open(target_file, 'w', encoding='utf-8') as f:
                json.dump(target_data, f, ensure_ascii=False, indent=2)

            if modifications > 0:
                print(f"{VERT}✅ Fichier {os.path.basename(target_file)} mis à jour ({modifications} modifications){RESET}")
            else:
                print(f"✅ Fichier {os.path.basename(target_file)} déjà à jour")

        print(f"\n🎉 Synchronisation terminée avec succès !")
        return True

    except Exception as e:
        print(f"{ROUGE}❌ Erreur lors de la synchronisation : {e}{RESET}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Synchronise un fichier JSON avec ses équivalents dans d\'autres langues')
    parser.add_argument('source_file', help='Chemin vers le fichier JSON source')
    parser.add_argument('--force', '-f', action='store_true',
                       help='Force la retraduction même si une traduction existe')

    args = parser.parse_args()

    if not args.source_file:
        print(f"{ROUGE}❌ Aucun fichier source spécifié{RESET}")
        sys.exit(1)

    success = sync_file(args.source_file, force_retranslate=args.force)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
