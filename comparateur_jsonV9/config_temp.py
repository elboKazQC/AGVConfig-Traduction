import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
print(f"Chargement du fichier .env depuis: {os.path.abspath(env_path)}")
result = load_dotenv(env_path)
print(f"Résultat du chargement: {result}")

# Récupérer la clé API depuis les variables d'environnement
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
print(f"OPENAI_API_KEY trouvée: {OPENAI_API_KEY is not None}")

if not OPENAI_API_KEY:
    print("⚠️ OPENAI_API_KEY non trouvée, utilisation d'une clé de test")
    OPENAI_API_KEY = "sk-test-key-for-development"
else:
    print(f"✅ OPENAI_API_KEY chargée: {OPENAI_API_KEY[:20]}...")

print(f"OPENAI_API_KEY finale: {OPENAI_API_KEY[:20]}...")
