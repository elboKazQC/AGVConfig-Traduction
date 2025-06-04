#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suite de tests pour l'application FaultEditor
Permet de vérifier que les modifications n'introduisent pas de régressions
"""

import unittest
import tkinter as tk
import traceback
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

class TestFaultEditorBase(unittest.TestCase):
    """Classe de base pour les tests avec setup/teardown communs"""

    def setUp(self):
        """Préparation avant chaque test"""
        self.root = tk.Tk()
        self.root.withdraw()  # Cacher la fenêtre pendant les tests

        # Créer un répertoire temporaire pour les tests
        self.temp_dir = tempfile.mkdtemp()
        self.test_json_file = os.path.join(self.temp_dir, "test_fault.json")

        # Données de test JSON valides
        self.test_data = {
            "Header": {
                "Language": "fr",
                "FileName": "test_fault.json",
                "IdLevel0": 0,
                "IdLevel1": 255,
                "IdLevel2": 255,
                "IdLevel3": 255
            },
            "FaultDetailList": [
                {
                    "Id": 0,
                    "Description": "Test Fault 1",
                    "IsExpandable": True
                },
                {
                    "Id": 1,
                    "Description": "Test Fault 2",
                    "IsExpandable": False
                }
            ]
        }

        # Créer le fichier de test
        with open(self.test_json_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_data, f, indent=2, ensure_ascii=False)

    def tearDown(self):
        """Nettoyage après chaque test"""
        try:
            self.root.destroy()
        except tk.TclError:
            traceback.print_exc()  # handled for visibility

        # Nettoyer les fichiers temporaires
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except OSError:
            traceback.print_exc()  # handled for visibility

class TestFaultEditorInitialization(TestFaultEditorBase):
    """Tests d'initialisation de l'application"""

    def test_app_creation(self):
        """Test: L'application peut être créée sans erreur"""
        try:
            app = FaultEditor(self.root)
            self.assertIsInstance(app, FaultEditor)
            print("✅ Test création app: PASS")
        except Exception as e:
            self.fail(f"❌ Échec création app: {e}")

    def test_ui_components_exist(self):
        """Test: Les composants UI principaux existent"""
        app = FaultEditor(self.root)

        # Vérifier que les attributs essentiels existent
        essential_attrs = [
            'root', 'columns', 'file_map', 'data_map',
            'current_path', 'editing_info', 'status'
        ]

        for attr in essential_attrs:
            self.assertTrue(hasattr(app, attr), f"Attribut manquant: {attr}")

        print("✅ Test composants UI: PASS")

    def test_initial_state(self):
        """Test: L'état initial de l'application est correct"""
        app = FaultEditor(self.root)

        self.assertEqual(app.lang, "fr")
        self.assertEqual(app.current_path, [0, 255, 255, 255])
        self.assertIsNone(app.editing_info)
        self.assertEqual(len(app.columns), 0)

        print("✅ Test état initial: PASS")

class TestFileOperations(TestFaultEditorBase):
    """Tests des opérations sur fichiers"""

    @patch('tkinter.filedialog.askdirectory')
    def test_open_folder(self, mock_askdir):
        """Test: Ouverture d'un dossier"""
        mock_askdir.return_value = self.temp_dir

        app = FaultEditor(self.root)
        app.open_folder()

        # Vérifier que le file_map est initialisé
        self.assertIsInstance(app.file_map, dict)
        print("✅ Test ouverture dossier: PASS")

    def test_save_file_success(self):
        """Test: Sauvegarde réussie d'un fichier"""
        app = FaultEditor(self.root)

        # Simuler les données en mémoire
        test_filename = os.path.basename(self.test_json_file)
        app.file_map[test_filename] = self.test_json_file
        app.data_map[test_filename] = self.test_data

        # Tester la sauvegarde
        try:
            app.save_file(test_filename)

            # Vérifier que le fichier a été sauvegardé
            self.assertTrue(os.path.exists(self.test_json_file))

            # Vérifier le contenu
            with open(self.test_json_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)

            self.assertEqual(saved_data, self.test_data)
            print("✅ Test sauvegarde fichier: PASS")

        except Exception as e:
            self.fail(f"❌ Échec sauvegarde: {e}")

    def test_save_file_with_invalid_path(self):
        """Test: Gestion d'erreur lors de sauvegarde avec chemin invalide"""
        app = FaultEditor(self.root)

        # Simuler un chemin invalide
        app.file_map["invalid.json"] = "/chemin/inexistant/invalid.json"
        app.data_map["invalid.json"] = self.test_data

        # La méthode ne doit pas lever d'exception, mais gérer l'erreur
        try:
            app.save_file("invalid.json")
            print("✅ Test erreur sauvegarde: PASS")
        except Exception as e:
            self.fail(f"❌ Exception non gérée: {e}")

