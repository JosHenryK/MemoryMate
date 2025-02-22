import os
import pytest
from config import CONFIG, LLM_CONFIG, get_save_path

def test_config_constants():
    assert isinstance(CONFIG["max_history"], int)
    assert CONFIG["max_history"] > 0
    assert isinstance(CONFIG["wake_word"], str)
    
def test_llm_config():
    assert LLM_CONFIG["model_name"] == "gemini-1.5-flash"
    assert 0 <= LLM_CONFIG["temperature"] <= 1

def test_get_save_path(tmp_path):
    original = CONFIG["save_folder"]
    try:
        CONFIG["save_folder"] = str(tmp_path / "test_saves")
        path = get_save_path()
        assert os.path.exists(path)
        assert "test_saves" in path
    finally:
        CONFIG["save_folder"] = original