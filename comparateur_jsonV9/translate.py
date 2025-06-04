import os
from openai import OpenAI
from dotenv import load_dotenv

# Chargement direct du fichier .env
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

# Récupération de la clé API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("⚠️ OPENAI_API_KEY non trouvée, utilisation d'une clé de test")
    OPENAI_API_KEY = "sk-test-key-for-development"

# Sélection du modèle et de la température
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
TRANSLATION_TEMPERATURE = float(os.getenv("TRANSLATION_TEMPERATURE", "0.1"))

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
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": f"""Tu es un traducteur expert spécialisé dans les systèmes industriels et véhicules guidés automatiquement (AGV). Tu dois traduire avec une précision technique absolue.

CONTEXTE : Codes de défauts et messages d'erreur pour AGV industriels.

INTELLIGENCE ADAPTATIVE : Analyse chaque texte et applique automatiquement les meilleures règles :

1. GESTION DES VARIANTES ORTHOGRAPHIQUES :
   - "réinitialisation" / "reinitialisation" / "Renitialisation" → toutes équivalentes
   - Corrige automatiquement les fautes de frappe courantes
   - Gère les variations de casse (majuscules/minuscules)

2. GESTION DES PLURIELS ET SINGULIERS :
   - "balayeur" / "balayeurs" → "laser scanner" / "laser scanners"
   - "capteur" / "capteurs" → "sensor" / "sensors"
   - Adapte automatiquement le nombre

3. TERMINOLOGIE TECHNIQUE PRÉCISE :
   - "balayeur" → "laser scanner" (jamais juste "scanner")
   - "réinitialisation" → "reset"
   - "défaut" → "fault"
   - "erreur" → "error"
   - "capteur" → "sensor"
   - "moteur" → "motor"
   - "batterie" → "battery"

4. GESTION DES POSITIONS :
   - "gauche/droit/avant/arrière" → place correctement selon la langue
   - Anglais : position + objet ("left laser scanner")
   - Espagnol : objet + position ("escáner láser izquierdo")

5. GESTION DES COMBINAISONS COMPLEXES :
   - "réinitialisation balayeur laser" → "reset laser scanner"
   - "défaut capteur avant gauche" → "left front sensor fault"
   - Analyse le contexte complet pour une traduction cohérente

6. PRÉSERVATION DE LA CASSE :
   - Respecte la majuscule initiale du texte source
   - Maintient le style de formatage

EXEMPLES AVANCÉS :
- "Renitialisation balayeurs lasers" → "Reset laser scanners"
- "défaut capteur avant droit" → "right front sensor fault"
- "erreur communication moteur gauche" → "left motor communication error"
- "arrêt d'urgence activé" → "emergency stop activated"

INSTRUCTIONS :
- Analyse intelligemment chaque texte
- Applique les règles contextuellement
- Produis une traduction technique parfaite
- Ne donne QUE la traduction finale, sans explication

Langue cible : {target_language}"""
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            max_tokens=500,
            temperature=TRANSLATION_TEMPERATURE
        )

        content = response.choices[0].message.content
        translated_text = content.strip() if content else ""
        return translated_text

    except Exception as e:
        print(f"Erreur lors de la traduction: {e}")
        return text  # Retourner le texte original en cas d'erreur
