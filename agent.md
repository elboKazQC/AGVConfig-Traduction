# Agent IA - FaultEditor Application

## 🤖 Description de l'Agent

Cet agent IA est spécialisé dans l'assistance et le support pour l'application **FaultEditor**, une interface graphique Python dédiée à la gestion et à la traduction des codes de défaut AGV (Véhicules Guidés Automatisés).

## 🎯 Domaines d'Expertise

### 1. Application FaultEditor
- **Interface utilisateur Tkinter** avec thème sombre professionnel
- **Navigation hiérarchique** des codes de défaut JSON
- **Édition en ligne** des descriptions de défaut
- **Système de traduction intégré** (Français ↔ Anglais ↔ Espagnol)
- **Fonctionnalités de recherche** avancées (hiérarchique et plate)

### 2. Gestion des Fichiers JSON
- **Structure hiérarchique** des codes de défaut AGV
- **Synchronisation multi-langue** (FR/EN/ES)
- **Validation de cohérence** entre fichiers
- **Génération automatique** de fichiers manquants

### 3. Traduction Automatisée
- **Intégration OpenAI GPT** pour traductions de qualité
- **Traduction par lot** avec barre de progression
- **Détection automatique** de langue (optionnel)
- **Gestion des erreurs** de traduction robuste

## 🛠️ Fonctionnalités Principales

### Interface Utilisateur
```python
# Thème sombre professionnel
COL_BG_MAIN = "#2a2a2a"
COL_BG_TOPBAR = "#1c1c1c"
COL_FG_TEXT = "#ffffff"
FONT_DEFAULT = ("Segoe UI", 11)
```

### Modes de Visualisation
- **Vue hiérarchique** : Navigation par colonnes avec arborescence
- **Vue plate** : Éditeur tabulaire pour traductions en masse
- **Recherche en temps réel** avec surlignage des résultats

### Fonctionnalités Clés
| Fonctionnalité | Description | Raccourci |
|----------------|-------------|-----------|
| Ouverture dossier | Chargement répertoire JSON | `📂 Bouton` |
| Changement langue | FR/EN/ES | `Radio buttons` |
| Recherche | Recherche temps réel | `Ctrl+F` |
| Édition | Modification en ligne | `Double-clic` |
| Traduction | Traduction automatique | `🌐 Bouton` |
| Sauvegarde | Enregistrement changes | `💾 Bouton` |

## 📁 Structure du Projet

```
AGVConfig-Traduction/
├── comparateur_jsonV9/
│   ├── app.py                 # Application principale
│   ├── translate.py           # Module de traduction
│   ├── sync_one.py           # Synchronisation fichiers
│   ├── check_coherence.py    # Vérification cohérence
│   └── requirements.txt      # Dépendances Python
├── JSON/                     # Fichiers de codes de défaut
│   ├── faults_*_fr.json     # Versions françaises
│   ├── faults_*_en.json     # Versions anglaises
│   └── faults_*_es.json     # Versions espagnoles
└── logs/                     # Fichiers de log
```

## 🔧 Configuration Requise

### Prérequis Techniques
- **Python 3.7+**
- **Tkinter** (inclus avec Python)
- **OpenAI API Key** (pour traductions)
- **Packages Python** : `openai`, `python-dotenv`, `langdetect`

### Variables d'Environnement
```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
TRANSLATION_TEMPERATURE=0.1
```

## 🚀 Utilisation

### Démarrage de l'Application
```bash
cd comparateur_jsonV9
python app.py
```

### Flux de Travail Typique
1. **Ouvrir un dossier** contenant les fichiers JSON
2. **Sélectionner la langue** de travail (FR/EN/ES)
3. **Navigator** dans la hiérarchie des codes
4. **Éditer** les descriptions (double-clic)
5. **Traduire** automatiquement si nécessaire
6. **Sauvegarder** les modifications

### Mode Éditeur Plat
- Cliquer sur "📄 Charger JSON plat"
- Voir toutes les traductions dans un tableau
- Utiliser "🌐 Traduire tout" pour traduire en masse
- Rechercher avec `Ctrl+F`

## 🎨 Interface Utilisateur

### Thème Visuel
- **Design sombre** professionnel
- **Logo Noovelia** en haut à gauche
- **Couleurs de statut** :
  - 🟢 Vert : Éléments extensibles
  - 🔴 Rouge : Alertes/erreurs
  - 🟡 Ambre : Avertissements
  - 🟠 Orange : Surlignage recherche

### Zones d'Interface
1. **Barre supérieure** : Logo, sélecteur langue, boutons
2. **Barre d'outils** : Fonctions spécialisées
3. **Zone principale** : Colonnes hiérarchiques ou tableau
4. **Barre de statut** : Messages et progression

## 🔍 Fonctionnalités de Recherche

### Recherche Hiérarchique
- Parcourt toutes les colonnes visibles
- Surligne les résultats en temps réel
- Navigation avec `◀` `▶`
- Compteur de résultats

### Recherche Plate
- Recherche dans clés et valeurs
- Défilement automatique vers résultats
- Surlignage contexte de ligne
- Recherche sensible à la casse

