import datetime
import sqlite3
from src.config import DB_PATH
from src.models.table_model import TableModel
from src.models.stock_model import StockModel

class OrderModel:
    def __init__(self):
        self.db_path = str(DB_PATH)
        self.table_model = TableModel()
        self.stock_model = StockModel()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def create_order(self, table_id=None, loai_don="Tại bàn"):
        order_code = f"DH{int(datetime.datetime.now().timestamp())}"
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO don_hang (ma_don, ban_id, loai_don) VALUES (?, ?, ?)",
            (order_code, table_id, loai_don),
        )
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
            cursor.execute(
                "SELECT id, ma_don, ban_id, loai_don, ghi_chu FROM don_hang WHERE ban_id IS NULL AND trang_thai = 'Mở' ORDER BY id DESC LIMIT 1"
            )
        else:
            cursor.execute(
                "SELECT id, ma_don, ban_id, loai_don, ghi_chu FROM don_hang WHERE ban_id = ? AND trang_thai = 'Mở' ORDER BY id DESC LIMIT 1",
                (table_id,),
            )
        order = cursor.fetchone()
        conn.close()
        return order

    def get_or_create_open_order(self, table_id=None, loai_don="Tại bàn"):
        order = self.get_open_order_by_table(table_id)
        if order:
            return order[0]
        return self.create_order(table_id, loai_don)

    def add_order_item(self, order_id, do_uong_id, quantity=1, ghi_chu=None):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT gia_ban FROM do_uong WHERE id = ?",
            (do_uong_id,),
        )
        row = cursor.fetchone()
        if not row:
            conn.close()
            raise ValueError("Món không tồn tại")

        don_gia = int(row[0])
        if ghi_chu is None or ghi_chu == "":
            cursor.execute(
                "SELECT id, so_luong FROM chi_tiet_don_hang WHERE don_hang_id = ? AND do_uong_id = ? AND (ghi_chu IS NULL OR ghi_chu = '')",
                (order_id, do_uong_id),
            )
            existing = cursor.fetchone()
            if existing:
                item_id, existing_qty = existing
                cursor.execute(
                    "UPDATE chi_tiet_don_hang SET so_luong = ? WHERE id = ?",
                    (existing_qty + quantity, item_id),
                )
            else:
                cursor.execute(
                    "INSERT INTO chi_tiet_don_hang (don_hang_id, do_uong_id, so_luong, don_gia, ghi_chu) VALUES (?, ?, ?, ?, ?)",
                    (order_id, do_uong_id, quantity, don_gia, ghi_chu),
                )
        else:
            cursor.execute(
                "INSERT INTO chi_tiet_don_hang (don_hang_id, do_uong_id, so_luong, don_gia, ghi_chu) VALUES (?, ?, ?, ?, ?)",
                (order_id, do_uong_id, quantity, don_gia, ghi_chu),
            )
        conn.commit()
        conn.close()

    def get_order_items(self, order_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT c.id, c.do_uong_id, d.ten_mon, c.so_luong, c.don_gia, c.ghi_chu, c.so_luong * c.don_gia "
            "FROM chi_tiet_don_hang c "
            "JOIN do_uong d ON c.do_uong_id = d.id "
            "WHERE c.don_hang_id = ?",
            (order_id,),
        )
        items = cursor.fetchall()
        conn.close()
        return items

    def calculate_order_total(self, order_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COALESCE(SUM(so_luong * don_gia), 0) FROM chi_tiet_don_hang WHERE don_hang_id = ?",
            (order_id,),
        )
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
        if tien_khach_dua < total:
            return total, None

        tien_thua = int(tien_khach_dua - total)

        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT ban_id FROM don_hang WHERE id = ?", (order_id,))
        row = cursor.fetchone()
        ban_id = row[0] if row else None

        order_items = self.get_order_items(order_id)
        recipe_items = [
            {"do_uong_id": item[1], "so_luong": item[3]}
            for item in order_items
        ]
        if recipe_items:
            self.stock_model.deduct_ingredients(recipe_items)

        cursor.execute(
            "UPDATE don_hang SET tong_tien = ?, tien_khach_dua = ?, tien_thua = ?, trang_thai = 'Đã Thanh Toán', thoi_gian_thanh_toan = CURRENT_TIMESTAMP WHERE id = ?",
            (total, tien_khach_dua, tien_thua, order_id),
        )
        conn.commit()
        conn.close()

        if ban_id is not None:
            self.table_model.set_table_status(ban_id, "Trống")

        return total, tien_thua

    def move_order(self, source_table_id, target_table_id):
        if source_table_id == target_table_id:
            return False

        source_order = self.get_open_order_by_table(source_table_id)
        if not source_order:
            return False

        target_order = self.get_open_order_by_table(target_table_id)
        if target_order:
            return self.merge_orders(source_order, target_order, source_table_id, target_table_id)

        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE don_hang SET ban_id = ? WHERE id = ?",
            (target_table_id, source_order[0]),
        )
        conn.commit()
        conn.close()

        self.table_model.set_table_status(source_table_id, "Trống")
        self.table_model.set_table_status(target_table_id, "Có khách")
        return source_order[0]

    def merge_orders(self, source_order, target_order, source_table_id, target_table_id):
        if source_table_id == target_table_id:
            return False

        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE chi_tiet_don_hang SET don_hang_id = ? WHERE don_hang_id = ?",
            (target_order[0], source_order[0]),
        )

        target_note = target_order[4] or ""
        source_note = source_order[4] or ""
        merged_note = target_note
        if source_note:
            if merged_note:
                merged_note = f"{merged_note}\n{source_note}"
            else:
                merged_note = source_note

        if merged_note:
            cursor.execute(
                "UPDATE don_hang SET ghi_chu = ? WHERE id = ?",
                (merged_note, target_order[0]),
            )

        cursor.execute("DELETE FROM don_hang WHERE id = ?", (source_order[0],))
        conn.commit()
        conn.close()

        self.table_model.set_table_status(source_table_id, "Trống")
        self.table_model.set_table_status(target_table_id, "Có khách")
        return target_order[0]
