import os
from openai import OpenAI
from dotenv import load_dotenv

# Chargement direct du fichier .env
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

# Récupération de la clé API
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    print("⚠️ OPENAI_API_KEY non trouvée, utilisation d'une clé de test")
    OPENAI_API_KEY = "sk-test-key-for-development"

# Configuration du client OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

def traduire(text, target_lang):
    """
    Traduit un texte français vers la langue cible en utilisant l'API OpenAI

    Args:
        text (str): Le texte français à traduire
        target_lang (str): La langue cible ('en' pour anglais, 'es' pour espagnol)

    Returns:
        str: Le texte traduit
    """
    if not text or not text.strip():
        return text

    # Définir les langues complètes
    lang_map = {
        'en': 'anglais',
        'es': 'espagnol',
        'fr': 'français'
    }

    target_language = lang_map.get(target_lang, target_lang)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"Tu es un traducteur professionnel. Traduis uniquement le texte fourni du français vers le {target_language}. Ne donne que la traduction, sans explication ni commentaire."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            max_tokens=500,
            temperature=0.3
        )

        translated_text = response.choices[0].message.content.strip()
        return translated_text

    except Exception as e:
        print(f"Erreur lors de la traduction: {e}")
        return text  # Retourner le texte original en cas d'erreur
