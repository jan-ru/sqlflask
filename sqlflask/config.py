import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "sqlflask.db"
EXCEL_DIR = BASE_DIR / "data" / "excel_versions"
if not EXCEL_DIR.exists():
    EXCEL_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR = BASE_DIR / "templates"
if not TEMPLATES_DIR.exists():
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR = BASE_DIR / "static"
if not STATIC_DIR.exists():
    STATIC_DIR.mkdir(parents=True, exist_ok=True)