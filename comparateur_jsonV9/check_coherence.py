#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script optimisé pour vérifier la cohérence des fichiers JSON de traduction.
Vérifie spécifiquement la structure des fichiers faults_*.json.
"""

import os
import sys
import json
import argparse
import traceback
from collections import defaultdict

def load_json_safe(file_path):
    """Charge un fichier JSON de manière sécurisée."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"❌ Erreur lors du chargement de {file_path}: {e}")  # handled for visibility
        traceback.print_exc()
        return None

def extract_ids_from_filename(filename):
    """Extrait les IDs du nom de fichier (ex: faults_000_001_002_255_fr.json -> [0,1,2,255])."""
    parts = filename.replace('.json', '').split('_')
    if len(parts) >= 6 and parts[0] == 'faults':
        try:
            return [int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])]
        except ValueError:
            return None
    return None

def check_translation_file_coherence(files_group):
    """Vérifie spécifiquement la cohérence d'un groupe de fichiers de traduction."""
    errors = {
        'critical': [],  # Erreurs critiques (structure)
        'metadata': [],  # Erreurs de métadonnées
        'content': [],   # Erreurs de contenu
        'warnings': []   # Avertissements
    }

    base_name = files_group['base_name']
    print(f"\n🔍 Vérification optimisée : {base_name}")

    # Charger tous les fichiers valides
    loaded_files = {}
    for lang, file_path in files_group['files'].items():
        if os.path.exists(file_path):
            data = load_json_safe(file_path)
            if data is not None:
                loaded_files[lang] = {'data': data, 'path': file_path}
            else:
                errors['critical'].append(f"❌ {lang}: Impossible de charger {file_path}")
        else:
            errors['critical'].append(f"❌ {lang}: Fichier manquant {file_path}")

    if len(loaded_files) < 2:
        errors['critical'].append(f"⚠️ Pas assez de fichiers valides pour la comparaison")
        return errors

    # Référence : premier fichier trouvé
    ref_lang = list(loaded_files.keys())[0]
    ref_data = loaded_files[ref_lang]['data']
    ref_path = loaded_files[ref_lang]['path']

    # 1. Vérifications de métadonnées et structure
    expected_ids = extract_ids_from_filename(os.path.basename(ref_path))

    for lang, file_info in loaded_files.items():
        data = file_info['data']
        file_path = file_info['path']
        filename = os.path.basename(file_path)

        # Vérifier la structure de base
        required_keys = ['Header', 'LinkedVariable', 'Version', 'FaultDetailList']
        for key in required_keys:
            if key not in data:
                errors['critical'].append(f"❌ {lang}: Clé manquante '{key}'")

        if 'Header' in data:
            header = data['Header']

            # Vérifier les IDs dans le header
            if expected_ids:
                header_ids = [
                    header.get('IdLevel0'), header.get('IdLevel1'),
                    header.get('IdLevel2'), header.get('IdLevel3')
                ]
                if header_ids != expected_ids:
                    errors['metadata'].append(
                        f"⚠️ {lang}: IDs incohérents - Fichier: {expected_ids}, Header: {header_ids}"
                    )

            # Vérifier la langue dans le header
            if header.get('Language') != lang:
                errors['metadata'].append(
                    f"⚠️ {lang}: Langue dans Header ('{header.get('Language')}') != nom fichier ('{lang}')"
                )

            # Vérifier le nom de fichier dans le header
            if header.get('Filename') != filename:
                errors['metadata'].append(
                    f"⚠️ {lang}: Filename dans Header ('{header.get('Filename')}') != nom réel ('{filename}')"
                )

    # 2. Comparaisons entre fichiers
    languages = list(loaded_files.keys())
    for i, lang in enumerate(languages):
        if i == 0:  # Skip reference
            continue

        curr_data = loaded_files[lang]['data']

        # Comparer LinkedVariable (doit être identique)
        if curr_data.get('LinkedVariable') != ref_data.get('LinkedVariable'):
            errors['metadata'].append(
                f"⚠️ {lang} vs {ref_lang}: LinkedVariable différente"
            )

        # Comparer Version (doit être identique)
        if curr_data.get('Version') != ref_data.get('Version'):
            errors['warnings'].append(
                f"⚠️ {lang} vs {ref_lang}: Version différente ({curr_data.get('Version')} vs {ref_data.get('Version')})"
            )

        # Vérifier FaultDetailList
        ref_list = ref_data.get('FaultDetailList', [])
        curr_list = curr_data.get('FaultDetailList', [])

        if len(ref_list) != len(curr_list):
            errors['critical'].append(
                f"❌ {lang} vs {ref_lang}: Nombre d'éléments différent dans FaultDetailList ({len(curr_list)} vs {len(ref_list)})"
            )
        else:
            # Vérifier que IsExpandable est identique pour chaque élément
            for idx, (ref_item, curr_item) in enumerate(zip(ref_list, curr_list)):
                if ref_item.get('IsExpandable') != curr_item.get('IsExpandable'):
                    errors['content'].append(
                        f"❌ {lang} vs {ref_lang}: IsExpandable différent à l'index {idx}"
                    )

                # Vérifier que les descriptions vides le restent
                ref_desc = ref_item.get('Description', '').strip()
                curr_desc = curr_item.get('Description', '').strip()

                if (ref_desc == '') != (curr_desc == ''):
                    errors['content'].append(
                        f"⚠️ {lang} vs {ref_lang}: Description vide/non-vide incohérente à l'index {idx}"
                    )

    return errors

