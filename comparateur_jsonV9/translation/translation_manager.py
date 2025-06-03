# Gestionnaire de traduction pour l'application Fault Editor
"""
Ce module gère toutes les fonctionnalités de traduction.
Utilisez ces classes pour traduire du texte et gérer les traductions en lots.
"""

import logging
from typing import Dict, List, Optional
from translate import traduire

logger = logging.getLogger(__name__)

class TranslationManager:
    """Gestionnaire principal pour les traductions"""

    def __init__(self):
        self.translation_cache: Dict[str, Dict[str, str]] = {}

    def translate_text(self, text: str, target_language: str, source_language: str = "fr") -> str:
        """Traduit un texte vers la langue cible"""
        if not text.strip():
            return text

        # Vérifier le cache
        cache_key = f"{source_language}_{target_language}_{text}"
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]

        try:
            translated = traduire(text, target_language)
            # Mettre en cache le résultat
            self.translation_cache[cache_key] = translated
            logger.info(f"Texte traduit : '{text}' -> '{translated}' ({target_language})")
            return translated
        except Exception as e:
            logger.error(f"Erreur lors de la traduction de '{text}' vers {target_language}: {e}")
            return text

    def translate_multiple(self, texts: List[str], target_language: str,
                          source_language: str = "fr") -> List[str]:
        """Traduit plusieurs textes en une fois"""
        results = []
        for text in texts:
            translated = self.translate_text(text, target_language, source_language)
            results.append(translated)
        return results

    def clear_cache(self):
        """Vide le cache de traductions"""
        self.translation_cache.clear()
        logger.info("Cache de traductions vidé")

    def cleanup(self):
        """Nettoie les ressources utilisées par le gestionnaire de traduction"""
        self.clear_cache()
        logger.info("Nettoyage du gestionnaire de traduction terminé")

class BatchTranslator:
    """Gestionnaire pour les traductions en lot"""

    def __init__(self, translation_manager: TranslationManager):
        self.translation_manager = translation_manager
        self.progress_callback: Optional[callable] = None

    def set_progress_callback(self, callback: callable):
        """Définit une fonction de callback pour suivre le progrès"""
        self.progress_callback = callback

    def translate_flat_data(self, fr_data: Dict[str, str], keys_to_translate: List[str]) -> Dict[str, Dict[str, str]]:
        """Traduit des données plates du français vers l'anglais et l'espagnol"""
        results = {"en": {}, "es": {}}
        total_keys = len(keys_to_translate)

        for idx, key in enumerate(keys_to_translate):
            fr_text = fr_data.get(key, "")

            if fr_text.strip():
                # Traduire vers l'anglais
                results["en"][key] = self.translation_manager.translate_text(fr_text, "en")

                # Traduire vers l'espagnol
                results["es"][key] = self.translation_manager.translate_text(fr_text, "es")
            else:
                results["en"][key] = ""
                results["es"][key] = ""

            # Notifier le progrès
            if self.progress_callback:
                progress = (idx + 1) / total_keys * 100
                self.progress_callback(progress, f"Traduction de '{key}'")

        return results

    def translate_hierarchical_data(self, fault_list: List[Dict], language: str) -> List[Dict]:
        """Traduit une liste de défauts hiérarchiques"""
        translated_faults = []
        total_faults = len(fault_list)

        for idx, fault in enumerate(fault_list):
            translated_fault = fault.copy()

            # Traduire la description
            if "Description" in fault and fault["Description"]:
                translated_fault["Description"] = self.translation_manager.translate_text(
                    fault["Description"], language
                )

            translated_faults.append(translated_fault)

            # Notifier le progrès
            if self.progress_callback:
                progress = (idx + 1) / total_faults * 100
                self.progress_callback(progress, f"Traduction du défaut {idx + 1}")

        return translated_faults

class TranslationValidator:
    """Validateur pour les traductions"""

    @staticmethod
    def validate_translation(original: str, translated: str, target_language: str) -> Dict[str, any]:
        """Valide une traduction et retourne un rapport"""
        issues = []

        # Vérifications de base
        if not translated or translated == original:
            issues.append("Traduction identique à l'original ou vide")

        if len(translated) > len(original) * 3:
            issues.append("Traduction anormalement longue")

        if len(translated) < len(original) * 0.3:
            issues.append("Traduction anormalement courte")

        # Vérifier la présence de caractères spéciaux conservés
        special_chars = ["{", "}", "[", "]", "(", ")", "%", "#"]
        for char in special_chars:
            if char in original and char not in translated:
                issues.append(f"Caractère spécial manquant : {char}")

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "original": original,
            "translated": translated,
            "target_language": target_language
        }

    @staticmethod
    def batch_validate(translations: Dict[str, str], originals: Dict[str, str],
                      target_language: str) -> Dict[str, Dict]:
        """Valide un lot de traductions"""
        results = {}

        for key in translations:
            if key in originals:
                validation = TranslationValidator.validate_translation(
                    originals[key], translations[key], target_language
                )
                results[key] = validation

        return results