## 🌐 Système de Traduction

### Intégration OpenAI
```python
def translate_text(self, text, target_lang):
    """Traduit un texte français vers la langue cible"""
    try:
        translated = traduire(text, target_lang)
        return translated
    except Exception as e:
        print(f"Erreur traduction: {e}")
        return text
```

### Langues Supportées
- **Français (fr)** : Langue source principale
- **Anglais (en)** : Traduction primaire
- **Espagnol (es)** : Traduction secondaire

### Fonctionnalités Avancées
- **Traduction par lot** avec barre de progression
- **Gestion d'erreurs** robuste
- **Confirmation utilisateur** pour actions en masse
- **Effets visuels** pendant traduction

## 🛡️ Gestion d'Erreurs

### Types d'Erreurs Gérées
- Fichiers JSON corrompus
- Erreurs de traduction API
- Problèmes de connectivité
- Widgets Tkinter détruits

### Logging
```python
# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app_debug.log'),
        logging.StreamHandler()
    ]
)
```

## 🧪 Tests et Validation

### Environnement de Test
- **Display requis** : Tkinter nécessite un affichage graphique
- **CI/CD** : Configuration spéciale nécessaire pour tests automatisés
- **Tests sans UI** : Utiliser `validate_improvements.py`

### Tests Disponibles
```bash
# Validation sans interface graphique
python validate_improvements.py  # ✅ Fonctionne toujours

# Tests unitaires complets (nécessite affichage)
pytest -q  # ❌ Échoue si pas d'affichage (TclError)
```

### Gestion des Erreurs Spécifiques
- **TranslationError** : Erreurs de traduction
- **TclError** : Erreurs liées à l'interface Tkinter
- **FileError** : Problèmes d'accès aux fichiers
- **SubprocessError** : Erreurs d'exécution de commandes

### Bonnes Pratiques de Test
1. **Configuration d'environnement**
   - Configurer DISPLAY si nécessaire
   - Installer toutes les dépendances
   - Vérifier les permissions fichiers

2. **Validation sans UI**
   - Utiliser les scripts de validation
   - Tester la logique métier séparément
   - Vérifier les logs d'erreur

3. **Tests avec UI**
   - Exécuter sur machine avec affichage
   - Tester toutes les interactions utilisateur
   - Valider le comportement visuel

## 📝 Bonnes Pratiques

### Pour les Développeurs
1. **Tests réguliers** des fonctionnalités de traduction
2. **Sauvegarde** avant modifications importantes
3. **Vérification cohérence** après changements
4. **Respect des conventions** de nommage JSON

### Pour les Utilisateurs
1. **Sauvegarde fréquente** des modifications
2. **Test traductions** avant validation
3. **Vérification orthographe** des textes
4. **Utilisation recherche** pour navigation rapide

## 🔄 Maintenance et Support

### Fichiers de Log
- `logs/app_debug.log` : Log détaillé application
- `logs/app_complete.log` : Log complet opérations

### Outils de Diagnostic
- `check_coherence.py` : Vérification cohérence
- `validate_app.py` : Validation application
- `test_*.py` : Tests unitaires

### Scripts Utilitaires
- `sync_one.py` : Synchronisation fichier unique
- `sync_all.py` : Synchronisation complète
- `generer_manquant.py` : Génération fichiers manquants

## 🎯 Cas d'Usage Typiques

### 1. Ajout Nouveau Code de Défaut
1. Ouvrir fichier français de référence
2. Naviguer vers la section appropriée
3. Double-cliquer pour éditer
4. Ajouter description et définir "IsExpandable"
5. Utiliser traduction automatique
6. Vérifier et ajuster traductions
7. Sauvegarder

### 2. Correction Traduction Existante
1. Utiliser recherche (`Ctrl+F`)
2. Trouver terme à corriger
3. Éditer directement
4. Ou utiliser mode plat pour vue d'ensemble
5. Sauvegarder modifications

### 3. Traduction en Masse
1. Charger éditeur plat
2. Utiliser "🌐 Traduire tout"
3. Confirmer l'opération
4. Surveiller barre de progression
5. Vérifier résultats
6. Sauvegarder

## 🚨 Points d'Attention

### Limitations Connues
- **Dépendance internet** pour traductions
- **Limites API OpenAI** (quotas, coûts)
- **Performance** avec gros fichiers JSON
- **Encodage** potentiel selon système

### Précautions
- ⚠️ Toujours **sauvegarder** avant modifications importantes
- ⚠️ **Tester traductions** avant validation définitive
- ⚠️ **Vérifier cohérence** entre versions linguistiques
- ⚠️ **Surveiller quotas** API OpenAI

## 📞 Support et Contact

Pour toute assistance technique ou question sur l'application FaultEditor :

- **Documentation** : Ce fichier et commentaires dans le code
- **Logs** : Consulter `logs/app_debug.log` pour diagnostics
- **Tests** : Utiliser scripts de validation fournis
- **Issues** : Reporter problèmes avec logs et contexte

---

*Cet agent est optimisé pour assister avec l'application FaultEditor et son écosystème de traduction de codes de défaut AGV.*