def print_error_summary(all_errors):
    """Affiche un résumé détaillé des erreurs trouvées."""
    total_critical = sum(len(errors['critical']) for errors in all_errors.values())
    total_metadata = sum(len(errors['metadata']) for errors in all_errors.values())
    total_content = sum(len(errors['content']) for errors in all_errors.values())
    total_warnings = sum(len(errors['warnings']) for errors in all_errors.values())

    print(f"\n📊 Résumé détaillé :")
    print(f"   🔴 Erreurs critiques : {total_critical}")
    print(f"   🟠 Erreurs métadonnées : {total_metadata}")
    print(f"   🟡 Erreurs contenu : {total_content}")
    print(f"   🔵 Avertissements : {total_warnings}")

    if total_critical > 0:
        print(f"\n🔴 ERREURS CRITIQUES À CORRIGER :")
        for group_name, errors in all_errors.items():
            if errors['critical']:
                print(f"  📁 {group_name}:")
                for error in errors['critical']:
                    print(f"    {error}")

    if total_metadata > 0:
        print(f"\n🟠 ERREURS DE MÉTADONNÉES :")
        for group_name, errors in all_errors.items():
            if errors['metadata']:
                print(f"  📁 {group_name}:")
                for error in errors['metadata']:
                    print(f"    {error}")

    if total_content > 0:
        print(f"\n🟡 ERREURS DE CONTENU :")
        for group_name, errors in all_errors.items():
            if errors['content']:
                print(f"  📁 {group_name}:")
                for error in errors['content']:
                    print(f"    {error}")

    return total_critical + total_metadata + total_content

def check_file_group_coherence(files_group):
    """Vérifie la cohérence d'un groupe de fichiers avec la nouvelle méthode optimisée."""
    return check_translation_file_coherence(files_group)

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

def fix_metadata_errors(files_group, errors):
    """Corrige automatiquement les erreurs de métadonnées détectées."""
    fixes_applied = 0

    for lang, file_info in files_group.items():
        if lang not in ['fr', 'en', 'es']:
            continue

        file_path = file_info['path']
        data = file_info['data']
        filename = os.path.basename(file_path)
        modified = False

        if 'Header' in data:
            header = data['Header']

            # Corriger la langue dans le header
            if header.get('Language') != lang:
                print(f"  🔧 Correction langue {lang}: '{header.get('Language')}' -> '{lang}'")
                header['Language'] = lang
                modified = True
                fixes_applied += 1

            # Corriger le nom de fichier dans le header
            if header.get('Filename') != filename:
                print(f"  🔧 Correction filename {lang}: '{header.get('Filename')}' -> '{filename}'")
                header['Filename'] = filename
                modified = True
                fixes_applied += 1

            # Corriger les IDs dans le header
            expected_ids = extract_ids_from_filename(filename)
            if expected_ids:
                header_ids = [
                    header.get('IdLevel0'), header.get('IdLevel1'),
                    header.get('IdLevel2'), header.get('IdLevel3')
                ]
                if header_ids != expected_ids:
                    print(f"  🔧 Correction IDs {lang}: {header_ids} -> {expected_ids}")
                    header['IdLevel0'] = expected_ids[0]
                    header['IdLevel1'] = expected_ids[1]
                    header['IdLevel2'] = expected_ids[2]
                    header['IdLevel3'] = expected_ids[3]
                    modified = True
                    fixes_applied += 1

        # Sauvegarder le fichier si modifié
        if modified:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"  ✅ Fichier sauvegardé: {filename}")
            except OSError as e:
                print(f"  ❌ Erreur sauvegarde {filename}: {e}")  # handled for visibility
                traceback.print_exc()

    return fixes_applied

