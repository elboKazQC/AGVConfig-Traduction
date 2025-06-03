#!/usr/bin/env python3
"""
Test script pour vérifier les améliorations de traduction
Teste la nouvelle approche 100% OpenAI avec prompt intelligent
"""
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from translate import traduire

def test_api_translation():
    """Test de traduction via l'API intelligente"""
    print("🧪 Test de traduction via l'API intelligente (100% OpenAI)")
    print("=" * 60)

    test_cases = [
        # Cas problématique original
        ("réinitialisation balayeur laser", "en", "reset laser scanner"),

        # Variations orthographiques et casse
        ("Réinitialisation balayeur laser", "en", "Reset laser scanner"),
        ("reinitialisation balayeur laser", "en", "reset laser scanner"),
        ("Renitialisation balayeur laser", "en", "Reset laser scanner"),  # Faute de frappe

        # Pluriels
        ("réinitialisation balayeurs lasers", "en", "reset laser scanners"),
        ("Renitialisation balayeurs lasers", "en", "Reset laser scanners"),  # Cas problématique mentionné

        # Avec positions
        ("réinitialisation balayeur gauche", "en", "left laser scanner reset"),
        ("défaut balayeur avant droit", "en", "right front laser scanner fault"),

        # Autres cas techniques
        ("défaut capteur avant", "en", "front sensor fault"),
        ("erreur communication moteur", "en", "motor communication error"),
        ("arrêt d'urgence activé", "en", "emergency stop activated"),

        # Cas simples
        ("balayeur", "en", "laser scanner"),
        ("réinitialisation", "en", "reset"),
        ("défaut", "en", "fault"),

        # Tests en espagnol
        ("réinitialisation balayeur laser", "es", "reinicio escáner láser"),
        ("défaut capteur avant", "es", "fallo sensor delantero"),
    ]

    success_count = 0
    total_count = len(test_cases)

    for text, target_lang, expected in test_cases:
        try:
            result = traduire(text, target_lang)

            # Normaliser les résultats pour la comparaison (ignorer la casse et espaces)
            result_normalized = result.lower().strip()
            expected_normalized = expected.lower().strip()

            if result_normalized == expected_normalized:
                print(f"✅ '{text}' → '{result}' (✓)")
                success_count += 1
            else:
                print(f"❌ '{text}' → '{result}' (attendu: '{expected}')")

        except Exception as e:
            print(f"🔥 ERREUR '{text}': {e}")

    print(f"\n📊 Résultats: {success_count}/{total_count} traductions correctes")
    print(f"📈 Taux de réussite: {(success_count/total_count)*100:.1f}%")

    return success_count >= (total_count * 0.8)  # 80% de réussite minimum

def test_edge_cases():
    """Test des cas limites et complexes"""
    print("\n🧪 Test des cas limites")
    print("=" * 40)

    edge_cases = [
        # Combinaisons complexes
        ("défaut réinitialisation balayeur avant gauche", "en"),
        ("erreur communication balayeurs arrière", "en"),
        ("arrêt urgence défaut capteur", "en"),

        # Très courts
        ("OK", "en"),
        ("NOK", "en"),

        # Codes techniques (ne devraient pas être traduits par est_code_technique)
        ("A1B2", "en"),
        ("ERR_001", "en"),
    ]

    for text, target_lang in edge_cases:
        try:
            result = traduire(text, target_lang)
            print(f"📝 '{text}' → '{result}'")
        except Exception as e:
            print(f"🔥 ERREUR '{text}': {e}")

def main():
    """Point d'entrée principal"""
    print("🚀 Test du système de traduction amélioré")
    print("=" * 60)
    print("Changements apportés:")
    print("   ✅ Suppression des traductions spéciales (dictionnaire)")
    print("   ✅ 100% des traductions passent par OpenAI")
    print("   ✅ Prompt intelligent capable de gérer tous les cas")
    print("   ✅ Gestion automatique des pluriels, fautes de frappe, positions")
    print("   ✅ Modèle gpt-4o-mini avec température 0.1")
    print()

    # Test principal
    api_ok = test_api_translation()

    # Test des cas limites
    test_edge_cases()

    print("\n" + "=" * 60)
    if api_ok:
        print("🎉 Tests réussis! Le système de traduction intelligent fonctionne.")
        print("   Toutes les traductions passent maintenant par OpenAI avec un prompt optimisé.")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez la configuration de l'API OpenAI.")

    print("\nPour tester avec de vrais fichiers:")
    print("   python sync_one.py path/to/file_fr.json --force")

if __name__ == "__main__":
    main()
