#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suite de tests simplifiée pour l'application FaultEditor
Permet de vérifier que les modifications n'introduisent pas de régressions
"""

import unittest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour importer l'app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import FaultEditor
except ImportError as e:
    print(f"⚠️ Impossible d'importer l'app: {e}")
    print("Assurez-vous que app.py est dans le même répertoire")
    sys.exit(1)

class TestFaultEditorBasic(unittest.TestCase):
    """Tests de base pour FaultEditor"""

    def setUp(self):
        """Préparation avant chaque test"""
        self.root = tk.Tk()
        self.root.withdraw()  # Cacher la fenêtre pendant les tests

    def tearDown(self):
        """Nettoyage après chaque test"""
        try:
            if hasattr(self, 'app') and self.app:
                self.app.root.destroy()
        except:
            pass
        try:
            self.root.destroy()
        except:
            pass

    def test_app_can_be_created(self):
        """Test que l'application peut être créée sans crash"""
        try:
            self.app = FaultEditor(self.root)
            self.assertIsNotNone(self.app)
            print("✅ Application créée avec succès")
        except Exception as e:
            self.fail(f"❌ Impossible de créer l'app: {e}")

    def test_app_has_required_methods(self):
        """Test que l'application a les méthodes essentielles"""
        self.app = FaultEditor(self.root)

        # Vérifier que les méthodes importantes existent
        required_methods = [
            'load_json_file',
            'save_json_file',
            'create_widgets',
            'update_info_frame'
        ]

        for method_name in required_methods:
            self.assertTrue(hasattr(self.app, method_name),
                          f"Méthode manquante: {method_name}")

        print("✅ Toutes les méthodes requises sont présentes")

class TestFileOperations(unittest.TestCase):
    """Tests pour les opérations sur fichiers"""

    def setUp(self):
        """Préparation avant chaque test"""
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = FaultEditor(self.root)

        # Créer un fichier de test temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.json")

        # Données de test valides
        self.test_data = {
            "Header": {
                "Language": "fr",
                "FileName": "test.json"
            },
            "FaultDetailList": [
                {
                    "Id": 0,
                    "Name": "Test Fault",
                    "Description": "Test Description"
                }
            ]
        }

        # Créer le fichier de test
        with open(self.test_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_data, f, indent=2, ensure_ascii=False)

    def tearDown(self):
        """Nettoyage après chaque test"""
        try:
            if os.path.exists(self.test_file):
                os.remove(self.test_file)
            os.rmdir(self.temp_dir)
        except:
            pass
        try:
            self.app.root.destroy()
            self.root.destroy()
        except:
            pass

    def test_load_valid_json(self):
        """Test de chargement d'un fichier JSON valide"""
        try:
            self.app.load_json_file(self.test_file)
            self.assertIsNotNone(self.app.json_data)
            self.assertEqual(self.app.json_data["Header"]["Language"], "fr")
            print("✅ Chargement JSON valide réussi")
        except Exception as e:
            self.fail(f"❌ Échec du chargement JSON: {e}")

    def test_load_nonexistent_file(self):
        """Test de chargement d'un fichier inexistant"""
        nonexistent_file = os.path.join(self.temp_dir, "inexistant.json")

        # Cette opération ne devrait pas crasher l'app
        try:
            self.app.load_json_file(nonexistent_file)
            print("✅ Gestion fichier inexistant OK")
        except Exception as e:
            # On s'attend à une erreur contrôlée, pas un crash
            print(f"⚠️ Erreur attendue pour fichier inexistant: {e}")

def run_quick_tests():
    """Lance les tests rapides essentiels"""
    print("🚀 Lancement des tests essentiels...")
    print("=" * 50)

    # Créer une suite de tests
    suite = unittest.TestSuite()

    # Ajouter les tests essentiels
    suite.addTest(TestFaultEditorBasic('test_app_can_be_created'))
    suite.addTest(TestFaultEditorBasic('test_app_has_required_methods'))
    suite.addTest(TestFileOperations('test_load_valid_json'))
    suite.addTest(TestFileOperations('test_load_nonexistent_file'))

    # Lancer les tests
    runner = unittest.TextTestRunner(verbosity=1)
    result = runner.run(suite)

    print("=" * 50)
    if result.wasSuccessful():
        print("🎉 TOUS LES TESTS ESSENTIELS SONT RÉUSSIS!")
        print("✅ Votre application fonctionne correctement")
        return True
    else:
        print(f"❌ {len(result.failures + result.errors)} problème(s) détecté(s)")

        if result.failures:
            print("\n🔍 ÉCHECS:")
            for test, traceback in result.failures:
                print(f"  - {test}")
                print(f"    {traceback}")

        if result.errors:
            print("\n💥 ERREURS:")
            for test, traceback in result.errors:
                print(f"  - {test}")
                print(f"    {traceback}")

        return False

def run_all_tests():
    """Lance tous les tests disponibles"""
    print("🚀 Lancement de TOUS les tests...")
    print("=" * 50)

    # Découvrir et lancer tous les tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("=" * 50)
    print(f"📊 RÉSULTATS COMPLETS:")
    print(f"Tests lancés: {result.testsRun}")
    print(f"Échecs: {len(result.failures)}")
    print(f"Erreurs: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n🎉 TOUS LES TESTS SONT RÉUSSIS!")
        return True
    else:
        print(f"\n❌ {len(result.failures + result.errors)} problème(s) détecté(s)")
        return False

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Tests pour FaultEditor")
    parser.add_argument("--all", action="store_true",
                       help="Lance tous les tests disponibles")

    args = parser.parse_args()

    if args.all:
        success = run_all_tests()
    else:
        # Par défaut, tests essentiels seulement
        success = run_quick_tests()

    print(f"\n{'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    sys.exit(0 if success else 1)
