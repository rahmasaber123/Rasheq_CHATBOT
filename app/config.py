import os
from pathlib import Path

# ── Load .env using python-dotenv (robust, handles edge cases) ──
try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(_env_path, override=False)
except ImportError:
    # Fallback manual .env parser
    _env_path = Path(__file__).resolve().parent.parent / ".env"
    if _env_path.exists():
        for line in _env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

# ── OpenAI API ──────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = "https://api.openai.com/v1/chat/completions"
MODEL_ID = "gpt-4o-mini"

# ── Generation Parameters ───────────────────────────────────
MAX_TOKENS = 1024
TEMPERATURE = 0.4
TOP_P = 0.9
STREAM = True

# ── Session ─────────────────────────────────────────────────
MAX_HISTORY_MESSAGES = 20

# ── Server ──────────────────────────────────────────────────
HOST = "0.0.0.0"
PORT = 8000
