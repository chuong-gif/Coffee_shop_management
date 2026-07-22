import os
import sys
from pathlib import Path

def get_base_path():
    if getattr(sys, 'frozen', False):
        # Khi đóng gói, lấy đường dẫn từ thư mục _internal của PyInstaller
        return sys._MEIPASS
    else:
        # Khi chạy code (python main.py), lấy thư mục gốc dự án
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE_DIR = Path(get_base_path())

# Tạo đường dẫn tuyệt đối chuẩn xác
DB_PATH = BASE_DIR / "database" / "coffee_shop.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"
GOOGLE_CLIENT_SECRETS = BASE_DIR / "google_client_secret.json"
GOOGLE_TOKEN_PATH = BASE_DIR / ".google_drive_token.pickle"
DRIVE_ROOT_FOLDER_NAME = "QuanNuoc_Backup"
LAST_CLOUD_BACKUP_FILE = BASE_DIR / ".last_cloud_backup.txt"