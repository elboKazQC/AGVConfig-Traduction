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

            # Synchroniser les données avec la logique améliorée
            modifications = sync_data_structure_improved(
                source_data, target_data, source_lang, target_lang,
                force_retranslate, basename
            )

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

def sync_data_structure_improved(source_data, target_data, source_lang, target_lang, force_retranslate=False, filename=""):
    """
    Synchronise récursivement les structures de données avec logique améliorée.
    Retourne le nombre de modifications effectuées.
    """
    modifications = 0

    if isinstance(source_data, dict):
        if not isinstance(target_data, dict):
            target_data.clear()
            target_data.update({})

        for key, value in source_data.items():
            if key == "Description" and isinstance(value, str) and value.strip():
                source_desc = value.strip()
                current_desc = target_data.get(key, "").strip()

                # Si c'est un code technique, copier directement
                if est_code_technique(source_desc):
                    if current_desc != source_desc:
                        print(f"{JAUNE}🔁 Correction code technique [{target_lang.upper()}] : {current_desc} → {source_desc}{RESET}")
                        log_changement(target_lang, "N/A", current_desc, source_desc, filename)
                        target_data[key] = source_desc
                        modifications += 1
                    continue

                # Décider si on doit traduire
                should_translate = False
                reason = ""

                if not current_desc:
                    should_translate = True
                    reason = "description vide"
                elif force_retranslate:
                    should_translate = True
                    reason = "retraduction forcée"
                else:
                    # Vérifier la langue de la description existante
                    detected_lang = detecter_langue(current_desc)
                    if detected_lang and detected_lang != target_lang:
                        should_translate = True
                        reason = f"langue détectée: {detected_lang} ≠ {target_lang}"
                    else:
                        # Comparer avec une nouvelle traduction pour voir si elle a changé
                        new_translation = traduire(source_desc, target_lang).strip()
                        if current_desc.lower() != new_translation.lower():
                            should_translate = True
                            reason = "traduction mise à jour"

                if should_translate:
                    # Vérifier d'abord s'il y a une traduction spéciale
                    special_translation = special_translations(source_desc, target_lang)
                    if special_translation:
                        new_translation = special_translation
                    else:
                        new_translation = traduire(source_desc, target_lang).strip()

                    print(f"{BLEU}🔄 [{target_lang.upper()}] {reason}{RESET}")
                    print(f"    Source ({source_lang}) : {source_desc}")
                    print(f"    Ancien : {current_desc}")
                    print(f"    Nouveau : {new_translation}")
                    log_changement(target_lang, "N/A", current_desc, new_translation, filename)
                    target_data[key] = new_translation
                    modifications += 1
                else:
                    # Garder la traduction existante
                    target_data[key] = current_desc

            elif key == "Language":
                # Corriger l'en-tête de langue
                correct_lang = target_lang
                if target_data.get(key) != correct_lang:
                    print(f"{JAUNE}🔧 Correction en-tête langue : {target_data.get(key)} → {correct_lang}{RESET}")
                    target_data[key] = correct_lang
                    modifications += 1
            elif key in ["Id", "IsExpandable", "CategoryId", "SubCategoryId", "FaultId"]:
                # Copier les valeurs numériques et booléennes directement
                target_data[key] = value
            else:
                # Synchroniser récursivement
                if isinstance(value, (dict, list)):
                    if key not in target_data:
                        target_data[key] = {} if isinstance(value, dict) else []
                    sub_modifications = sync_data_structure_improved(
                        value, target_data[key], source_lang, target_lang,
                        force_retranslate, filename
                    )
                    modifications += sub_modifications
                else:
                    # Pour les valeurs primitives, copier directement
                    target_data[key] = value

    elif isinstance(source_data, list):
        if not isinstance(target_data, list):
            target_data.clear()
            target_data.extend([])

        # S'assurer que la liste cible a la même longueur
        while len(target_data) < len(source_data):
            target_data.append({})

        # Synchroniser chaque élément
        for i, source_item in enumerate(source_data):
            if i < len(target_data):
                sub_modifications = sync_data_structure_improved(
                    source_item, target_data[i], source_lang, target_lang,
                    force_retranslate, filename
                )
                modifications += sub_modifications
            else:
                # Ajouter un nouvel élément
                new_item = {}
                sub_modifications = sync_data_structure_improved(
                    source_item, new_item, source_lang, target_lang,
                    force_retranslate, filename
                )
                modifications += sub_modifications
                target_data.append(new_item)

    return modifications

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
