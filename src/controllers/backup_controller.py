import datetime
import os
import shutil
from src.config import DB_PATH, GOOGLE_CLIENT_SECRETS, GOOGLE_TOKEN_PATH, DRIVE_ROOT_FOLDER_NAME
from src.utils.drive_helper import upload_database_backup

class BackupController:
    def __init__(self):
        self.db_path = str(DB_PATH)
        self.client_secrets = str(GOOGLE_CLIENT_SECRETS)
        self.token_path = str(GOOGLE_TOKEN_PATH)
        self.drive_root_folder_name = DRIVE_ROOT_FOLDER_NAME

    def create_local_backup(self):
        if not os.path.exists(self.db_path):
            raise FileNotFoundError("Không tìm thấy file database để sao lưu.")

        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"coffee_shop_backup_{now}.db"
        target_path = os.path.join(os.path.dirname(self.db_path), backup_name)
        shutil.copy2(self.db_path, target_path)
        return target_path

    def backup_to_google_drive(self):
        if not os.path.exists(self.client_secrets):
            raise FileNotFoundError("Không tìm thấy file google_client_secret.json.")

        return upload_database_backup(
            client_secrets_path=self.client_secrets,
            token_path=self.token_path,
            app_root_folder_name=self.drive_root_folder_name,
            local_db_path=self.db_path,
        )