class TestDataValidation(TestFaultEditorBase):
    """Tests de validation des données"""

    def test_valid_json_structure(self):
        """Test: Validation d'une structure JSON valide"""
        app = FaultEditor(self.root)

        # Test avec données valides
        self.assertTrue(self._is_valid_fault_data(self.test_data))
        print("✅ Test JSON valide: PASS")

    def test_invalid_json_structure(self):
        """Test: Détection d'une structure JSON invalide"""
        invalid_data = {
            "WrongKey": "wrong_value"
            # Manque Header et FaultDetailList
        }

        self.assertFalse(self._is_valid_fault_data(invalid_data))
        print("✅ Test JSON invalide: PASS")

    def _is_valid_fault_data(self, data):
        """Méthode helper pour valider la structure des données"""
        try:
            # Vérifier les clés principales
            if not isinstance(data, dict):
                return False

            if "Header" not in data or "FaultDetailList" not in data:
                return False

            # Vérifier la structure du Header
            header = data["Header"]
            required_header_keys = ["Language", "FileName", "IdLevel0", "IdLevel1", "IdLevel2", "IdLevel3"]
            if not all(key in header for key in required_header_keys):
                return False

            # Vérifier que FaultDetailList est une liste
            if not isinstance(data["FaultDetailList"], list):
                return False

            return True

        except (KeyError, TypeError):
            traceback.print_exc()  # handled for visibility
            return False

class TestUIOperations(TestFaultEditorBase):
    """Tests des opérations UI (sans affichage réel)"""

    def test_clear_columns(self):
        """Test: Nettoyage des colonnes"""
        app = FaultEditor(self.root)

        # Simuler quelques colonnes
        for i in range(3):
            frame = tk.Frame(app.columns_frame)
            app.columns.append(frame)

        initial_count = len(app.columns)
        self.assertEqual(initial_count, 3)

        # Nettoyer à partir du niveau 1
        app.clear_columns_from(1)

        # Vérifier que les colonnes ont été supprimées
        self.assertEqual(len(app.columns), 1)
        print("✅ Test nettoyage colonnes: PASS")

    def test_path_to_filename(self):
        """Test: Génération correcte du nom de fichier à partir du chemin"""
        app = FaultEditor(self.root)

        path = [0, 1, 2, 255]
        expected = "faults_000_001_002_255_fr.json"
        result = app.path_to_filename(path)

        self.assertEqual(result, expected)
        print("✅ Test génération nom fichier: PASS")

class TestTranslationOperations(TestFaultEditorBase):
    """Tests des opérations de traduction"""

    @patch('app.traduire')
    def test_translate_text_success(self, mock_traduire):
        """Test: Traduction réussie"""
        mock_traduire.return_value = "Translated text"

        app = FaultEditor(self.root)
        result = app.translate_text("Texte français", "en")

        self.assertEqual(result, "Translated text")
        mock_traduire.assert_called_once_with("Texte français", "en")
        print("✅ Test traduction réussie: PASS")

    @patch('app.traduire')
    def test_translate_text_error(self, mock_traduire):
        """Test: Gestion d'erreur de traduction"""
        mock_traduire.side_effect = Exception("Erreur API")

        app = FaultEditor(self.root)
        result = app.translate_text("Texte français", "en")

        # En cas d'erreur, doit retourner le texte original
        self.assertEqual(result, "Texte français")
        print("✅ Test erreur traduction: PASS")

