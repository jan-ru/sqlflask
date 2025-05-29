from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "default.sqlite"
EXCEL_DIR = BASE_DIR / "data" / "excel_versions"