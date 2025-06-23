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
from collections import defaultdict
import traceback

def load_json_safe(file_path):
    """Charge un fichier JSON de manière sécurisée."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Erreur lors du chargement de {file_path}: {e}")
        traceback.print_exc()
        return None

def save_json_safe(data, file_path):
    """Sauvegarde un fichier JSON de manière sécurisée avec indentation."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde de {file_path}: {e}")
        traceback.print_exc()
        return False

def extract_ids_from_filename(filename):
    """Extrait les IDs du nom de fichier (ex: faults_000_001_002_255_fr.json -> [0,1,2,255])."""
    parts = filename.replace('.json', '').split('_')
    if len(parts) >= 6 and parts[0] == 'faults':
        try:
            return [int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])]
        except ValueError:
            return None
    return None

def normalize_json_fields(data, filename):
    """Normalise les champs JSON et ajoute les champs manquants."""
    modified = False

    # 1. Collecter tous les headers possibles
    header_data = {}
    header_keys = []

    # Chercher toutes les variations possibles de "header"
    for key in data.keys():
        if key.lower() == 'header':
            header_keys.append(key)
            header_content = data[key]
            if isinstance(header_content, dict):
                header_data.update(header_content)

    # Supprimer tous les anciens headers après la fusion
    for key in header_keys:
        data.pop(key)
        modified = True

    # 2. Normaliser les champs du Header
    field_mapping = {
        'idLevel0': 'IdLevel0',
        'idLevel1': 'IdLevel1',
        'idLevel2': 'IdLevel2',
        'idLevel3': 'IdLevel3',
        'language': 'Language',
        'filename': 'Filename'
    }

    # Convertir les champs en minuscules vers majuscules
    normalized_header = {}
    for key, value in header_data.items():
        normalized_key = field_mapping.get(key.lower(), key)
        normalized_header[normalized_key] = value
        if normalized_key != key:
            modified = True

    # 3. S'assurer que les IDs sont présents et corrects
    ids = extract_ids_from_filename(filename)
    if ids:
        for i, value in enumerate(ids):
            key = f'IdLevel{i}'
            if key not in normalized_header or normalized_header[key] != value:
                normalized_header[key] = value
                modified = True

    # 4. Ajouter ou corriger le Filename
    if 'Filename' not in normalized_header or normalized_header['Filename'] != filename:
        normalized_header['Filename'] = filename
        modified = True

    # 5. Ajouter ou corriger la Language
    expected_lang = filename[-6:-5]  # Extrait 'fr', 'en' ou 'es' du nom de fichier
    if 'Language' not in normalized_header or normalized_header['Language'] in ('n', 'e', 'r', 's', ''):
        if expected_lang in ('fr', 'en', 'es'):
            normalized_header['Language'] = expected_lang
            modified = True

    # 6. Reconstruire le fichier JSON dans le bon ordre
    ordered_data = {}

    # Header en premier
    ordered_data['Header'] = normalized_header

    # Puis les autres champs dans un ordre spécifique
    if 'Version' in data:
        ordered_data['Version'] = data.pop('Version')

    if 'LinkedVariable' in data:
        ordered_data['LinkedVariable'] = data.pop('LinkedVariable')

    # Copier tous les autres champs dans l'ordre où ils apparaissent
    for key, value in data.items():
        ordered_data[key] = value

    # Remplacer les données par la version réordonnée
    data.clear()
    data.update(ordered_data)
    modified = True

    return modified

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
            # Essayer de corriger l'encodage si nécessaire
            data = load_json_safe(file_path)
            if data is None:
                print(f"⚠️ Tentative de correction de l'encodage pour {file_path}")
                if fix_file_encoding(file_path):
                    data = load_json_safe(file_path)
                if data is None:
                    errors['critical'].append(f"❌ {lang}: Impossible de charger {file_path}")
                    continue
            loaded_files[lang] = {'data': data, 'path': file_path}
        else:
            errors['critical'].append(f"❌ {lang}: Fichier manquant {file_path}")

    if len(loaded_files) < 2:
        errors['critical'].append(f"⚠️ Pas assez de fichiers valides pour la comparaison")
        return errors

    # Vérifier et normaliser chaque fichier
    corrected_files = {}
    for lang, file_info in loaded_files.items():
        data = file_info['data']
        filename = os.path.basename(file_info['path'])

        # Vérifier si une normalisation est nécessaire
        if normalize_json_fields(data, filename):
            corrected_files[lang] = {
                'data': data,
                'path': file_info['path']
            }
            errors['metadata'].append(f"⚠️ {lang}: Normalisation des champs nécessaire")

    # Sauvegarder les fichiers corrigés
    for lang, file_info in corrected_files.items():
        try:
            with open(file_info['path'], 'w', encoding='utf-8') as f:
                json.dump(file_info['data'], f, indent=2, ensure_ascii=False)
            print(f"  ✅ Fichier sauvegardé: {os.path.basename(file_info['path'])}")
        except Exception as e:
            print(f"  ❌ Erreur sauvegarde {os.path.basename(file_info['path'])}: {e}")
            errors['critical'].append(f"❌ {lang}: Erreur lors de la sauvegarde")

    # Référence : préférer la version française, sinon premier fichier
    ref_lang = 'fr' if 'fr' in loaded_files else list(loaded_files.keys())[0]
    ref_data = loaded_files[ref_lang]['data']
    ref_path = loaded_files[ref_lang]['path']

    # Comparaisons entre fichiers
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
            except Exception as e:
                print(f"  ❌ Erreur sauvegarde {filename}: {e}")
                traceback.print_exc()

    return fixes_applied

