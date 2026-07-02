import os
import shutil
import datetime
import sqlite3
import json
import hashlib
import zipfile
from src.config import DB_PATH

class BackupController:
    def __init__(self):
        self.db_path = str(DB_PATH)
        self.config_path = os.path.join(os.path.dirname(self.db_path), "backup_config.json")
        self.image_dir = os.path.join(os.path.dirname(self.db_path), "images")
        
        self._init_sys_logs()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_sys_logs(self):
        conn = self._connect()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS nhat_ky_he_thong (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thoi_gian DATETIME DEFAULT CURRENT_TIMESTAMP,
                hanh_dong TEXT,
                chi_tiet TEXT
            )
        """)
        conn.commit()
        conn.close()

    def log_action(self, action, detail):
        conn = self._connect()
        conn.execute("INSERT INTO nhat_ky_he_thong (hanh_dong, chi_tiet) VALUES (?, ?)", (action, detail))
        conn.commit()
        conn.close()

    def get_system_logs(self, limit=20):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT datetime(thoi_gian, 'localtime'), hanh_dong, chi_tiet FROM nhat_ky_he_thong ORDER BY id DESC LIMIT ?", (limit,))
        logs = cursor.fetchall()
        conn.close()
        return logs

    def _calculate_sha256(self, filepath):
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    # ==========================================
    # ĐỒNG BỘ 1 CHẠM (.coffee)
    # ==========================================
    def export_1_touch(self, dest_path):
        if not os.path.exists(self.db_path):
            raise FileNotFoundError("Không tìm thấy cơ sở dữ liệu gốc.")

        temp_dir = os.path.join(os.path.dirname(self.db_path), "temp_export")
        os.makedirs(temp_dir, exist_ok=True)

        try:
            temp_db_path = os.path.join(temp_dir, "coffee_shop.db")
            shutil.copy2(self.db_path, temp_db_path)

            db_hash = self._calculate_sha256(temp_db_path)

            manifest = {
                "export_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "db_hash": db_hash,
                "version": "1.0"
            }
            with open(os.path.join(temp_dir, "manifest.json"), "w", encoding="utf-8") as f:
                json.dump(manifest, f)

            with zipfile.ZipFile(dest_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(temp_db_path, "coffee_shop.db")
                zipf.write(os.path.join(temp_dir, "manifest.json"), "manifest.json")
                
                if os.path.exists(self.image_dir):
                    for root, _, files in os.walk(self.image_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, os.path.dirname(self.db_path))
                            zipf.write(file_path, arcname)

            self.log_action("DATA_EXPORT", f"Xuất gói đồng bộ thành công. Checksum: {db_hash[:8]}...")
            return True
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def import_1_touch(self, source_path):
        if not os.path.exists(source_path):
            raise FileNotFoundError("Không tìm thấy file nguồn.")

        temp_dir = os.path.join(os.path.dirname(self.db_path), "temp_import")
        os.makedirs(temp_dir, exist_ok=True)

        try:
            with zipfile.ZipFile(source_path, 'r') as zipf:
                zipf.extractall(temp_dir)

            manifest_path = os.path.join(temp_dir, "manifest.json")
            temp_db_path = os.path.join(temp_dir, "coffee_shop.db")

            if not os.path.exists(manifest_path) or not os.path.exists(temp_db_path):
                raise ValueError("File .coffee không hợp lệ hoặc bị hỏng.")

            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)

            current_db_hash = self._calculate_sha256(temp_db_path)
            if current_db_hash != manifest.get("db_hash"):
                self.log_action("SECURITY_ALERT", "Từ chối Import do file DB bị sửa đổi!")
                raise PermissionError("LỖI BẢO MẬT: File dữ liệu đã bị can thiệp. Từ chối nạp!")

            safe_backup = f"{self.db_path}.safe_bak"
            shutil.copy2(self.db_path, safe_backup)
            
            try:
                shutil.copy2(temp_db_path, self.db_path)
                
                temp_img_dir = os.path.join(temp_dir, "images")
                if os.path.exists(temp_img_dir):
                    os.makedirs(self.image_dir, exist_ok=True)
                    for item in os.listdir(temp_img_dir):
                        s = os.path.join(temp_img_dir, item)
                        d = os.path.join(self.image_dir, item)
                        if os.path.isfile(s):
                            shutil.copy2(s, d)

                if os.path.exists(safe_backup): os.remove(safe_backup)
                self.log_action("DATA_IMPORT", f"Nạp đồng bộ từ bản xuất ngày {manifest.get('export_time')}")
                return True
                
            except Exception as e:
                if os.path.exists(safe_backup):
                    shutil.copy2(safe_backup, self.db_path)
                raise e

        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    # ==========================================
    # SAO LƯU TỰ ĐỘNG - FILE PHẲNG & GIỮ 7 FILE
    # ==========================================
    def load_auto_backup_config(self):
        default_config = {
            "path": os.path.join(os.path.dirname(self.db_path), "Data"),
            "enabled": True,
            "interval_num": 1,
            "interval_unit": "Giờ"
        }
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    default_config.update(loaded)
            except: pass
        return default_config

    def save_auto_backup_config(self, path, enabled, interval_num, interval_unit):
        config = {
            "path": path, 
            "enabled": enabled,
            "interval_num": interval_num,
            "interval_unit": interval_unit
        }
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f)

    def trigger_auto_backup(self):
        """Sao lưu trực tiếp vào thư mục gốc, tự dọn rác giữ 7 file gần nhất"""
        config = self.load_auto_backup_config()
        if not config["enabled"]:
            return False, "Auto Backup đang tắt."

        base_dir = config["path"]
        os.makedirs(base_dir, exist_ok=True)

        now = datetime.datetime.now()
        
        # Tên file phẳng: DataBackup_YYYY_MM_DD.zip
        backup_filename = f"DataBackup_{now.strftime('%Y_%m_%d')}.zip"
        dest_zip = os.path.join(base_dir, backup_filename)
        
        # Đóng gói nén DB
        with zipfile.ZipFile(dest_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(self.db_path, "coffee_shop.db")

        # Quét rác tự động, giữ 7 file
        self._cleanup_old_backups(base_dir, keep_count=7)

        self.log_action("AUTO_BACKUP", f"Tạo bản sao lưu định kỳ: {backup_filename}")
        return True, dest_zip

    def _cleanup_old_backups(self, base_dir, keep_count=7):
        """Giữ lại 'keep_count' file backup gần nhất, trảm các file còn lại"""
        if not os.path.exists(base_dir): 
            return
            
        backup_files = []
        for file in os.listdir(base_dir):
            if file.startswith("DataBackup_") and file.endswith(".zip"):
                filepath = os.path.join(base_dir, file)
                if os.path.isfile(filepath):
                    backup_files.append(filepath)
        
        # Sắp xếp theo mốc thời gian sửa đổi (mới nhất đứng đầu)
        backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        # Xóa các file từ vị trí số 7 trở đi
        if len(backup_files) > keep_count:
            files_to_delete = backup_files[keep_count:]
            for filepath in files_to_delete:
                try: 
                    os.remove(filepath)
                except: 
                    pass