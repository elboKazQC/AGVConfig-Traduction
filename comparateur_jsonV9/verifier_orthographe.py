#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour vérifier et corriger l'orthographe dans les fichiers JSON français.
"""

import os
import json
import re
import argparse
from typing import Dict, List, Tuple

# Dictionnaire des corrections orthographiques courantes
CORRECTIONS_ORTHOGRAPHE = {
    # Fautes d'accents
    "arret": "arrêt",
    "Arret": "Arrêt",
    "ARRET": "ARRÊT",
    "arrets": "arrêts",
    "Arrets": "Arrêts",
    "ARRETS": "ARRÊTS",

    # Fautes de grammaire et conjugaison
    "reconnue": "reconnu",  # pour "Mouvement AMR non reconnue" -> "reconnu"
    "enonce": "énoncé",
    "Enonce": "Énoncé",
    "detecte": "détecté",
    "Detecte": "Détecté",
    "detectee": "détectée",
    "Detectee": "Détectée",
    "connecte": "connecté",
    "Connecte": "Connecté",
    "connectee": "connectée",
    "Connectee": "Connectée",

    # Fautes d'apostrophes
    "d'urgence": "d'urgence",  # Vérification apostrophe typographique
    "l'urgence": "l'urgence",
    "s'arrete": "s'arrête",
    "n'est": "n'est",
    "n'a": "n'a",
    "n'ont": "n'ont",

    # Fautes courantes techniques
    "contacteur": "contacteur",  # Déjà correct
    "aux.": "aux.",  # Abréviation correcte
    "desynchronisation": "désynchronisation",
    "Desynchronisation": "Désynchronisation",
    "synchronisation": "synchronisation",
    "Synchronisation": "Synchronisation",

    # Autres corrections courantes
    "defaut": "défaut",
    "Defaut": "Défaut",
    "defauts": "défauts",
    "Defauts": "Défauts",
    "echec": "échec",
    "Echec": "Échec",
    "echoue": "échoué",
    "Echoue": "Échoué",
    "donnee": "donnée",
    "Donnee": "Donnée",
    "donnees": "données",
    "Donnees": "Données",
    "indisponible": "indisponible",
    "Indisponible": "Indisponible",
    "verifier": "vérifier",
    "Verifier": "Vérifier",
    "verification": "vérification",
    "Verification": "Vérification",
    "capteur": "capteur",
    "Capteur": "Capteur",
    "capteurs": "capteurs",
    "Capteurs": "Capteurs",
    "detecteur": "détecteur",
    "Detecteur": "Détecteur",
    "detecteurs": "détecteurs",
    "Detecteurs": "Détecteurs",
    "peripherique": "périphérique",
    "Peripherique": "Périphérique",
    "peripheriques": "périphériques",
    "Peripheriques": "Périphériques",
    "cable": "câble",
    "Cable": "Câble",
    "cables": "câbles",
    "Cables": "Câbles",
    "controle": "contrôle",
    "Controle": "Contrôle",
    "controles": "contrôles",
    "Controles": "Contrôles",
    "probleme": "problème",
    "Probleme": "Problème",
    "problemes": "problèmes",
    "Problemes": "Problèmes",
    "systeme": "système",
    "Systeme": "Système",
    "systemes": "systèmes",
    "Systemes": "Systèmes",
    "memoire": "mémoire",
    "Memoire": "Mémoire",
    "memoires": "mémoires",
    "Memoires": "Mémoires",
    "parametre": "paramètre",
    "Parametre": "Paramètre",
    "parametres": "paramètres",
    "Parametres": "Paramètres",
    "temperature": "température",
    "Temperature": "Température",
    "temperatures": "températures",
    "Temperatures": "Températures",
    "batterie": "batterie",
    "Batterie": "Batterie",
    "batteries": "batteries",
    "Batteries": "Batteries",
    "camera": "caméra",
    "Camera": "Caméra",
    "cameras": "caméras",
    "Cameras": "Caméras",
    "numero": "numéro",
    "Numero": "Numéro",
    "numeros": "numéros",
    "Numeros": "Numéros",
    "reponse": "réponse",
    "Reponse": "Réponse",
    "reponses": "réponses",
    "Reponses": "Réponses",
    "requete": "requête",
    "Requete": "Requête",
    "requetes": "requêtes",
    "Requetes": "Requêtes",
    "cree": "créé",
    "Cree": "Créé",
    "creee": "créée",
    "Creee": "Créée",
    "supprime": "supprimé",
    "Supprime": "Supprimé",
    "supprimee": "supprimée",
    "Supprimee": "Supprimée",
    "modifie": "modifié",
    "Modifie": "Modifié",
    "modifiee": "modifiée",
    "Modifiee": "Modifiée",
    "valide": "validé",
    "Valide": "Validé",
    "validee": "validée",
    "Validee": "Validée",
    "configure": "configuré",
    "Configure": "Configuré",
    "configuree": "configurée",
    "Configuree": "Configurée",
    "initialise": "initialisé",
    "Initialise": "Initialisé",
    "initialisee": "initialisée",
    "Initialisee": "Initialisée",
    "termine": "terminé",
    "Termine": "Terminé",
    "terminee": "terminée",
    "Terminee": "Terminée",
    "active": "activé",
    "Active": "Activé",
    "activee": "activée",
    "Activee": "Activée",
    "desactive": "désactivé",
    "Desactive": "Désactivé",
    "desactivee": "désactivée",
    "Desactivee": "Désactivée",
    "bloque": "bloqué",
    "Bloque": "Bloqué",
    "bloquee": "bloquée",
    "Bloquee": "Bloquée",
    "debloque": "débloqué",
    "Debloque": "Débloqué",
    "debloquee": "débloquée",
    "Debloquee": "Débloquée",
    "lance": "lancé",
    "Lance": "Lancé",
    "lancee": "lancée",
    "Lancee": "Lancée",

    # Corrections spécifiques au contexte AGV/robotique
    "balayeur": "balayeur",  # Déjà correct
    "encodeur": "encodeur",  # Déjà correct
    "moteur": "moteur",
    "Moteur": "Moteur",
    "moteurs": "moteurs",
    "Moteurs": "Moteurs",
    "actionneur": "actionneur",
    "Actionneur": "Actionneur",
    "actionneurs": "actionneurs",
    "Actionneurs": "Actionneurs",
    "roue": "roue",
    "Roue": "Roue",
    "roues": "roues",
    "Roues": "Roues",
    "direction": "direction",
    "Direction": "Direction",
    "directions": "directions",
    "Directions": "Directions",
    "navigation": "navigation",
    "Navigation": "Navigation",
    "position": "position",
    "Position": "Position",
    "positions": "positions",
    "Positions": "Positions",
    "localisation": "localisation",
    "Localisation": "Localisation",
    "chargeur": "chargeur",
    "Chargeur": "Chargeur",
    "chargeurs": "chargeurs",
    "Chargeurs": "Chargeurs",
    "charge": "charge",
    "Charge": "Charge",
    "charges": "charges",
    "Charges": "Charges",
    "decharge": "décharge",
    "Decharge": "Décharge",
    "decharges": "décharges",
    "Decharges": "Décharges",
    "securite": "sécurité",
    "Securite": "Sécurité",
    "urgence": "urgence",
    "Urgence": "Urgence",
    "vehicule": "véhicule",
    "Vehicule": "Véhicule",
    "vehicules": "véhicules",
    "Vehicules": "Véhicules",
    "accessoire": "accessoire",
    "Accessoire": "Accessoire",
    "accessoires": "accessoires",
    "Accessoires": "Accessoires",

    # Corrections pour les distances et unités
    "metre": "mètre",
    "Metre": "Mètre",
    "metres": "mètres",
    "Metres": "Mètres",
    "centimetre": "centimètre",
    "Centimetre": "Centimètre",
    "centimetres": "centimètres",
    "Centimetres": "Centimètres",
    "degre": "degré",
    "Degre": "Degré",
    "degres": "degrés",
    "Degres": "Degrés",

    # Prépositions et articles
    "a distance": "à distance",
    "A distance": "À distance",
    "a l'arret": "à l'arrêt",
    "A l'arret": "À l'arrêt",
    "a l'arrêt": "à l'arrêt",
    "A l'arrêt": "À l'arrêt",
}

# Corrections spéciales (regex patterns)
CORRECTIONS_REGEX = [
    # Correction accord masculin/féminin pour certains contextes
    (r'\bmouvement\s+\w+\s+non\s+reconnue\b', lambda m: m.group(0).replace('reconnue', 'reconnu')),
    (r'\bversion\s+\w+\s+\w+\s+non\s+reconnue\b', lambda m: m.group(0).replace('reconnue', 'reconnue')),  # Version peut rester féminin

    # Correction des espaces avant les deux-points
    (r'\s+:', ':'),

    # Correction des guillemets
    (r'"([^"]*)"', r'« \1 »'),  # Optionnel : conversion en guillemets français
]

class VerificateurOrthographe:
    def __init__(self):
        self.corrections_appliquees = []
        self.fichiers_modifies = []

    def corriger_texte(self, texte: str) -> Tuple[str, List[str]]:
        """Corrige l'orthographe d'un texte et retourne le texte corrigé et la liste des corrections."""
        if not texte or not texte.strip():
            return texte, []

        texte_original = texte
        corrections_locales = []

        # Appliquer les corrections simples
        for incorrect, correct in CORRECTIONS_ORTHOGRAPHE.items():
            if incorrect in texte:
                ancien_texte = texte
                texte = texte.replace(incorrect, correct)
                if texte != ancien_texte:
                    corrections_locales.append(f"'{incorrect}' → '{correct}'")

        # Appliquer les corrections regex
        for pattern, replacement in CORRECTIONS_REGEX:
            if isinstance(replacement, str):
                nouveau_texte = re.sub(pattern, replacement, texte, flags=re.IGNORECASE)
            else:
                nouveau_texte = re.sub(pattern, replacement, texte, flags=re.IGNORECASE)

            if nouveau_texte != texte:
                corrections_locales.append(f"Pattern '{pattern}' appliqué")
                texte = nouveau_texte

        return texte, corrections_locales

    def verifier_fichier_json(self, filepath: str) -> bool:
        """Vérifie et corrige un fichier JSON français."""
        try:
            print(f"🔍 Vérification de {os.path.basename(filepath)}")

            # Charger le fichier JSON
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            modifications = False
            corrections_fichier = []

            # Vérifier les descriptions dans FaultDetailList
            if "FaultDetailList" in data:
                for i, fault in enumerate(data["FaultDetailList"]):
                    if "Description" in fault and fault["Description"]:
                        description_originale = fault["Description"]
                        description_corrigee, corrections = self.corriger_texte(description_originale)

                        if description_corrigee != description_originale:
                            fault["Description"] = description_corrigee
                            modifications = True
                            correction_info = {
                                "fichier": os.path.basename(filepath),
                                "index": i,
                                "avant": description_originale,
                                "après": description_corrigee,
                                "corrections": corrections
                            }
                            corrections_fichier.append(correction_info)
                            self.corrections_appliquees.append(correction_info)

            # Sauvegarder si des modifications ont été faites
            if modifications:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                self.fichiers_modifies.append(filepath)
                print(f"  ✅ {len(corrections_fichier)} correction(s) appliquée(s)")

                # Afficher les corrections
                for correction in corrections_fichier:
                    print(f"    • Index {correction['index']}: '{correction['avant']}' → '{correction['après']}'")
                    if correction['corrections']:
                        print(f"      Détails: {', '.join(correction['corrections'])}")

                return True
            else:
                print(f"  ✓ Aucune correction nécessaire")
                return False

        except Exception as e:
            print(f"  ❌ Erreur lors de la vérification de {filepath}: {e}")
            return False

    def generer_rapport(self) -> str:
        """Génère un rapport des corrections effectuées."""
        rapport = []
        rapport.append("# RAPPORT DE CORRECTION ORTHOGRAPHIQUE")
        rapport.append("=" * 50)
        rapport.append(f"Fichiers modifiés: {len(self.fichiers_modifies)}")
        rapport.append(f"Total corrections: {len(self.corrections_appliquees)}")
        rapport.append("")

        if self.corrections_appliquees:
            rapport.append("## DÉTAIL DES CORRECTIONS")
            rapport.append("-" * 30)

            fichiers_groupes = {}
            for correction in self.corrections_appliquees:
                fichier = correction["fichier"]
                if fichier not in fichiers_groupes:
                    fichiers_groupes[fichier] = []
                fichiers_groupes[fichier].append(correction)

            for fichier, corrections in fichiers_groupes.items():
                rapport.append(f"\n### {fichier}")
                for correction in corrections:
                    rapport.append(f"  Index {correction['index']}:")
                    rapport.append(f"    AVANT: {correction['avant']}")
                    rapport.append(f"    APRÈS: {correction['après']}")
                    if correction['corrections']:
                        rapport.append(f"    DÉTAILS: {', '.join(correction['corrections'])}")

        return "\n".join(rapport)

def main():
    parser = argparse.ArgumentParser(description='Vérifier et corriger l\'orthographe dans les fichiers JSON français')
    parser.add_argument('base_dir', help='Répertoire de base contenant les fichiers JSON')
    parser.add_argument('--dry-run', action='store_true', help='Afficher les corrections sans les appliquer')
    parser.add_argument('--rapport', help='Fichier pour sauvegarder le rapport de corrections')

    args = parser.parse_args()

    if not os.path.exists(args.base_dir):
        print(f"❌ Répertoire introuvable : {args.base_dir}")
        return 1

    print(f"🔍 Recherche des fichiers JSON français dans : {args.base_dir}")

    # Trouver tous les fichiers JSON français
    fichiers_fr = []
    for root, dirs, files in os.walk(args.base_dir):
        for file in files:
            if file.endswith('_fr.json'):
                fichiers_fr.append(os.path.join(root, file))

    if not fichiers_fr:
        print("❌ Aucun fichier JSON français trouvé")
        return 1

    print(f"📁 {len(fichiers_fr)} fichiers JSON français trouvés")

    if args.dry_run:
        print("🔍 MODE SIMULATION (dry-run) - Aucune modification ne sera effectuée")

    verificateur = VerificateurOrthographe()

    # Traiter chaque fichier
    for i, fichier in enumerate(fichiers_fr, 1):
        print(f"\n[{i}/{len(fichiers_fr)}] {os.path.relpath(fichier, args.base_dir)}")

        if not args.dry_run:
            verificateur.verifier_fichier_json(fichier)
        else:
            # Mode simulation - juste vérifier sans modifier
            try:
                with open(fichier, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                corrections_simulees = []
                if "FaultDetailList" in data:
                    for j, fault in enumerate(data["FaultDetailList"]):
                        if "Description" in fault and fault["Description"]:
                            description_originale = fault["Description"]
                            description_corrigee, corrections = verificateur.corriger_texte(description_originale)

                            if description_corrigee != description_originale:
                                corrections_simulees.append({
                                    "index": j,
                                    "avant": description_originale,
                                    "après": description_corrigee,
                                    "corrections": corrections
                                })

                if corrections_simulees:
                    print(f"  🔍 {len(corrections_simulees)} correction(s) possible(s):")
                    for correction in corrections_simulees:
                        print(f"    • Index {correction['index']}: '{correction['avant']}' → '{correction['après']}'")
                else:
                    print(f"  ✓ Aucune correction nécessaire")

            except Exception as e:
                print(f"  ❌ Erreur lors de la lecture de {fichier}: {e}")

    # Générer et afficher le rapport
    if not args.dry_run:
        print(f"\n📊 RÉSUMÉ:")
        print(f"   ✅ Fichiers modifiés : {len(verificateur.fichiers_modifies)}")
        print(f"   🔧 Total corrections : {len(verificateur.corrections_appliquees)}")

        if verificateur.corrections_appliquees:
            rapport = verificateur.generer_rapport()
            print(f"\n{rapport}")

            if args.rapport:
                with open(args.rapport, 'w', encoding='utf-8') as f:
                    f.write(rapport)
                print(f"\n💾 Rapport sauvegardé dans : {args.rapport}")

        if verificateur.fichiers_modifies:
            print("🎉 Corrections orthographiques terminées avec succès !")
        else:
            print("✅ Aucune correction orthographique nécessaire")

    return 0

if __name__ == "__main__":
    exit(main())