def main():
    parser = argparse.ArgumentParser(description='Vérifie la cohérence des fichiers de traduction (optimisé)')
    parser.add_argument('base_dir', help='Répertoire de base à vérifier')
    parser.add_argument('--verbose', '-v', action='store_true', help='Mode verbeux')
    parser.add_argument('--quick', '-q', action='store_true', help='Vérification rapide (arrêt au premier problème critique)')
    parser.add_argument('--fix', '-f', action='store_true', help='Corriger automatiquement les erreurs de métadonnées')

    args = parser.parse_args()

    if not os.path.exists(args.base_dir):
        print(f"❌ Répertoire introuvable : {args.base_dir}")
        sys.exit(1)

    print(f"🔍 Vérification optimisée de cohérence dans : {args.base_dir}")
    if args.fix:
        print("🔧 Mode correction automatique activé")

    # Trouver tous les groupes de fichiers
    file_groups = find_file_groups(args.base_dir)

    if not file_groups:
        print("❌ Aucun fichier JSON trouvé")
        sys.exit(1)

    print(f"📁 {len(file_groups)} groupes de fichiers trouvés")

    all_errors = {}
    groups_with_errors = 0
    total_fixes = 0

    # Vérifier chaque groupe avec la nouvelle méthode
    for group in file_groups:
        errors = check_translation_file_coherence(group)

        # Compter les erreurs significatives (pas les warnings seuls)
        significant_errors = len(errors['critical']) + len(errors['metadata']) + len(errors['content'])

        if significant_errors > 0:
            groups_with_errors += 1
            all_errors[group['base_name']] = errors

            # Appliquer les corrections si demandé
            if args.fix and errors['metadata']:
                print(f"\n🔧 Correction des erreurs de métadonnées pour : {group['base_name']}")
                  # Recharger les fichiers pour les corrections
                loaded_files = {}
                for lang, file_path in group['files'].items():
                    if os.path.exists(file_path):
                        data = load_json_safe(file_path)
                        if data is not None:
                            loaded_files[lang] = {'data': data, 'path': file_path}

                fixes = fix_metadata_errors(loaded_files, errors)
                total_fixes += fixes
                print(f"  ✅ {fixes} corrections appliquées")

            if args.quick:
                print(f"⚠️ Mode rapide : arrêt après la première erreur critique détectée")
                break
        else:
            print(f"  ✅ {group['base_name']}: Cohérent")

    # Afficher le résumé détaillé
    total_errors = print_error_summary(all_errors)

    print(f"\n📊 Résumé final :")
    print(f"   📁 Groupes vérifiés     : {len(file_groups)}")
    print(f"   ❌ Groupes avec erreurs : {groups_with_errors}")
    print(f"   🔍 Total erreurs        : {total_errors}")

    if args.fix:
        print(f"   🔧 Corrections appliquées : {total_fixes}")

    if total_errors == 0:
        print("🎉 Tous les fichiers sont cohérents !")
        sys.exit(0)
    else:
        if args.fix and total_fixes > 0:
            print("✅ Des corrections ont été appliquées, relancez la vérification")
        else:
            print("⚠️ Des incohérences ont été détectées")
        sys.exit(1)

if __name__ == "__main__":
    main()
