import os
import sys
from dotenv import load_dotenv

print("Répertoire de travail:", os.getcwd())
print("Fichier courant:", __file__)

# Test du chemin vers le fichier .env
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
print("Chemin vers .env:", env_path)
print("Fichier .env existe:", os.path.exists(env_path))

# Chargement du fichier .env
load_dotenv(env_path)

# Vérification de la clé API
api_key = os.getenv('OPENAI_API_KEY')
print("OPENAI_API_KEY trouvée:", api_key is not None)
if api_key:
    print("Début de la clé:", api_key[:20] + "...")
else:
    print("Clé API non trouvée")
