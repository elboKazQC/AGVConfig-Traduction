import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure the package modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Provide a dummy API key for tests
os.environ.setdefault("OPENAI_API_KEY", "dummy-test-key")

from translate import traduire, OPENAI_API_KEY

class TestTranslation(unittest.TestCase):
    def test_api_key_configuration(self):
        """Test if the API key is configured correctly."""
        self.assertTrue(OPENAI_API_KEY and OPENAI_API_KEY != 'sk-test-key-for-development', "API Key is not configured properly.")

    @patch("translate.client.chat.completions.create")
    def test_translation_functionality(self, mock_create):
        """Test the translation functionality without real API calls."""
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "Hello"
        mock_response.choices = [mock_choice]
        mock_create.return_value = mock_response

        test_text = "Bonjour"
        result = traduire(test_text, "en")
        self.assertEqual(result, "Hello")

if __name__ == '__main__':
    unittest.main()
