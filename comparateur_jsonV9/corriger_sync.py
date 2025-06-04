#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour corriger les problèmes de synchronisation où des entrées vides
dans le fichier français master génèrent quand même des traductions.
"""

import os
import json
import argparse
from datetime import datetime

def corriger_synchronisation(fichier_fr_path):
    """
    Corrige les problèmes de synchronisation pour un fichier français donné.

    Args:
        fichier_fr_path: Chemin vers le fichier français master
    """
    if not os.path.exists(fichier_fr_path):
        print(f"❌ Fichier source introuvable : {fichier_fr_path}")
        return False

    # Déterminer les fichiers cibles
    basename = os.path.basename(fichier_fr_path)
    if not basename.endswith('_fr.json'):
        print(f"❌ Le fichier doit être un fichier français (_fr.json) : {basename}")
        return False

    fichier_en_path = fichier_fr_path.replace('_fr.json', '_en.json')
    fichier_es_path = fichier_fr_path.replace('_fr.json', '_es.json')

    try:
        # Charger le fichier français master
        with open(fichier_fr_path, 'r', encoding='utf-8') as f:
            data_fr = json.load(f)

        print(f"✅ Fichier français chargé : {basename}")

        # Traiter les fichiers anglais et espagnol
        for lang, target_path in [('en', fichier_en_path), ('es', fichier_es_path)]:
            if not os.path.exists(target_path):
                print(f"⚠️ Fichier {lang} introuvable : {os.path.basename(target_path)}")
                continue

            # Charger le fichier cible
            with open(target_path, 'r', encoding='utf-8') as f:
                data_target = json.load(f)

            modifications = 0
            fault_list_fr = data_fr.get("FaultDetailList", [])
            fault_list_target = data_target.get("FaultDetailList", [])

            # Vérifier chaque entrée
            for i, fault_fr in enumerate(fault_list_fr):
                if i >= len(fault_list_target):
                    break

                desc_fr = fault_fr.get("Description", "").strip()
                desc_target = fault_list_target[i].get("Description", "").strip()

                # Si l'entrée française est vide mais la traduction ne l'est pas
                if not desc_fr and desc_target:
                    print(f"🔧 Correction [{lang.upper()}][index {i}] : '{desc_target}' → ''")
                    fault_list_target[i]["Description"] = ""
                    modifications += 1

                # Cas spécial : "chat" doit être traduit correctement
                elif desc_fr == "chat":
                    correct_translation = "cat" if lang == "en" else "gato"
                    if desc_target != correct_translation:
                        print(f"🔧 Correction traduction [{lang.upper()}][index {i}] : '{desc_target}' → '{correct_translation}'")
                        fault_list_target[i]["Description"] = correct_translation
                        modifications += 1

            # Sauvegarder si des modifications ont été faites
            if modifications > 0:
                # Créer une sauvegarde
                backup_path = target_path.replace('.json', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    json.dump(data_target, f, ensure_ascii=False, indent=2)
                print(f"📦 Sauvegarde créée : {os.path.basename(backup_path)}")

                # Sauvegarder le fichier corrigé
                with open(target_path, 'w', encoding='utf-8') as f:
                    json.dump(data_target, f, ensure_ascii=False, indent=2)
                print(f"✅ Fichier {lang} corrigé ({modifications} modifications) : {os.path.basename(target_path)}")
            else:
                print(f"✅ Fichier {lang} déjà correct : {os.path.basename(target_path)}")

        return True

    except Exception as e:
        print(f"❌ Erreur lors de la correction : {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Corrige les problèmes de synchronisation où des entrées vides génèrent des traductions'
    )
    parser.add_argument('fichier_fr', help='Chemin vers le fichier français master à corriger')

    args = parser.parse_args()

    success = corriger_synchronisation(args.fichier_fr)
    exit(0 if success else 1)

if __name__ == "__main__":
    main()
