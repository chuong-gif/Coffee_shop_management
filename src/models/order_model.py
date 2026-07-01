import datetime
import sqlite3
import json
from src.config import DB_PATH
from src.models.table_model import TableModel
from src.models.stock_model import StockModel

class OrderModel:
    def __init__(self):
        self.db_path = str(DB_PATH)
        self.table_model = TableModel()
        self.stock_model = StockModel()
        
        try:
            conn = self._connect()
            conn.execute("ALTER TABLE chi_tiet_don_hang ADD COLUMN cong_thuc_tuy_chinh TEXT DEFAULT NULL")
            conn.commit()
            conn.close()
        except Exception:
            pass 

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def create_order(self, table_id=None, loai_don="Tại bàn"):
        order_code = f"DH{int(datetime.datetime.now().timestamp())}"
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO don_hang (ma_don, ban_id, loai_don) VALUES (?, ?, ?)", (order_code, table_id, loai_don))
        conn.commit()
        order_id = cursor.lastrowid
        conn.close()
        if table_id is not None:
            self.table_model.set_table_status(table_id, "Có khách")
        return order_id

    def get_open_order_by_table(self, table_id=None):
        conn = self._connect()
        cursor = conn.cursor()
        if table_id is None:
            cursor.execute("SELECT id, ma_don, ban_id, loai_don, ghi_chu FROM don_hang WHERE ban_id IS NULL AND trang_thai = 'Mở' ORDER BY id DESC LIMIT 1")
        else:
            cursor.execute("SELECT id, ma_don, ban_id, loai_don, ghi_chu FROM don_hang WHERE ban_id = ? AND trang_thai = 'Mở' ORDER BY id DESC LIMIT 1", (table_id,))
        order = cursor.fetchone()

        # [FIX]: Nếu đơn "Mở" nhưng KHÔNG có món nào (rác từ dữ liệu cũ, hoặc lỗi phát sinh),
        # tự động hủy ngầm và coi như KHÔNG có đơn đang mở -> tránh hiển thị "Đơn #xx" ma
        if order:
            order_id = order[0]
            cursor.execute("SELECT COUNT(*) FROM chi_tiet_don_hang WHERE don_hang_id = ?", (order_id,))
            item_count = cursor.fetchone()[0]
            if item_count == 0:
                cursor.execute("UPDATE don_hang SET trang_thai = 'Đã Hủy' WHERE id = ?", (order_id,))
                conn.commit()
                conn.close()
                if table_id is not None:
                    self.table_model.set_table_status(table_id, "Trống")
                return None

        conn.close()
        return order

    def get_or_create_open_order(self, table_id=None, loai_don="Tại bàn"):
        order = self.get_open_order_by_table(table_id)
        if order: return order[0]
        return self.create_order(table_id, loai_don)

    def add_order_item(self, order_id, do_uong_id, quantity=1, ghi_chu=None):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT gia_ban FROM do_uong WHERE id = ?", (do_uong_id,))
        row = cursor.fetchone()
        if not row: return

        don_gia = int(row[0])
        if not ghi_chu:
            cursor.execute("SELECT id, so_luong FROM chi_tiet_don_hang WHERE don_hang_id = ? AND do_uong_id = ? AND (ghi_chu IS NULL OR ghi_chu = '') AND cong_thuc_tuy_chinh IS NULL", (order_id, do_uong_id))
            existing = cursor.fetchone()
            if existing:
                item_id, existing_qty = existing
                cursor.execute("UPDATE chi_tiet_don_hang SET so_luong = ? WHERE id = ?", (existing_qty + quantity, item_id))
            else:
                cursor.execute("INSERT INTO chi_tiet_don_hang (don_hang_id, do_uong_id, so_luong, don_gia, ghi_chu) VALUES (?, ?, ?, ?, ?)", (order_id, do_uong_id, quantity, don_gia, ghi_chu))
        else:
            cursor.execute("INSERT INTO chi_tiet_don_hang (don_hang_id, do_uong_id, so_luong, don_gia, ghi_chu) VALUES (?, ?, ?, ?, ?)", (order_id, do_uong_id, quantity, don_gia, ghi_chu))
        conn.commit()
        conn.close()

    def get_order_items(self, order_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT c.id, c.do_uong_id, d.ten_mon, c.so_luong, c.don_gia, c.ghi_chu, c.so_luong * c.don_gia, c.cong_thuc_tuy_chinh "
            "FROM chi_tiet_don_hang c JOIN do_uong d ON c.do_uong_id = d.id WHERE c.don_hang_id = ?",
            (order_id,),
        )
        items = cursor.fetchall()
        conn.close()
        return items

    def calculate_order_total(self, order_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(SUM(so_luong * don_gia), 0) FROM chi_tiet_don_hang WHERE don_hang_id = ?", (order_id,))
        total = cursor.fetchone()[0]
        conn.close()
        return total

    def update_order_note(self, order_id, ghi_chu):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE don_hang SET ghi_chu = ? WHERE id = ?", (ghi_chu, order_id))
        conn.commit()
        conn.close()

    def get_order_note_by_order_id(self, order_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT ghi_chu FROM don_hang WHERE id = ?", (order_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    def close_order(self, order_id, tien_khach_dua):
        total = self.calculate_order_total(order_id)
        if tien_khach_dua < total: return total, None
        tien_thua = int(tien_khach_dua - total)

        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT ban_id FROM don_hang WHERE id = ?", (order_id,))
        row = cursor.fetchone()
        ban_id = row[0] if row else None

        order_items = self.get_order_items(order_id)
        recipe_items = [{"do_uong_id": item[1], "so_luong": item[3], "cong_thuc_tuy_chinh": item[7]} for item in order_items]
        
        if recipe_items:
            self.stock_model.deduct_ingredients(recipe_items)

        cursor.execute("UPDATE don_hang SET tong_tien = ?, tien_khach_dua = ?, tien_thua = ?, trang_thai = 'Đã Thanh Toán', thoi_gian_thanh_toan = CURRENT_TIMESTAMP WHERE id = ?", (total, tien_khach_dua, tien_thua, order_id))
        conn.commit()
        conn.close()

        if ban_id is not None:
            self.table_model.set_table_status(ban_id, "Trống")
        return total, tien_thua

    # [FIX CỐT LÕI]: Dùng trực tiếp order_id để Move hoặc Merge
    def move_order(self, order_id, source_table_id, target_table_id):
        if source_table_id == target_table_id: return False

        target_order = self.get_open_order_by_table(target_table_id)
        if target_order:
            return self.merge_orders_by_id(order_id, target_order[0], source_table_id, target_table_id)

        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE don_hang SET ban_id = ? WHERE id = ?", (target_table_id, order_id))
        conn.commit()
        conn.close()

        if source_table_id:
            self.table_model.set_table_status(source_table_id, "Trống")
        self.table_model.set_table_status(target_table_id, "Có khách")
        return order_id

    def merge_orders_by_id(self, source_order_id, target_order_id, source_table_id, target_table_id):
        conn = self._connect()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE chi_tiet_don_hang SET don_hang_id = ? WHERE don_hang_id = ?", (target_order_id, source_order_id))
        
        cursor.execute("SELECT ghi_chu FROM don_hang WHERE id = ?", (source_order_id,))
        s_note = cursor.fetchone()
        cursor.execute("SELECT ghi_chu FROM don_hang WHERE id = ?", (target_order_id,))
        t_note = cursor.fetchone()
        
        s_text = s_note[0] if s_note and s_note[0] else ""
        t_text = t_note[0] if t_note and t_note[0] else ""
        merged_note = t_text
        if s_text:
            merged_note = f"{merged_note}\n{s_text}" if merged_note else s_text
            
        if merged_note:
            cursor.execute("UPDATE don_hang SET ghi_chu = ? WHERE id = ?", (merged_note, target_order_id))
            
        cursor.execute("DELETE FROM don_hang WHERE id = ?", (source_order_id,))
        conn.commit()
        conn.close()
        
        if source_table_id:
            self.table_model.set_table_status(source_table_id, "Trống")
        self.table_model.set_table_status(target_table_id, "Có khách")
        return target_order_id

    def update_item_quantity(self, item_id, new_qty):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE chi_tiet_don_hang SET so_luong = ? WHERE id = ?", (new_qty, item_id))
        cursor.execute("SELECT don_hang_id FROM chi_tiet_don_hang WHERE id = ?", (item_id,))
        self._update_order_total(cursor, cursor.fetchone()[0])
        conn.commit()
        conn.close()

    def remove_order_item(self, item_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT don_hang_id FROM chi_tiet_don_hang WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        if row:
            don_hang_id = row[0]
            cursor.execute("DELETE FROM chi_tiet_don_hang WHERE id = ?", (item_id,))
            cursor.execute("SELECT COUNT(*) FROM chi_tiet_don_hang WHERE don_hang_id = ?", (don_hang_id,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("SELECT ban_id FROM don_hang WHERE id = ?", (don_hang_id,))
                b_row = cursor.fetchone()
                ban_id = b_row[0] if b_row else None
                cursor.execute("UPDATE don_hang SET trang_thai = 'Đã Hủy' WHERE id = ?", (don_hang_id,))
                if ban_id: cursor.execute("UPDATE ban SET trang_thai = 'Trống' WHERE id = ?", (ban_id,))
            else:
                self._update_order_total(cursor, don_hang_id)
        conn.commit()
        conn.close()

    def _update_order_total(self, cursor, order_id):
        cursor.execute("SELECT COALESCE(SUM(so_luong * don_gia), 0) FROM chi_tiet_don_hang WHERE don_hang_id = ?", (order_id,))
        total = cursor.fetchone()[0]
        cursor.execute("UPDATE don_hang SET tong_tien = ? WHERE id = ?", (total, order_id))

    def update_item_note(self, item_id, note):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE chi_tiet_don_hang SET ghi_chu = ? WHERE id = ?", (note, item_id))
        conn.commit()
        conn.close()
        
    def update_custom_recipe(self, item_id, recipe_str):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE chi_tiet_don_hang SET cong_thuc_tuy_chinh = ? WHERE id = ?", (recipe_str, item_id))
        conn.commit()
        conn.close()

    def cancel_order(self, order_id, table_id=None):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE don_hang SET trang_thai = 'Đã Hủy' WHERE id = ?", (order_id,))
        if table_id: cursor.execute("UPDATE ban SET trang_thai = 'Trống' WHERE id = ?", (table_id,))
        conn.commit()
        conn.close()