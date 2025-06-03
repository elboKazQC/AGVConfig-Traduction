from dotenv import load_dotenv

def test_hello_world():
    """Test de base pour vérifier que l'environnement de test fonctionne."""
    load_dotenv()
    assert True, "L'environnement de test fonctionne correctement"

def test_environment_variables():
    """Test pour vérifier que les variables d'environnement sont chargées."""
    load_dotenv()
    assert os.getenv('FAULT_EDITOR_LEGACY_MODE') is not None
if __name__ == '__main__':
    pytest.main(['-v'])

def test_hello_world():
    assert 1 + 1 == 2