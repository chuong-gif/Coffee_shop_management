import sqlite3
from src.config import DB_PATH

class TableModel:
    def __init__(self):
        self.db_path = str(DB_PATH)

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def get_all_tables(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, ten_ban, trang_thai FROM ban ORDER BY id")
        tables = cursor.fetchall()
        conn.close()
        return tables

    def add_table(self, ten_ban):
        """Thêm một bàn mới vào hệ thống"""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ban (ten_ban, trang_thai) VALUES (?, 'Trống')", (ten_ban,))
        conn.commit()
        conn.close()

    def delete_table(self, table_id):
        """Xóa bàn theo ID"""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ban WHERE id = ?", (table_id,))
        conn.commit()
        conn.close()

    def update_table_name(self, table_id, new_name):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE ban SET ten_ban = ? WHERE id = ?", (new_name, table_id))
        conn.commit()
        conn.close()

    def set_table_status(self, table_id, status):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE ban SET trang_thai = ? WHERE id = ?", (status, table_id))
        conn.commit()
        conn.close()

    def get_table_by_id(self, table_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, ten_ban, trang_thai FROM ban WHERE id = ?", (table_id,))
        table = cursor.fetchone()
        conn.close()
        return table

    def get_table_by_name(self, ten_ban):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, ten_ban, trang_thai FROM ban WHERE ten_ban = ?", (ten_ban,))
        table = cursor.fetchone()
        conn.close()
        return table