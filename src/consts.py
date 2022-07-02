from pathlib import Path

ADDON_DIR = Path(__file__).parent
USERFILES_DIR = ADDON_DIR / "user_files"
PROVIDERS_DIR = ADDON_DIR / "providers"
VENDOR_DIR = PROVIDERS_DIR / "vendor"
DB_FILE = USERFILES_DIR / "sentences.db"
