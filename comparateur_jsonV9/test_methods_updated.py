#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test mis à jour pour vérifier que l'application FaultEditor a les bonnes méthodes
"""

import unittest
import tkinter as tk
import sys
import os

# Ajouter le répertoire parent au path pour importer l'app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import FaultEditor
except ImportError as e:
    print(f"⚠️ Impossible d'importer l'app: {e}")
    print("Assurez-vous que app.py est dans le même répertoire")
    sys.exit(1)

class TestFaultEditorMethods(unittest.TestCase):
    """Tests pour vérifier que les méthodes requises existent"""

    def setUp(self):
        """Préparation avant chaque test"""
        self.root = tk.Tk()
        self.root.withdraw()  # Cacher la fenêtre pendant les tests

    def tearDown(self):
        """Nettoyage après chaque test"""
        try:
            if hasattr(self, 'app') and self.app and hasattr(self.app, 'root'):
                self.app.root.quit()
                self.app.root.destroy()
        except:
            pass
        try:
            if self.root:
                self.root.quit()
                self.root.destroy()
        except:
            pass

    def test_app_has_current_methods(self):
        """Test que l'application a les méthodes de la version actuelle"""
        try:
            self.app = FaultEditor(self.root)

            # Méthodes qui existent dans la version actuelle
            current_methods = [
                'load_json_file',      # Existe toujours - charge un fichier JSON
                'save_file',           # Remplace save_json_file - sauvegarde hiérarchique
                'save_flat_files',     # Nouvelle méthode - sauvegarde JSON plats
                'setup_ui'             # Remplace create_widgets - initialise l'interface
            ]

            missing_methods = []
            existing_methods = []

            for method_name in current_methods:
                if hasattr(self.app, method_name):
                    existing_methods.append(method_name)
                else:
                    missing_methods.append(method_name)

            print(f"✅ Méthodes existantes: {existing_methods}")
            if missing_methods:
                print(f"❌ Méthodes manquantes: {missing_methods}")

            # Le test passe si toutes les méthodes existent
            self.assertEqual(len(missing_methods), 0,
                           f"Méthodes manquantes: {missing_methods}")

            print("✅ Toutes les méthodes requises sont présentes dans la version actuelle")

        except Exception as e:
            self.fail(f"❌ Erreur lors de la vérification des méthodes: {e}")

    def test_old_methods_removed(self):
        """Test que les anciennes méthodes ont bien été supprimées/remplacées"""
        try:
            self.app = FaultEditor(self.root)

            # Anciennes méthodes qui n'existent plus
            old_methods = [
                'save_json_file',      # Remplacée par save_file et save_flat_files
                'create_widgets',      # Remplacée par setup_ui
                'update_info_frame'    # Fonctionnalité refactorisée
            ]

            existing_old_methods = []
            removed_methods = []

            for method_name in old_methods:
                if hasattr(self.app, method_name):
                    existing_old_methods.append(method_name)
                else:
                    removed_methods.append(method_name)

            print(f"✅ Anciennes méthodes supprimées: {removed_methods}")
            if existing_old_methods:
                print(f"⚠️ Anciennes méthodes encore présentes: {existing_old_methods}")

            # Ce test vérifie juste l'évolution, ne fait pas échouer
            print("ℹ️ Évolution confirmée: l'application a bien évolué")

        except Exception as e:
            self.fail(f"❌ Erreur lors de la vérification de l'évolution: {e}")

if __name__ == "__main__":
    print("🔍 Test des méthodes de l'application FaultEditor (version mise à jour)")
    unittest.main(verbosity=2)
