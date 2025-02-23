import pytest
from unittest.mock import Mock
from chains import create_chains

@pytest.fixture
def mock_llm():
    return Mock()

def test_chain_creation():
    chains = create_chains()
    assert "key_points" in chains
    assert "summary" in chains
    assert chains["key_points"].name == "ChatGoogleGenerativeAI"

def test_key_points_prompt():
    chains = create_chains()
    prompt = chains["key_points"].prompt
    assert "Identify {num_points} key points" in prompt.template

def test_summary_prompt():
    chains = create_chains()
    prompt = chains["summary"].prompt
    assert "Create summary" in prompt.template