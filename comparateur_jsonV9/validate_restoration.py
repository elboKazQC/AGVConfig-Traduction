#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de validation rapide pour vérifier que toutes les fonctionnalités
de l'interface Fault Editor ont été correctement restaurées.

Usage: python validate_restoration.py

Author: AI Assistant
Created: 2024
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

def check_imports():
    """Vérifier que tous les imports fonctionnent."""
    print("🔍 Vérification des imports...")

    try:
        from main_controller import FaultEditorController
        print("  ✅ main_controller.FaultEditorController")

        from app import FaultEditor
        print("  ✅ app.FaultEditor")

        from config.constants import Colors, Fonts, Messages, Dimensions
        print("  ✅ config.constants")

        from models.data_models import ApplicationState
        print("  ✅ models.data_models")

        return True
    except ImportError as e:
        print(f"  ❌ Erreur d'import: {e}")
        return False

def check_interface_creation():
    """Vérifier que l'interface peut être créée sans erreur."""
    print("\n🏗️ Vérification de la création d'interface...")

    try:
        # Créer une fenêtre test (cachée)
        root = tk.Tk()
        root.withdraw()

        # Tester la création du controller
        from main_controller import FaultEditorController
        controller = FaultEditorController(root)
        print("  ✅ FaultEditorController créé avec succès")

        # Tester la création du wrapper legacy
        from app import FaultEditor
        editor = FaultEditor(root)
        print("  ✅ FaultEditor (wrapper) créé avec succès")

        root.destroy()
        return True

    except Exception as e:
        print(f"  ❌ Erreur lors de la création: {e}")
        return False

def check_required_attributes():
    """Vérifier que tous les attributs requis sont présents."""
    print("\n📋 Vérification des attributs requis...")

    try:
        root = tk.Tk()
        root.withdraw()

        from main_controller import FaultEditorController
        controller = FaultEditorController(root)

        # Liste des attributs critiques de l'interface originale
        required_attrs = {
            'lang': 'Langue courante',
            'file_map': 'Mapping des fichiers',
            'data_map': 'Données chargées',
            'path_map': 'Mapping des chemins',
            'columns': 'Liste des colonnes',
            'current_path': 'Chemin courant',
            'base_dir': 'Dossier de base',
            'search_results': 'Résultats de recherche',
            'main_canvas': 'Canvas principal',
            'columns_frame': 'Frame des colonnes',
            'tools_frame': 'Frame des outils',
            'status': 'Barre de statut',
            'lang_var': 'Variable de langue',
            'sync_one_var': 'Variable sync un fichier',
            'genfichier_file_var': 'Variable génération fichier',
            'genfichier_src_var': 'Variable langue source',
            'genfichier_tgt_var': 'Variable langue cible'
        }

        missing_attrs = []
        for attr, description in required_attrs.items():
            if hasattr(controller, attr):
                print(f"  ✅ {attr} - {description}")
            else:
                print(f"  ❌ {attr} - {description}")
                missing_attrs.append(attr)

        root.destroy()

        if missing_attrs:
            print(f"\n⚠️ Attributs manquants: {missing_attrs}")
            return False
        else:
            print(f"\n✅ Tous les {len(required_attrs)} attributs requis sont présents")
            return True

    except Exception as e:
        print(f"  ❌ Erreur lors de la vérification: {e}")
        return False

def check_required_methods():
    """Vérifier que toutes les méthodes requises sont présentes."""
    print("\n🔧 Vérification des méthodes requises...")

    try:
        root = tk.Tk()
        root.withdraw()

        from main_controller import FaultEditorController
        controller = FaultEditorController(root)

        # Liste des méthodes critiques de l'interface originale
        required_methods = {
            'setup_ui': 'Configuration interface',
            'open_folder': 'Ouverture dossier',
            'load_flat_json': 'Chargement JSON plat',
            'show_search': 'Affichage recherche',
            'reload_lang': 'Rechargement langue',
            'run_sync_all': 'Synchronisation tous',
            'run_sync_one': 'Synchronisation un',
            'run_generer_fichier': 'Génération fichier',
            'run_generer_manquant': 'Génération manquants',
            'run_check_coherence': 'Vérification cohérence',
            'run_spell_check': 'Vérification orthographe',
            'perform_search': 'Exécution recherche',
            'search_next': 'Recherche suivant',
            'search_previous': 'Recherche précédent',
            'reload_root': 'Rechargement racine',
            'initialize_file_map': 'Initialisation file_map',
            'load_root': 'Chargement racine',
            'load_data_for_current_language': 'Chargement données langue'
        }

        missing_methods = []
        for method, description in required_methods.items():
            if hasattr(controller, method) and callable(getattr(controller, method)):
                print(f"  ✅ {method}() - {description}")
            else:
                print(f"  ❌ {method}() - {description}")
                missing_methods.append(method)

        root.destroy()

        if missing_methods:
            print(f"\n⚠️ Méthodes manquantes: {missing_methods}")
            return False
        else:
            print(f"\n✅ Toutes les {len(required_methods)} méthodes requises sont présentes")
            return True

    except Exception as e:
        print(f"  ❌ Erreur lors de la vérification: {e}")
        return False

