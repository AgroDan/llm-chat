import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

CONFIG_PATH = Path(__file__).parent / "config.json"

_DEFAULTS = {
    "provider": "ollama",
    "openai_api_key": "",
    "anthropic_api_key": "",
    "base_url": "http://localhost:11434",
    "model": "llama3",
    "system_prompt": "You are a helpful assistant.",
    "admin_password": "admin",
}

# Map from config key -> environment variable name
_ENV_KEYS = {
    "provider": "LLM_PROVIDER",
    "openai_api_key": "OPENAI_API_KEY",
    "anthropic_api_key": "ANTHROPIC_API_KEY",
    "base_url": "LLM_BASE_URL",
    "model": "LLM_MODEL",
    "system_prompt": "SYSTEM_PROMPT",
    "admin_password": "ADMIN_PASSWORD",
}


def _load_json_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {}


def get_config():
    # Start with hardcoded defaults
    merged = dict(_DEFAULTS)
    # Override with env vars
    env_overrides = {key: os.getenv(env_var) for key, env_var in _ENV_KEYS.items()}
    merged.update({k: v for k, v in env_overrides.items() if v is not None})
    # Saved config (admin panel) always wins
    merged.update({k: v for k, v in _load_json_config().items() if v != ""})
    return merged


def save_config(data):
    existing = _load_json_config()
    existing.update(data)
    with open(CONFIG_PATH, "w") as f:
        json.dump(existing, f, indent=2)
