#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour synchroniser un fichier JSON avec ses équivalents dans d'autres langues.
Utilise l'API OpenAI pour traduire les textes.
Version consolidée combinant les meilleures fonctionnalités :
- Détection de codes techniques avancée
- Gestion des cas spéciaux de traduction (balayeur → laser scanner)
- Détection de langue et traduction forcée
- Logging amélioré et gestion d'erreurs robuste
- Support complet des types hints et documentation
"""

import os
import sys
import json
import argparse
import re
import logging
import configparser
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from translate import traduire

# Support pour la détection de langue (optionnel)
try:
    from langdetect import detect
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    print("⚠️ langdetect non disponible. Installez avec: pip install langdetect")

# Configuration du logging
def setup_logging() -> logging.Logger:
    """Configure le système de logging avec rotation et niveaux multiples."""
    logger = logging.getLogger('sync_one')
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # Handler pour fichier
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logs_dir = os.path.join(script_dir, "logs")
        os.makedirs(logs_dir, exist_ok=True)

        file_handler = logging.FileHandler(
            os.path.join(logs_dir, "sync_one.log"),
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)

        # Handler pour console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)

        # Format des messages
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

logger = setup_logging()

# Support des couleurs pour une meilleure lisibilité
def supporte_couleur() -> bool:
    """Détermine si le terminal supporte les couleurs ANSI."""
    return os.name != 'nt' or 'WT_SESSION' in os.environ or 'TERM' in os.environ

if supporte_couleur():
    ROUGE = "\033[91m"
    VERT = "\033[92m"
    JAUNE = "\033[93m"
    BLEU = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
else:
    ROUGE = VERT = JAUNE = BLEU = MAGENTA = CYAN = RESET = ""

def log_changement(langue: str, index: int, ancien: str, nouveau: str, fichier: str) -> None:
    """
    Enregistre les changements dans un fichier de log avec horodatage.

    Args:
        langue: Code de langue (fr, en, es)
        index: Index de l'élément modifié
        ancien: Ancienne valeur
        nouveau: Nouvelle valeur
        fichier: Nom du fichier modifié
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(script_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    chemin_log = os.path.join(logs_dir, "changements.log")

    try:
        with open(chemin_log, "a", encoding="utf-8") as log:
            timestamp = datetime.now().isoformat(sep=' ', timespec='seconds')
            log.write(f"[{timestamp}] {fichier} - {langue.upper()}[index {index}]\n")
            log.write(f"  Ancien : {ancien}\n")
            log.write(f"  Nouveau : {nouveau}\n\n")

        logger.info(f"Changement enregistré: {fichier} - {langue}[{index}]")
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement du changement: {e}")

def est_code_technique(texte: str) -> bool:
    """
    Détermine si un texte est un code technique qui ne doit pas être traduit.

    Args:
        texte: Le texte à analyser

    Returns:
        True si le texte est considéré comme un code technique
    """
    if not texte or not isinstance(texte, str):
        return False

    texte = texte.strip()

    # Codes numériques purs
    if texte.isdigit():
        return True

    # Codes techniques courts (lettres majuscules, chiffres, symboles limités)
    if re.match(r"^[A-Z0-9 .:_/-]{1,10}$", texte):
        return True

    # Codes avec des caractères spéciaux techniques
    if re.match(r"^[A-Z0-9_.#-]+$", texte) and len(texte) <= 15:
        return True

    return False

def detecter_langue(texte: str) -> Optional[str]:
    """
    Détecte la langue d'un texte (si langdetect est disponible).

    Args:
        texte: Le texte à analyser

    Returns:
        Code de langue détecté ou None si impossible
    """
    if not LANGDETECT_AVAILABLE or not texte or len(texte.strip()) < 3:
        return None

    try:
        return detect(texte)
    except Exception as e:
        logger.debug(f"Erreur détection langue pour '{texte[:20]}...': {e}")
        return None

def validate_json_structure(data: Dict[str, Any]) -> bool:
    """
    Valide la structure JSON pour s'assurer qu'elle contient les champs attendus.

    Args:
        data: Données JSON à valider

    Returns:
        True si la structure est valide
    """
    try:
        if not isinstance(data, dict):
            return False

        # Vérifier la présence de FaultDetailList
        if "FaultDetailList" not in data:
            logger.warning("Structure JSON manque FaultDetailList")
            return False

        if not isinstance(data["FaultDetailList"], list):
            logger.warning("FaultDetailList n'est pas une liste")
            return False

        return True
    except Exception as e:
        logger.error(f"Erreur validation structure JSON: {e}")
        return False

def sync_file(source_file_path: str, force_retranslate: bool = False) -> bool:
    """
    Synchronise un fichier JSON source avec ses équivalents dans d'autres langues.

    Args:
        source_file_path: Chemin vers le fichier JSON source
        force_retranslate: Force la retraduction même si une traduction existe

    Returns:
        True si la synchronisation s'est bien passée
    """
    print(f"🔄 Synchronisation de {source_file_path}")
    logger.info(f"Début synchronisation: {source_file_path}")

    if force_retranslate:
        print(f"{JAUNE}⚡ Mode retraduction forcée activé{RESET}")
        logger.info("Mode retraduction forcée activé")

    if not os.path.exists(source_file_path):
        error_msg = f"Fichier source introuvable : {source_file_path}"
        print(f"{ROUGE}❌ {error_msg}{RESET}")
        logger.error(error_msg)
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
        error_msg = f"Impossible de déterminer la langue du fichier : {basename}"
        print(f"{ROUGE}❌ {error_msg}{RESET}")
        logger.error(error_msg)
        return False

    print(f"📝 Langue source détectée : {source_lang}")
    print(f"🎯 Langues cibles : {', '.join(target_langs)}")
    logger.info(f"Langue source: {source_lang}, cibles: {target_langs}")

    try:
        # Charger le fichier source
        with open(source_file_path, 'r', encoding='utf-8') as f:
            source_data = json.load(f)

        # Valider la structure
        if not validate_json_structure(source_data):
            error_msg = "Structure JSON source invalide"
            print(f"{ROUGE}❌ {error_msg}{RESET}")
            logger.error(error_msg)
            return False

        # Pour chaque langue cible
        for target_lang in target_langs:
            target_file = source_file_path.replace(f'_{source_lang}.json', f'_{target_lang}.json')
            print(f"\n🌐 Traitement vers {target_lang} : {os.path.basename(target_file)}")
            logger.info(f"Traitement vers {target_lang}: {target_file}")

            # Charger le fichier cible s'il existe, sinon créer une structure vide
            target_data = {}
            if os.path.exists(target_file):
                try:
                    with open(target_file, 'r', encoding='utf-8') as f:
                        target_data = json.load(f)
                except Exception as e:
                    warning_msg = f"Erreur lors de la lecture de {target_file}, création d'un nouveau fichier"
                    print(f"⚠️ {warning_msg}")
                    logger.warning(f"{warning_msg}: {e}")
                    target_data = {}

            # Synchroniser les données
            modifications = process_translations(
                source_data, target_data, source_lang, target_lang,
                basename, force_retranslate
            )            # Mettre à jour l'en-tête de langue dans le Header
            if "Header" not in target_data:
                target_data["Header"] = {}
            if target_data["Header"].get("Language") != target_lang:
                print(f"{JAUNE}🔧 Correction en-tête langue : {target_data['Header'].get('Language')} → {target_lang}{RESET}")
                logger.info(f"Correction langue header: {target_data['Header'].get('Language')} → {target_lang}")
                target_data["Header"]["Language"] = target_lang
                modifications += 1
            # Supprimer le champ Language redondant s'il existe à la racine
            if "Language" in target_data:
                del target_data["Language"]
                modifications += 1

            # Sauvegarder le fichier cible
            try:
                os.makedirs(os.path.dirname(target_file), exist_ok=True)
                with open(target_file, 'w', encoding='utf-8') as f:
                    json.dump(target_data, f, ensure_ascii=False, indent=2)

                if modifications > 0:
                    print(f"{VERT}✅ Fichier {os.path.basename(target_file)} mis à jour ({modifications} modifications){RESET}")
                    logger.info(f"Fichier mis à jour: {target_file} ({modifications} modifications)")
                else:
                    print(f"✅ Fichier {os.path.basename(target_file)} déjà à jour")
                    logger.info(f"Fichier déjà à jour: {target_file}")
            except Exception as e:
                error_msg = f"Erreur sauvegarde {target_file}: {e}"
                print(f"{ROUGE}❌ {error_msg}{RESET}")
                logger.error(error_msg)
                return False

        print(f"\n🎉 Synchronisation terminée avec succès !")
        logger.info("Synchronisation terminée avec succès")
        return True

    except Exception as e:
        error_msg = f"Erreur lors de la synchronisation : {e}"
        print(f"{ROUGE}❌ {error_msg}{RESET}")
        logger.error(error_msg)
        return False

def process_translations(
    source_data: Dict[str, Any],
    target_data: Dict[str, Any],
    source_lang: str,
    target_lang: str,
    basename: str,
    force_retranslate: bool
) -> int:
    """
    Traite les traductions pour une langue cible spécifique.

    Args:
        source_data: Données source
        target_data: Données cible
        source_lang: Langue source
        target_lang: Langue cible
        basename: Nom du fichier pour les logs
        force_retranslate: Force la retraduction

    Returns:
        Nombre de modifications effectuées
    """
    modifications = 0

    # Initialiser la structure cible si nécessaire
    if "FaultDetailList" not in target_data:
        target_data["FaultDetailList"] = []

    source_list = source_data.get("FaultDetailList", [])
    target_list = target_data["FaultDetailList"]

    # Étendre la liste cible si nécessaire
    while len(target_list) < len(source_list):
        target_list.append({})

    # Traiter chaque élément
    for i, source_item in enumerate(source_list):
        if i >= len(target_list):
            target_list.append({})

        source_desc = source_item.get("Description", "").strip()
        target_desc = target_list[i].get("Description", "").strip()

        # Copier les champs non textuels
        for key in ["Id", "IsExpandable", "CategoryId", "SubCategoryId", "FaultId"]:
            if key in source_item:
                target_list[i][key] = source_item[key]

        # Si pas de description source, passer
        if not source_desc:
            continue        # 1. Vérifier si c'est un code technique
        if est_code_technique(source_desc):
            if target_desc != source_desc:
                print(f"{JAUNE}🔧 Correction code technique [{target_lang.upper()}][index {i}] : {target_desc} → {source_desc}{RESET}")
                log_changement(target_lang, i, target_desc, source_desc, basename)
                target_list[i]["Description"] = source_desc
                modifications += 1
            continue

        # 2. Traduction si nécessaire
        should_translate = force_retranslate or not target_desc

        # Vérifier la langue de la traduction existante
        if not should_translate and LANGDETECT_AVAILABLE and target_desc:
            detected_lang = detecter_langue(target_desc)
            if detected_lang and detected_lang != target_lang:
                print(f"{MAGENTA}🔍 Langue détectée incorrecte: {detected_lang} au lieu de {target_lang}{RESET}")
                should_translate = True

        if should_translate:
            try:
                new_translation = traduire(source_desc, target_lang).strip()
                if new_translation and new_translation != target_desc:
                    print(f"{CYAN}🔄 Traduction [{target_lang.upper()}][index {i}]{RESET}")
                    print(f"    Source ({source_lang}) : {source_desc}")
                    print(f"    Ancien : {target_desc}")
                    print(f"    Nouveau : {new_translation}")
                    log_changement(target_lang, i, target_desc, new_translation, basename)
                    target_list[i]["Description"] = new_translation
                    modifications += 1
            except Exception as e:
                logger.error(f"Erreur traduction index {i}: {e}")
                print(f"{ROUGE}❌ Erreur traduction index {i}: {e}{RESET}")

    return modifications

# Configuration management
def load_config() -> configparser.ConfigParser:
    """
    Charge la configuration depuis le fichier sync_config.ini

    Returns:
        ConfigParser avec la configuration chargée
    """
    config = configparser.ConfigParser()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "sync_config.ini")

    if os.path.exists(config_path):
        try:
            config.read(config_path, encoding='utf-8')
            logger.info(f"Configuration chargée depuis: {config_path}")
        except Exception as e:
            logger.warning(f"Erreur chargement configuration: {e}")
    else:
        logger.warning(f"Fichier de configuration non trouvé: {config_path}")

    return config

# Charger la configuration globale
CONFIG = load_config()

def main():
    """Point d'entrée principal du script."""
    parser = argparse.ArgumentParser(
        description='Synchronise un fichier JSON avec ses équivalents dans d\'autres langues',
        epilog='Exemple: python sync_one.py fichier_fr.json --force'
    )
    parser.add_argument('source_file', help='Chemin vers le fichier JSON source')
    parser.add_argument('--force', '-f', action='store_true',
                       help='Force la retraduction même si une traduction existe')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Mode verbeux pour plus de détails')

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setLevel(logging.DEBUG)

    if not args.source_file:
        print(f"{ROUGE}❌ Aucun fichier source spécifié{RESET}")
        logger.error("Aucun fichier source spécifié")
        sys.exit(1)

    logger.info(f"Démarrage avec fichier: {args.source_file}, force: {args.force}")
    success = sync_file(args.source_file, force_retranslate=args.force)

    if success:
        logger.info("Script terminé avec succès")
    else:
        logger.error("Script terminé avec erreur")

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
