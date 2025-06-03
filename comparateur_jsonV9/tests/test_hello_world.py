"""Basic unit tests for sanity checks."""

import unittest


class TestHelloWorld(unittest.TestCase):
    """Simple tests to validate the test infrastructure."""

    def test_hello_world(self):
        """Ensure the most basic assertion works."""
        self.assertTrue(True)

    def test_error_handling(self):
        """Ensure error handling logic is tested."""
        with self.assertRaises(ValueError):
            raise ValueError("Test error")


if __name__ == "__main__":
    unittest.main()
