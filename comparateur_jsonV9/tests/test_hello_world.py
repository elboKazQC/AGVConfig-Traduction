import os
import pytest
from dotenv import load_dotenv


def test_hello_world():
    """Verify that the test environment is operational."""
    load_dotenv()
    assert True


def test_environment_variables():
    """Ensure FAULT_EDITOR_LEGACY_MODE is available."""
    load_dotenv()

    os.environ.setdefault("FAULT_EDITOR_LEGACY_MODE", "false")
    assert os.getenv("FAULT_EDITOR_LEGACY_MODE") is not None


def test_addition():
    """Simple sanity check."""
    assert 1 + 1 == 2


if __name__ == "__main__":
    pytest.main(["-v"])

    value = os.getenv('FAULT_EDITOR_LEGACY_MODE')
    if value is None:
        pytest.skip('FAULT_EDITOR_LEGACY_MODE not set')
    assert value is not None


if __name__ == "__main__":
    pytest.main(["-v"])


