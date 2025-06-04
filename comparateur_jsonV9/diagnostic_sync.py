#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour diagnostiquer les problèmes de synchronisation dans les fichiers JSON.
Détecte les incohérences où des entrées vides dans les masters génèrent des traductions.
"""

import os
import json
import glob
from pathlib import Path

def diagnostiquer_dossier(dossier_json):
    """
    Diagnostique tous les fichiers JSON dans un dossier pour détecter les problèmes de synchronisation.

    Args:
        dossier_json: Chemin vers le dossier contenant les fichiers JSON
    """
    if not os.path.exists(dossier_json):
        print(f"❌ Dossier introuvable : {dossier_json}")
        return False

    # Trouver tous les fichiers français (master)
    pattern_fr = os.path.join(dossier_json, "**", "*_fr.json")
    fichiers_fr = glob.glob(pattern_fr, recursive=True)

    if not fichiers_fr:
        print(f"❌ Aucun fichier français trouvé dans : {dossier_json}")
        return False

    print(f"🔍 Diagnostic de {len(fichiers_fr)} fichiers maîtres français...")
    print("=" * 80)

    problemes_totaux = 0

    for fichier_fr in sorted(fichiers_fr):
        print(f"\n📄 Analyse de : {os.path.relpath(fichier_fr, dossier_json)}")

        try:
            # Charger le fichier français
            with open(fichier_fr, 'r', encoding='utf-8') as f:
                data_fr = json.load(f)

            # Déterminer les fichiers cibles
            fichier_en = fichier_fr.replace('_fr.json', '_en.json')
            fichier_es = fichier_fr.replace('_fr.json', '_es.json')

            # Diagnostiquer chaque langue cible
            for lang, fichier_target in [('EN', fichier_en), ('ES', fichier_es)]:
                if not os.path.exists(fichier_target):
                    print(f"  ⚠️ Fichier {lang} manquant : {os.path.basename(fichier_target)}")
                    continue

                # Charger le fichier cible
                with open(fichier_target, 'r', encoding='utf-8') as f:
                    data_target = json.load(f)

                # Analyser les FaultDetailList
                fault_list_fr = data_fr.get("FaultDetailList", [])
                fault_list_target = data_target.get("FaultDetailList", [])

                problemes_fichier = []

                for i, fault_fr in enumerate(fault_list_fr):
                    if i >= len(fault_list_target):
                        break

                    desc_fr = fault_fr.get("Description", "").strip()
                    desc_target = fault_list_target[i].get("Description", "").strip()

                    # Problème 1: Entrée française vide mais traduction non vide
                    if not desc_fr and desc_target:
                        problemes_fichier.append({
                            'type': 'entrée_vide_traduite',
                            'index': i,
                            'fr': desc_fr,
                            'target': desc_target
                        })

                    # Problème 2: Traductions suspectes (messages d'erreur AI)
                    if desc_target and any(phrase in desc_target.lower() for phrase in [
                        "lo siento", "sorry", "i can't", "je ne peux pas"
                    ]):
                        problemes_fichier.append({
                            'type': 'traduction_suspecte',
                            'index': i,
                            'fr': desc_fr,
                            'target': desc_target
                        })

                    # Problème 3: Traductions manifestement incorrectes
                    if desc_fr == "chat" and desc_target not in ["cat", "gato"]:
                        problemes_fichier.append({
                            'type': 'traduction_incorrecte',
                            'index': i,
                            'fr': desc_fr,
                            'target': desc_target,
                            'attendue': "cat" if lang == "EN" else "gato"
                        })

                # Afficher les problèmes trouvés
                if problemes_fichier:
                    print(f"  🚨 {len(problemes_fichier)} problème(s) détecté(s) en {lang} :")
                    for prob in problemes_fichier:
                        if prob['type'] == 'entrée_vide_traduite':
                            print(f"    [Index {prob['index']}] Entrée vide traduite : '' → '{prob['target']}'")
                        elif prob['type'] == 'traduction_suspecte':
                            print(f"    [Index {prob['index']}] Traduction suspecte : '{prob['fr']}' → '{prob['target']}'")
                        elif prob['type'] == 'traduction_incorrecte':
                            print(f"    [Index {prob['index']}] Traduction incorrecte : '{prob['fr']}' → '{prob['target']}' (attendue: '{prob['attendue']}')")

                    problemes_totaux += len(problemes_fichier)
                else:
                    print(f"  ✅ Fichier {lang} correct")

        except Exception as e:
            print(f"  ❌ Erreur lors de l'analyse : {e}")
            continue

    print("\n" + "=" * 80)
    if problemes_totaux > 0:
        print(f"🚨 RÉSUMÉ : {problemes_totaux} problème(s) de synchronisation détecté(s)")
        print("\n💡 Pour corriger, utilisez :")
        print("   python corriger_sync.py <fichier_fr.json>")
    else:
        print("✅ RÉSUMÉ : Aucun problème de synchronisation détecté")

    return problemes_totaux == 0

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Diagnostique les problèmes de synchronisation dans les fichiers JSON'
    )
    parser.add_argument('dossier', nargs='?',
                       default="../JSON",
                       help='Dossier contenant les fichiers JSON à diagnostiquer (défaut: ../JSON)')

    args = parser.parse_args()

    success = diagnostiquer_dossier(args.dossier)
    exit(0 if success else 1)

if __name__ == "__main__":
    main()
