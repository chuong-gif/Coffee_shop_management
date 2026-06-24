import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "coffee_shop.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"
GOOGLE_CLIENT_SECRETS = BASE_DIR / "google_client_secret.json"
GOOGLE_TOKEN_PATH = BASE_DIR / ".google_drive_token.pickle"
DRIVE_ROOT_FOLDER_NAME = "QuanNuoc_Backup"
LAST_CLOUD_BACKUP_FILE = BASE_DIR / ".last_cloud_backup.txt"