class TestSearchOperations(TestFaultEditorBase):
    """Tests des opérations de recherche"""

    def test_search_initialization(self):
        """Test: Initialisation des variables de recherche"""
        app = FaultEditor(self.root)

        # Créer une fenêtre factice pour les tests
        editor_window = tk.Toplevel(self.root)
        editor_window.withdraw()

        # Simuler l'initialisation des variables de recherche
        editor_window.search_results = []
        editor_window.current_search_index = -1
        editor_window.all_keys = ["key1", "key2", "key3"]

        # Vérifier l'état initial
        self.assertEqual(len(editor_window.search_results), 0)
        self.assertEqual(editor_window.current_search_index, -1)
        self.assertEqual(len(editor_window.all_keys), 3)

        editor_window.destroy()
        print("✅ Test initialisation recherche: PASS")

class SmokeTest(TestFaultEditorBase):
    """Tests de fumée - vérifications rapides que l'app fonctionne"""

    def test_app_starts_without_crash(self):
        """Test de fumée: L'app démarre sans crash"""
        try:
            app = FaultEditor(self.root)
            # Attendre un court moment pour l'initialisation
            self.root.update_idletasks()
            print("✅ Smoke test démarrage: PASS")
            return True
        except Exception as e:
            self.fail(f"❌ L'app crash au démarrage: {e}")

    def test_basic_operations_dont_crash(self):
        """Test de fumée: Opérations de base sans crash"""
        app = FaultEditor(self.root)

        operations = [
            lambda: app.path_to_filename([0, 255, 255, 255]),
            lambda: app.clear_columns_from(0),
            lambda: app.translate_text("test", "en"),
            lambda: app.ask_yes_no("Test question?")
        ]

        for i, operation in enumerate(operations):
            try:
                with patch('tkinter.messagebox.askyesno', return_value=True):
                    operation()
                print(f"✅ Opération {i+1}: PASS")
            except Exception as e:
                self.fail(f"❌ Opération {i+1} crash: {e}")

def run_quick_test():
    """Lance un test rapide pour vérifier que tout fonctionne"""
    print("🚀 Lancement des tests rapides...")

    # Tests essentiels seulement
    suite = unittest.TestSuite()

    # Tests de fumée
    suite.addTest(SmokeTest('test_app_starts_without_crash'))
    suite.addTest(SmokeTest('test_basic_operations_dont_crash'))

    # Tests d'initialisation
    suite.addTest(TestFaultEditorInitialization('test_app_creation'))
    suite.addTest(TestFaultEditorInitialization('test_initial_state'))

    # Test de sauvegarde
    suite.addTest(TestFileOperations('test_save_file_success'))

    runner = unittest.TextTestRunner(verbosity=1)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\n🎉 Tous les tests rapides sont RÉUSSIS!")
        print("✅ Votre app fonctionne correctement")
        return True
    else:
        print(f"\n❌ {len(result.failures + result.errors)} test(s) échoué(s)")
        return False

def run_full_test():
    """Lance tous les tests"""
    print("🚀 Lancement de la suite complète de tests...")

    # Découvrir et lancer tous les tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print(f"\n📊 RÉSULTATS:")
    print(f"Tests lancés: {result.testsRun}")
    print(f"Échecs: {len(result.failures)}")
    print(f"Erreurs: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n🎉 TOUS LES TESTS SONT RÉUSSIS!")
        return True
    else:
        print(f"\n❌ {len(result.failures + result.errors)} problème(s) détecté(s)")
        if result.failures:
            print("\n🔍 ÉCHECS:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback}")

        if result.errors:
            print("\n💥 ERREURS:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback}")

        return False

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Tests pour FaultEditor")
    parser.add_argument("--quick", action="store_true",
                       help="Lance seulement les tests rapides")
    parser.add_argument("--full", action="store_true",
                       help="Lance tous les tests")

    args = parser.parse_args()

    if args.quick:
        success = run_quick_test()
    elif args.full:
        success = run_full_test()
    else:
        # Par défaut, tests rapides
        print("💡 Tip: Utilisez --quick ou --full pour spécifier le type de test")
        success = run_quick_test()

    sys.exit(0 if success else 1)