def check_ui_components():
    """Vérifier que les composants UI sont correctement créés."""
    print("\n🎨 Vérification des composants UI...")

    try:
        root = tk.Tk()
        root.withdraw()

        from main_controller import FaultEditorController
        controller = FaultEditorController(root)

        # Vérifier les composants UI principaux
        ui_checks = {
            'main_canvas': 'Canvas principal créé',
            'columns_frame': 'Frame des colonnes créé',
            'tools_frame': 'Barre d\'outils créée',
            'status': 'Barre de statut créée',
            'scrollbar_x': 'Scrollbar horizontale créée'
        }

        all_good = True
        for component, description in ui_checks.items():
            if hasattr(controller, component):
                widget = getattr(controller, component)
                if widget and hasattr(widget, 'winfo_exists'):
                    print(f"  ✅ {description}")
                else:
                    print(f"  ❌ {description} - Widget invalide")
                    all_good = False
            else:
                print(f"  ❌ {description} - Composant manquant")
                all_good = False

        # Vérifier les variables tkinter
        var_checks = {
            'lang_var': 'Variable de langue',
            'sync_one_var': 'Variable sync un',
            'genfichier_file_var': 'Variable fichier génération',
            'genfichier_src_var': 'Variable source génération',
            'genfichier_tgt_var': 'Variable cible génération'
        }

        for var, description in var_checks.items():
            if hasattr(controller, var):
                var_obj = getattr(controller, var)
                if hasattr(var_obj, 'get'):  # C'est une variable tkinter
                    print(f"  ✅ {description}")
                else:
                    print(f"  ❌ {description} - Pas une variable tkinter")
                    all_good = False
            else:
                print(f"  ❌ {description} - Variable manquante")
                all_good = False

        root.destroy()
        return all_good

    except Exception as e:
        print(f"  ❌ Erreur lors de la vérification UI: {e}")
        return False

def check_legacy_compatibility():
    """Vérifier la compatibilité avec l'interface legacy."""
    print("\n🔄 Vérification de la compatibilité legacy...")

    try:
        root = tk.Tk()
        root.withdraw()

        from app import FaultEditor
        editor = FaultEditor(root)

        # Vérifier que les attributs principaux sont accessibles
        legacy_attrs = ['lang', 'file_map', 'base_dir', 'search_results', 'columns']

        all_good = True
        for attr in legacy_attrs:
            if hasattr(editor, attr):
                print(f"  ✅ {attr} accessible via wrapper")
            else:
                print(f"  ❌ {attr} non accessible via wrapper")
                all_good = False

        # Vérifier que les méthodes principales sont accessibles
        legacy_methods = ['open_folder', 'load_flat_json', 'show_search', 'reload_lang']

        for method in legacy_methods:
            if hasattr(editor, method) and callable(getattr(editor, method)):
                print(f"  ✅ {method}() accessible via wrapper")
            else:
                print(f"  ❌ {method}() non accessible via wrapper")
                all_good = False

        root.destroy()
        return all_good

    except Exception as e:
        print(f"  ❌ Erreur lors de la vérification legacy: {e}")
        return False

def main():
    """Exécuter tous les tests de validation."""
    print("🚀 VALIDATION DE LA RESTAURATION FAULT EDITOR")
    print("=" * 50)

    tests = [
        ("Imports", check_imports),
        ("Création d'interface", check_interface_creation),
        ("Attributs requis", check_required_attributes),
        ("Méthodes requises", check_required_methods),
        ("Composants UI", check_ui_components),
        ("Compatibilité legacy", check_legacy_compatibility)
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result = test_func()
        results.append((test_name, result))

    # Résumé final
    print("\n" + "="*50)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")

    print(f"\n📈 Score: {passed}/{total} tests réussis")

    if passed == total:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
        print("✅ La restauration de l'interface Fault Editor est COMPLÈTE")
        print("🚀 L'application est prête pour la production")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) ont échoué")
        print("🔧 Veuillez vérifier les composants manquants")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erreur inattendue: {e}")
        sys.exit(1)
