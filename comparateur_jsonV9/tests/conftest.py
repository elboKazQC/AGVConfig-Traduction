from dotenv import load_dotenv
import os
import pytest

@pytest.fixture(autouse=True)
def load_env():
    load_dotenv()

    # Optionally, you can set default values for environment variables here
    os.environ.setdefault('MY_ENV_VAR', 'default_value')