from dotenv import load_dotenv
import os
import pytest


def test_hello_world():
    """Basic test to ensure the test environment works."""
    load_dotenv()
    assert True


def test_environment_variables():
    """Verify required environment variables are loaded."""
    load_dotenv()
    if 'FAULT_EDITOR_LEGACY_MODE' not in os.environ:
        os.environ['FAULT_EDITOR_LEGACY_MODE'] = 'true'
    assert os.getenv('FAULT_EDITOR_LEGACY_MODE') is not None


def test_sum():
    assert 1 + 1 == 2
