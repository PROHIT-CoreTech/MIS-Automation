"""
core/config.py — Centralized application configuration.

All magic strings and environment-dependent values live here.
To override for production, set the corresponding environment variables
or copy .env.example → .env and fill in values.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# ── PROJECT ROOT ───────────────────────────────────────────────
_ROOT = Path(__file__).resolve().parent.parent

# ── DATABASE ───────────────────────────────────────────────────
MONGO_URI: str = os.environ.get('MONGO_URI_DEVELOPMENT', 'mongodb://localhost:27017/mis_portal')


# ── TALLY PRIME CONNECTION ─────────────────────────────────────
TALLY_URL: str     = os.environ.get('TALLY_URL', 'http://localhost:9000')
TALLY_TIMEOUT: int = int(os.environ.get('TALLY_TIMEOUT', '30'))

# ── AUTH / LOCKOUT ─────────────────────────────────────────────
MAX_ATTEMPTS: int  = int(os.environ.get('MAX_LOGIN_ATTEMPTS', '3'))
LOCKOUT_MINS: int  = int(os.environ.get('LOCKOUT_MINUTES', '30'))

# ── DEFAULT ADMIN ──────────────────────────────────────────────
ADMIN_USERNAME: str = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD: str = os.environ.get('ADMIN_PASSWORD', 'admin@123')

# ── MASTERS FILE ───────────────────────────────────────────────
MASTERS_PATH: str = os.environ.get(
    'MASTERS_PATH',
    str(_ROOT / 'config' / 'masters' / 'Masters.xlsx')
)
