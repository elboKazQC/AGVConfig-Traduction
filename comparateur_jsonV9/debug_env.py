import os
from dotenv import load_dotenv

print("=== Diagnostic du fichier .env ===")
print("Répertoire courant:", os.getcwd())
print("Fichier script:", __file__)

# Test de différents chemins pour le fichier .env
chemins_test = [
    os.path.join(os.path.dirname(__file__), '..', '.env'),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'),
    os.path.join(os.getcwd(), '..', '.env'),
    r'c:\Users\vcasaubon.NOOVELIA\OneDrive - Noovelia\Documents\GitHub\AGVConfig-Traduction\.env'
]

for i, chemin in enumerate(chemins_test):
    chemin_abs = os.path.abspath(chemin)
    print(f"Chemin {i+1}: {chemin}")
    print(f"  -> Absolu: {chemin_abs}")
    print(f"  -> Existe: {os.path.exists(chemin_abs)}")

    if os.path.exists(chemin_abs):
        print("  -> Tentative de chargement...")
        result = load_dotenv(chemin_abs)
        print(f"  -> Chargement réussi: {result}")
        api_key = os.getenv('OPENAI_API_KEY')
        print(f"  -> OPENAI_API_KEY trouvée: {api_key is not None}")
        if api_key:
            print(f"  -> Début de la clé: {api_key[:20]}...")
        break
    print()
