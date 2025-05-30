#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour vérifier la cohérence des fichiers JSON de traduction.
"""

import os
import sys
import json
import argparse

def load_json_safe(file_path):
    """Charge un fichier JSON de manière sécurisée."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Erreur lors du chargement de {file_path}: {e}")
        return None

def compare_structures(data1, data2, path=""):
    """Compare récursivement deux structures de données."""
    differences = []

    if type(data1) != type(data2):
        differences.append(f"{path}: Types différents ({type(data1).__name__} vs {type(data2).__name__})")
        return differences

    if isinstance(data1, dict):
        # Vérifier les clés manquantes
        keys1 = set(data1.keys())
        keys2 = set(data2.keys())

        missing_in_2 = keys1 - keys2
        missing_in_1 = keys2 - keys1

        for key in missing_in_2:
            differences.append(f"{path}.{key}: Clé manquante dans le second fichier")

        for key in missing_in_1:
            differences.append(f"{path}.{key}: Clé manquante dans le premier fichier")

        # Comparer les clés communes (sauf Description qui peut différer)
        common_keys = keys1 & keys2
        for key in common_keys:
            if key != "Description":  # Les descriptions peuvent légitimement différer
                sub_path = f"{path}.{key}" if path else key
                differences.extend(compare_structures(data1[key], data2[key], sub_path))

    elif isinstance(data1, list):
        if len(data1) != len(data2):
            differences.append(f"{path}: Longueurs de listes différentes ({len(data1)} vs {len(data2)})")

        min_len = min(len(data1), len(data2))
        for i in range(min_len):
            sub_path = f"{path}[{i}]" if path else f"[{i}]"
            differences.extend(compare_structures(data1[i], data2[i], sub_path))

    # Pour les types primitifs, on ne compare pas les descriptions

    return differences

def check_file_group_coherence(files_group):
    """Vérifie la cohérence d'un groupe de fichiers (fr, en, es)."""
    print(f"\n🔍 Vérification du groupe : {files_group['base_name']}")

    loaded_files = {}
    for lang, file_path in files_group['files'].items():
        if os.path.exists(file_path):
            data = load_json_safe(file_path)
            if data is not None:
                loaded_files[lang] = data
            else:
                print(f"  ❌ Impossible de charger {lang}: {file_path}")
        else:
            print(f"  ⚠️ Fichier manquant {lang}: {file_path}")

    if len(loaded_files) < 2:
        print(f"  ⚠️ Pas assez de fichiers valides pour comparer")
        return []

    # Comparer toutes les paires
    languages = list(loaded_files.keys())
    all_differences = []

    for i in range(len(languages)):
        for j in range(i + 1, len(languages)):
            lang1, lang2 = languages[i], languages[j]
            print(f"  📊 Comparaison {lang1} ↔ {lang2}")

            differences = compare_structures(loaded_files[lang1], loaded_files[lang2])

            if differences:
                print(f"    ❌ {len(differences)} différences trouvées")
                for diff in differences[:5]:  # Afficher seulement les 5 premières
                    print(f"      • {diff}")
                if len(differences) > 5:
                    print(f"      ... et {len(differences) - 5} autres")
                all_differences.extend(differences)
            else:
                print(f"    ✅ Structures identiques")

    return all_differences

def find_file_groups(base_dir):
    """Trouve tous les groupes de fichiers de traduction."""
    file_groups = {}

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.json'):
                # Extraire le nom de base et la langue
                if file.endswith('_fr.json'):
                    base_name = file[:-7]
                    lang = 'fr'
                elif file.endswith('_en.json'):
                    base_name = file[:-7]
                    lang = 'en'
                elif file.endswith('_es.json'):
                    base_name = file[:-7]
                    lang = 'es'
                else:
                    continue

                full_path = os.path.join(root, file)
                relative_dir = os.path.relpath(root, base_dir)

                key = (base_name, relative_dir)
                if key not in file_groups:
                    file_groups[key] = {
                        'base_name': f"{relative_dir}/{base_name}" if relative_dir != "." else base_name,
                        'files': {}
                    }

                file_groups[key]['files'][lang] = full_path

    return list(file_groups.values())

def main():
    parser = argparse.ArgumentParser(description='Vérifie la cohérence des fichiers de traduction')
    parser.add_argument('base_dir', help='Répertoire de base à vérifier')
    parser.add_argument('--verbose', '-v', action='store_true', help='Mode verbeux')

    args = parser.parse_args()

    if not os.path.exists(args.base_dir):
        print(f"❌ Répertoire introuvable : {args.base_dir}")
        sys.exit(1)

    print(f"🔍 Vérification de cohérence dans : {args.base_dir}")

    # Trouver tous les groupes de fichiers
    file_groups = find_file_groups(args.base_dir)

    if not file_groups:
        print("❌ Aucun fichier JSON trouvé")
        sys.exit(1)

    print(f"📁 {len(file_groups)} groupes de fichiers trouvés")

    total_differences = 0
    groups_with_errors = 0

    # Vérifier chaque groupe
    for group in file_groups:
        differences = check_file_group_coherence(group)
        if differences:
            groups_with_errors += 1
            total_differences += len(differences)

    print(f"\n📊 Résumé de la vérification :")
    print(f"   📁 Groupes vérifiés     : {len(file_groups)}")
    print(f"   ❌ Groupes avec erreurs : {groups_with_errors}")
    print(f"   🔍 Total différences    : {total_differences}")

    if total_differences == 0:
        print("🎉 Tous les fichiers sont cohérents !")
        sys.exit(0)
    else:
        print("⚠️ Des incohérences ont été détectées")
        sys.exit(1)

if __name__ == "__main__":
    main()
