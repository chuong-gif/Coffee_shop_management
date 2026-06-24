# Quản lý kết nối, đóng/mở và thực thi câu lệnh SQL chung
import sqlite3
import os
from src.config import DB_PATH, SCHEMA_PATH

class DatabaseManager:
    def __init__(self):
        self.db_path = str(DB_PATH)
        self.schema_path = str(SCHEMA_PATH)

    def get_connection(self):
        """Tạo và trả về đối tượng kết nối với SQLite"""
        return sqlite3.connect(self.db_path)

    def init_database(self):
        """Hàm này sẽ đọc file schema.sql và tạo các bảng nếu chưa có"""
        if not os.path.exists(self.schema_path):
            print("Lỗi: Không tìm thấy file schema.sql!")
            return

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            with open(self.schema_path, "r", encoding="utf-8") as f:
                sql_script = f.read()
            cursor.executescript(sql_script)
            conn.commit()
            print("Database initialized successfully!")
            self._migrate_database(conn)
        except Exception as e:
            print(f"Database initialization error: {e}")
        finally:
            conn.close()

    def _migrate_database(self, conn):
        cursor = conn.cursor()
        try:
            cursor.execute("PRAGMA table_info(do_uong)")
            columns = [row[1] for row in cursor.fetchall()]
            if "ma_mon" not in columns:
                cursor.execute("ALTER TABLE do_uong ADD COLUMN ma_mon TEXT DEFAULT NULL")
            if "hinh_anh" not in columns:
                cursor.execute("ALTER TABLE do_uong ADD COLUMN hinh_anh TEXT DEFAULT NULL")
            if "created_at" not in columns:
                cursor.execute("ALTER TABLE do_uong ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
            if "updated_at" not in columns:
                cursor.execute("ALTER TABLE do_uong ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP")
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute("PRAGMA table_info(kho_nguyen_lieu)")
            columns = [row[1] for row in cursor.fetchall()]
            if "ton_ly_thuyet" not in columns:
                cursor.execute("ALTER TABLE kho_nguyen_lieu ADD COLUMN ton_ly_thuyet REAL NOT NULL DEFAULT 0")
            if "gia_von" not in columns:
                cursor.execute("ALTER TABLE kho_nguyen_lieu ADD COLUMN gia_von REAL NOT NULL DEFAULT 0")
            if "updated_at" not in columns:
                cursor.execute("ALTER TABLE kho_nguyen_lieu ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP")
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute("PRAGMA table_info(don_hang)")
            columns = [row[1] for row in cursor.fetchall()]
            if "ma_don" not in columns:
                cursor.execute("ALTER TABLE don_hang ADD COLUMN ma_don TEXT DEFAULT NULL")
            if "tien_khach_dua" not in columns:
                cursor.execute("ALTER TABLE don_hang ADD COLUMN tien_khach_dua INTEGER NOT NULL DEFAULT 0")
            if "tien_thua" not in columns:
                cursor.execute("ALTER TABLE don_hang ADD COLUMN tien_thua INTEGER NOT NULL DEFAULT 0")
            if "trang_thai" not in columns:
                cursor.execute("ALTER TABLE don_hang ADD COLUMN trang_thai TEXT NOT NULL DEFAULT 'Mở'")
            if "thoi_gian_thanh_toan" not in columns:
                cursor.execute("ALTER TABLE don_hang ADD COLUMN thoi_gian_thanh_toan DATETIME")
            if "ghi_chu" not in columns:
                cursor.execute("ALTER TABLE don_hang ADD COLUMN ghi_chu TEXT DEFAULT NULL")
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='danh_muc'")
            if cursor.fetchone() is None:
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS danh_muc (id INTEGER PRIMARY KEY AUTOINCREMENT, ten_danh_muc TEXT NOT NULL UNIQUE)"
                )
        except sqlite3.OperationalError:
            pass

        conn.commit()