def fix_content_errors(loaded_files):
    """Corrige automatiquement les erreurs de contenu en utilisant la version française comme référence."""
    fixes_applied = 0

    # S'assurer que nous avons une version française pour référence
    if 'fr' not in loaded_files:
        print("❌ Impossible de corriger : pas de version française trouvée")
        return fixes_applied

    ref_data = loaded_files['fr']['data']

    for lang, file_info in loaded_files.items():
        if lang == 'fr':  # Skip reference
            continue

        data = file_info['data']
        file_path = file_info['path']
        filename = os.path.basename(file_path)
        modified = False

        # 1. Corriger LinkedVariable
        if data.get('LinkedVariable') != ref_data.get('LinkedVariable'):
            print(f"  🔧 Correction LinkedVariable {lang}")
            data['LinkedVariable'] = ref_data['LinkedVariable']
            modified = True
            fixes_applied += 1

        # 2. Corriger Version
        if data.get('Version') != ref_data.get('Version'):
            print(f"  🔧 Correction Version {lang}")
            data['Version'] = ref_data['Version']
            modified = True
            fixes_applied += 1

        # 3. Corriger FaultDetailList
        ref_list = ref_data.get('FaultDetailList', [])
        curr_list = data.get('FaultDetailList', [])

        if len(ref_list) != len(curr_list):
            print(f"  🔧 Correction taille FaultDetailList {lang}")
            # Copier la structure de la liste française en gardant les traductions existantes
            new_list = []
            for i, ref_item in enumerate(ref_list):
                new_item = ref_item.copy()
                if i < len(curr_list):
                    # Garder la description traduite si elle existe
                    if curr_list[i].get('Description', '').strip():
                        new_item['Description'] = curr_list[i]['Description']
                new_list.append(new_item)
            data['FaultDetailList'] = new_list
            modified = True
            fixes_applied += 1
        else:
            # Corriger les IsExpandable tout en préservant les traductions
            for idx, (ref_item, curr_item) in enumerate(zip(ref_list, curr_list)):
                if ref_item.get('IsExpandable') != curr_item.get('IsExpandable'):
                    print(f"  🔧 Correction IsExpandable {lang} à l'index {idx}")
                    curr_item['IsExpandable'] = ref_item['IsExpandable']
                    modified = True
                    fixes_applied += 1

                # Cohérence des descriptions vides
                ref_desc = ref_item.get('Description', '').strip()
                curr_desc = curr_item.get('Description', '').strip()

                if (ref_desc == '') != (curr_desc == ''):
                    print(f"  🔧 Correction Description vide {lang} à l'index {idx}")
                    if ref_desc == '':
                        curr_item['Description'] = ''
                    modified = True
                    fixes_applied += 1

        # Sauvegarder le fichier si modifié
        if modified:
            if save_json_safe(data, file_path):
                print(f"  ✅ Fichier sauvegardé: {filename}")
            else:
                print(f"  ❌ Erreur sauvegarde {filename}")

    return fixes_applied

