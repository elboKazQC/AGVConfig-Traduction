#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test ultra-simple pour diagnostiquer les problèmes
"""

import sys
import os

print("🔍 Diagnostic de l'environnement de test")
print(f"Python version: {sys.version}")
print(f"Répertoire de travail: {os.getcwd()}")

# Test 1: Import de base
print("\n📋 Test 1: Imports de base")
try:
    import tkinter as tk
    print("✅ tkinter importé")
except Exception as e:
    print(f"❌ tkinter: {e}")

try:
    import json
    print("✅ json importé")
except Exception as e:
    print(f"❌ json: {e}")

# Test 2: Vérification du fichier app.py
print("\n📋 Test 2: Vérification du fichier app.py")
app_file = "app.py"
if os.path.exists(app_file):
    print(f"✅ {app_file} trouvé")
    try:
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✅ {app_file} lu ({len(content)} caractères)")

        # Vérifier si FaultEditor est défini
        if "class FaultEditor" in content:
            print("✅ Classe FaultEditor trouvée")
        else:
            print("❌ Classe FaultEditor NON trouvée")

    except Exception as e:
        print(f"❌ Erreur lecture {app_file}: {e}")
else:
    print(f"❌ {app_file} NON trouvé")

# Test 3: Import sécurisé
print("\n📋 Test 3: Import de app.py")
try:
    # Ajouter le répertoire au path si nécessaire
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    # Import avec gestion d'erreur détaillée
    import app
    print("✅ app.py importé avec succès")

    # Vérifier si FaultEditor existe
    if hasattr(app, 'FaultEditor'):
        print("✅ Classe FaultEditor accessible")
    else:
        print("❌ Classe FaultEditor NON accessible")
        print(f"Attributs disponibles: {[attr for attr in dir(app) if not attr.startswith('_')]}")

except ImportError as e:
    print(f"❌ ImportError: {e}")
except Exception as e:
    print(f"❌ Autre erreur: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Création d'un objet JSON simple
print("\n📋 Test 4: Manipulation JSON")
try:
    test_data = {
        "Header": {"Language": "fr"},
        "FaultDetailList": []
    }
    json_str = json.dumps(test_data, indent=2)
    print("✅ Sérialisation JSON réussie")

    parsed = json.loads(json_str)
    print("✅ Désérialisation JSON réussie")

except Exception as e:
    print(f"❌ JSON: {e}")

print("\n🏁 Diagnostic terminé")
