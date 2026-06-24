# Truy vấn nhập kho, tính tồn lý thuyết, lưu lịch sử kiểm kho

import sqlite3
from src.config import DB_PATH

class StockModel:
    def __init__(self):
        self.db_path = str(DB_PATH)

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def get_all_ingredients(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, ten_nguyen_lieu, don_vi, ton_ly_thuyet, ton_thuc_te, muc_canh_bao, gia_von FROM kho_nguyen_lieu"
        )
        items = cursor.fetchall()
        conn.close()
        return items

    def add_ingredient(self, name, unit, quantity=0.0, cost=0.0, note=None):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO kho_nguyen_lieu (ten_nguyen_lieu, don_vi, muc_canh_bao, ton_thuc_te, ton_ly_thuyet, gia_von) VALUES (?, ?, ?, ?, ?, ?)",
            (name, unit, 0, quantity, quantity, cost),
        )
        ingredient_id = cursor.lastrowid
        if quantity > 0:
            cursor.execute(
                "INSERT INTO lich_su_kiem_kho (nguyen_lieu_id, ton_ly_thuyet, ton_thuc_te, so_luong_lech, ly_do) VALUES (?, ?, ?, ?, ?)",
                (ingredient_id, quantity, quantity, 0, note),
            )
        conn.commit()
        conn.close()

    def update_inventory(self, ing_id, new_stock, diff, reason):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT ton_ly_thuyet FROM kho_nguyen_lieu WHERE id = ?", (ing_id,))
        row = cursor.fetchone()
        ton_ly_thuyet = float(row[0]) if row else 0
        cursor.execute(
            "UPDATE kho_nguyen_lieu SET ton_thuc_te = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_stock, ing_id),
        )
        if diff != 0:
            cursor.execute(
                "INSERT INTO lich_su_kiem_kho (nguyen_lieu_id, ton_ly_thuyet, ton_thuc_te, so_luong_lech, ly_do) VALUES (?, ?, ?, ?, ?)",
                (ing_id, ton_ly_thuyet, new_stock, diff, reason),
            )
        conn.commit()
        conn.close()

    def restock_inventory(self, ing_id, add_qty, total_cost):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT gia_von FROM kho_nguyen_lieu WHERE id = ?", (ing_id,))
        existing = cursor.fetchone()
        existing_cost = float(existing[0]) if existing and existing[0] else 0
        average_cost = total_cost if total_cost and total_cost > 0 else existing_cost
        cursor.execute(
            "UPDATE kho_nguyen_lieu SET ton_thuc_te = ton_thuc_te + ?, ton_ly_thuyet = ton_ly_thuyet + ?, gia_von = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (add_qty, add_qty, average_cost, ing_id),
        )
        conn.commit()
        conn.close()

    def deduct_ingredients(self, order_items):
        conn = self._connect()
        cursor = conn.cursor()
        for item in order_items:
            cursor.execute(
                "SELECT nguyen_lieu_id, so_luong_tru FROM cong_thuc WHERE do_uong_id = ?",
                (item["do_uong_id"],),
            )
            recipe = cursor.fetchall()
            for nguyen_lieu_id, so_luong_tru in recipe:
                deduct_qty = float(so_luong_tru) * float(item["so_luong"])
                cursor.execute(
                    "UPDATE kho_nguyen_lieu SET ton_ly_thuyet = ton_ly_thuyet - ? WHERE id = ?",
                    (deduct_qty, nguyen_lieu_id),
                )
        conn.commit()
        conn.close()

    def get_inventory_history(self, limit=20):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT l.id, k.ten_nguyen_lieu, l.ton_ly_thuyet, l.ton_thuc_te, l.so_luong_lech, l.ly_do, l.thoi_gian_kiem_kho "
            "FROM lich_su_kiem_kho l "
            "LEFT JOIN kho_nguyen_lieu k ON l.nguyen_lieu_id = k.id "
            "ORDER BY l.thoi_gian_kiem_kho DESC LIMIT ?",
            (limit,),
        )
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_loss_report(self, start_date, end_date):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT SUM(ABS(l.so_luong_lech) * COALESCE(k.gia_von, 0)), SUM(ABS(l.so_luong_lech)) "
            "FROM lich_su_kiem_kho l "
            "LEFT JOIN kho_nguyen_lieu k ON l.nguyen_lieu_id = k.id "
            "WHERE date(l.thoi_gian_kiem_kho) BETWEEN ? AND ?",
            (start_date, end_date),
        )
        result = cursor.fetchone()
        conn.close()
        return result if result else (0, 0)