def fix_all_metadata_errors(files_group):
    """Corrige tous les problèmes de métadonnées dans un groupe de fichiers."""
    fixes_applied = 0

    for lang, file_info in files_group.items():
        file_path = file_info['path']
        data = file_info['data']
        filename = os.path.basename(file_path)

        # 1. Normaliser les champs
        if normalize_json_fields(data, filename):
            fixes_applied += 1

        # 2. Sauvegarder si des modifications ont été faites
        if fixes_applied > 0:
            if save_json_safe(data, file_path):
                print(f"  ✅ Fichier normalisé et sauvegardé: {filename}")
            else:
                print(f"  ❌ Erreur lors de la sauvegarde de {filename}")

    return fixes_applied

def fix_file_encoding(file_path):
    """Tente de corriger l'encodage d'un fichier JSON."""
    try:
        # Essayer d'abord avec utf-8
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return True
    except UnicodeDecodeError:
        try:
            # Si utf-8 échoue, essayer avec latin1 (qui peut lire n'importe quels octets)
            with open(file_path, 'r', encoding='latin1') as f:
                content = f.read()

            # Écrire le contenu en UTF-8
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"❌ Impossible de corriger l'encodage de {file_path}: {e}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors de la lecture de {file_path}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Vérifie la cohérence des fichiers de traduction (optimisé)')
    parser.add_argument('base_dir', help='Répertoire de base à vérifier')
    parser.add_argument('--verbose', '-v', action='store_true', help='Mode verbeux')
    parser.add_argument('--quick', '-q', action='store_true', help='Vérification rapide (arrêt au premier problème critique)')
    parser.add_argument('--fix', '-f', action='store_true', help='Corriger automatiquement les erreurs de métadonnées et de contenu')
    parser.add_argument('--metadata-only', '-m', action='store_true', help='Corriger uniquement les erreurs de métadonnées')

    args = parser.parse_args()

    if not os.path.exists(args.base_dir):
        print(f"❌ Répertoire introuvable : {args.base_dir}")
        sys.exit(1)

    print(f"🔍 Vérification optimisée de cohérence dans : {args.base_dir}")
    if args.fix:
        print("🔧 Mode correction automatique activé")
        if args.metadata_only:
            print("   Mode correction métadonnées uniquement")

    # Trouver tous les groupes de fichiers
    file_groups = find_file_groups(args.base_dir)

    if not file_groups:
        print("❌ Aucun fichier JSON trouvé")
        sys.exit(1)

    print(f"📁 {len(file_groups)} groupes de fichiers trouvés")

    all_errors = {}
    groups_with_errors = 0
    total_fixes = 0
    total_content_fixes = 0

    # Vérifier chaque groupe avec la nouvelle méthode
    for group in file_groups:
        errors = check_translation_file_coherence(group)

        # Compter les erreurs significatives (pas les warnings seuls)
        significant_errors = len(errors['critical']) + len(errors['metadata']) + len(errors['content'])

        if significant_errors > 0:
            groups_with_errors += 1
            all_errors[group['base_name']] = errors

            # Appliquer les corrections si demandé
            if args.fix:
                # Recharger les fichiers pour les corrections
                loaded_files = {}
                for lang, file_path in group['files'].items():
                    if os.path.exists(file_path):
                        data = load_json_safe(file_path)
                        if data is not None:
                            loaded_files[lang] = {'data': data, 'path': file_path}

                if errors['metadata']:
                    print(f"\n🔧 Correction des erreurs de métadonnées pour : {group['base_name']}")
                    fixes = fix_metadata_errors(loaded_files, errors)
                    total_fixes += fixes
                    print(f"  ✅ {fixes} corrections métadonnées appliquées")

                # Corriger le contenu seulement si demandé et si des erreurs existent
                if not args.metadata_only and (errors['critical'] or errors['content']):
                    print(f"\n🔧 Correction des erreurs de contenu pour : {group['base_name']}")
                    fixes = fix_content_errors(loaded_files)
                    total_content_fixes += fixes
                    print(f"  ✅ {fixes} corrections contenu appliquées")

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
        print(f"   🔧 Corrections métadonnées : {total_fixes}")
        if not args.metadata_only:
            print(f"   🔧 Corrections contenu    : {total_content_fixes}")
        print(f"   🔧 Total corrections      : {total_fixes + total_content_fixes}")

    if total_errors == 0:
        print("🎉 Tous les fichiers sont cohérents !")
        return 0
    return 1

if __name__ == '__main__':
    sys.exit(main())
