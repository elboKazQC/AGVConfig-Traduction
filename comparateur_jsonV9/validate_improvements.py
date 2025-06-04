#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de validation post-amélioration
Permet de vérifier que les améliorations d'error handling fonctionnent correctement
"""

import os
import sys
import json
import tempfile
import traceback
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def validate_imports():
    """Valide que tous les nouveaux modules peuvent être importés"""
    print("📋 Validation des imports...")

    try:
        from exceptions import FaultEditorError, ErrorCodes
        print("✅ exceptions.py importé")
    except ImportError as e:
        print(f"❌ Erreur import exceptions.py: {e}")
        return False

    try:
        from error_utils import safe_execute, show_error_to_user
        print("✅ error_utils.py importé")
    except ImportError as e:
        print(f"❌ Erreur import error_utils.py: {e}")
        return False

    return True

def validate_app_import():
    """Valide que l'application modifiée peut être importée"""
    print("\n📋 Validation de l'application modifiée...")

    try:
        import app
        print("✅ app.py importé")

        if hasattr(app, 'FaultEditor'):
            print("✅ Classe FaultEditor trouvée")
        else:
            print("❌ Classe FaultEditor non trouvée")
            return False

        return True
    except Exception as e:
        print(f"❌ Erreur import app.py: {e}")  # handled for visibility
        traceback.print_exc()
        return False

def test_error_handling():
    """Test basique de la gestion d'erreurs"""
    print("\n📋 Test de la gestion d'erreurs...")

    try:
        from exceptions import FileOperationError, ErrorCodes
        from error_utils import safe_execute

        # Test d'une exception personnalisée
        try:
            raise FileOperationError(
                "Test d'erreur",
                filepath="test.json",
                error_code=ErrorCodes.FILE_NOT_FOUND
            )
        except FileOperationError as e:
            print(f"✅ Exception personnalisée fonctionne: {e}")

        # Test du décorateur safe_execute
        @safe_execute("Test d'opération", show_user_error=False, default_return="ERREUR")
        def operation_qui_echoue():
            raise Exception("Test d'échec")

        result = operation_qui_echoue()
        if result == "ERREUR":
            print("✅ Décorateur safe_execute fonctionne")
        else:
            print("❌ Décorateur safe_execute ne fonctionne pas")
            return False

        return True

    except Exception as e:
        print(f"❌ Erreur test gestion d'erreurs: {e}")  # handled for visibility
        traceback.print_exc()
        return False

def main():
    """Fonction principale de validation"""
    print("🔍 VALIDATION DES AMÉLIORATIONS D'ERROR HANDLING")
    print("=" * 55)

    tests = {
        "Imports des nouveaux modules": validate_imports,
        "Import de l'application modifiée": validate_app_import,
        "Gestion d'erreurs personnalisées": test_error_handling,
    }

    results = {}

    for test_name, test_func in tests.items():
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Erreur inattendue dans {test_name}: {e}")  # handled for visibility
            traceback.print_exc()
            results[test_name] = False

    print("\n" + "=" * 55)
    print("📊 RÉSULTATS FINAUX:")

    passed = sum(results.values())
    total = len(results)

    for test_name, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")

        print(f"\n📈 Score: {passed}/{total} ({(passed/total)*100:.1f}%)")

    if passed == total:
        print("\n🎉 TOUTES LES VALIDATIONS SONT RÉUSSIES !")
        print("✅ Vos améliorations d'error handling sont fonctionnelles")
    else:
        print(f"\n⚠️ {total-passed} test(s) ont échoué")
        print("💡 Consultez les erreurs pour les détails")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
