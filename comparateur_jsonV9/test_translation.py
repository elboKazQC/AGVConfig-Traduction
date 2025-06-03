import unittest
from translate import traduire, OPENAI_API_KEY

class TestTranslation(unittest.TestCase):
    def test_api_key_configuration(self):
        """Test if the API key is configured correctly."""
        self.assertTrue(OPENAI_API_KEY and OPENAI_API_KEY != 'sk-test-key-for-development', "API Key is not configured properly.")

    def test_translation_functionality(self):
        """Test the translation functionality."""
        test_text = "Bonjour"
        try:
            result = traduire(test_text, "en")
            self.assertIsNotNone(result, "Translation result is None.")
            self.assertNotEqual(result, test_text, "Translation did not change the text.")
        except Exception as e:
            self.fail(f"Translation test failed with exception: {e}")

if __name__ == '__main__':
    unittest.main()
