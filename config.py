import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

CONFIG_PATH = Path(__file__).parent / "config.json"

_ENV_DEFAULTS = {
    "provider": os.getenv("LLM_PROVIDER", "ollama"),
    "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
    "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY", ""),
    "base_url": os.getenv("LLM_BASE_URL", "http://localhost:11434"),
    "model": os.getenv("LLM_MODEL", "llama3"),
    "system_prompt": os.getenv("SYSTEM_PROMPT", "You are a helpful assistant."),
    "admin_password": os.getenv("ADMIN_PASSWORD", "admin"),
}


def _load_json_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {}


def get_config():
    merged = dict(_ENV_DEFAULTS)
    merged.update({k: v for k, v in _load_json_config().items() if v != ""})
    return merged


def save_config(data):
    existing = _load_json_config()
    existing.update(data)
    with open(CONFIG_PATH, "w") as f:
        json.dump(existing, f, indent=2)
