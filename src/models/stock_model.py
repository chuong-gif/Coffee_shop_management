import sqlite3
import json
from src.config import DB_PATH

class StockModel:
    def __init__(self):
        self.db_path = str(DB_PATH)
        # [HACK NÂNG CẤP DB]: Tự động thêm cột chi_phi để lưu tiền nhập kho
        try:
            conn = self._connect()
            conn.execute("ALTER TABLE lich_su_kiem_kho ADD COLUMN chi_phi REAL DEFAULT 0")
            conn.commit()
            conn.close()
        except Exception:
            pass

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def get_all_ingredients(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, ten_nguyen_lieu, don_vi, ton_ly_thuyet, ton_thuc_te, muc_canh_bao, gia_von FROM kho_nguyen_lieu ORDER BY ten_nguyen_lieu")
        items = cursor.fetchall()
        conn.close()
        return items

    def add_ingredient(self, name, unit, warn_level=0.0, quantity=0.0, total_cost=0.0):
        unit_cost = (total_cost / quantity) if quantity > 0 else 0
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO kho_nguyen_lieu (ten_nguyen_lieu, don_vi, muc_canh_bao, ton_thuc_te, ton_ly_thuyet, gia_von) VALUES (?, ?, ?, ?, ?, ?)",
            (name, unit, warn_level, quantity, quantity, unit_cost),
        )
        ingredient_id = cursor.lastrowid
        # Lưu thẳng chi phí vào lịch sử để Thống kê đọc được
        if quantity > 0 or total_cost > 0:
            cursor.execute(
                "INSERT INTO lich_su_kiem_kho (nguyen_lieu_id, ton_ly_thuyet, ton_thuc_te, so_luong_lech, ly_do, chi_phi) VALUES (?, ?, ?, ?, ?, ?)",
                (ingredient_id, 0, quantity, quantity, 'Khởi tạo nguyên liệu', total_cost),
            )
        conn.commit()
        conn.close()

    def update_ingredient(self, ing_id, name, unit, warn_level):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE kho_nguyen_lieu SET ten_nguyen_lieu = ?, don_vi = ?, muc_canh_bao = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (name, unit, warn_level, ing_id)
        )
        conn.commit()
        conn.close()

    def delete_ingredient(self, ing_id):
        conn = self._connect()
        cursor = conn.cursor()
        # [QUAN TRỌNG]: Phải xóa sạch ở các bảng liên kết để chống lỗi treo DB
        cursor.execute("DELETE FROM cong_thuc WHERE nguyen_lieu_id = ?", (ing_id,))
        cursor.execute("DELETE FROM lich_su_kiem_kho WHERE nguyen_lieu_id = ?", (ing_id,))
        cursor.execute("DELETE FROM kho_nguyen_lieu WHERE id = ?", (ing_id,))
        conn.commit()
        conn.close()

    def update_inventory(self, ing_id, new_stock, diff, reason):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT ton_ly_thuyet FROM kho_nguyen_lieu WHERE id = ?", (ing_id,))
        row = cursor.fetchone()
        ton_ly_thuyet = float(row[0]) if row else 0
        
        cursor.execute("UPDATE kho_nguyen_lieu SET ton_thuc_te = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_stock, ing_id))
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
        cursor.execute("SELECT ton_thuc_te, gia_von FROM kho_nguyen_lieu WHERE id = ?", (ing_id,))
        existing = cursor.fetchone()
        old_qty = float(existing[0]) if existing else 0
        old_cost = float(existing[1]) if existing else 0
        
        # [THUẬT TOÁN]: Tự động trung bình giá vốn mới
        if old_qty <= 0:
            new_avg_cost = total_cost / add_qty if add_qty > 0 else 0
        else:
            new_avg_cost = ((old_qty * old_cost) + total_cost) / (old_qty + add_qty)

        cursor.execute(
            "UPDATE kho_nguyen_lieu SET ton_thuc_te = ton_thuc_te + ?, ton_ly_thuyet = ton_ly_thuyet + ?, gia_von = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (add_qty, add_qty, new_avg_cost, ing_id),
        )
        cursor.execute(
            "INSERT INTO lich_su_kiem_kho (nguyen_lieu_id, ton_ly_thuyet, ton_thuc_te, so_luong_lech, ly_do, chi_phi) VALUES (?, ?, ?, ?, ?, ?)",
            (ing_id, old_qty, old_qty + add_qty, add_qty, 'Nhập thêm hàng', total_cost),
        )
        conn.commit()
        conn.close()

    def deduct_ingredients(self, order_items):
        conn = self._connect()
        cursor = conn.cursor()
        for item in order_items:
            so_luong_mon = float(item["so_luong"])
            custom_recipe_str = item.get("cong_thuc_tuy_chinh")
            
            recipe_to_use = None
            if custom_recipe_str:
                try:
                    recipe_dict = json.loads(custom_recipe_str)
                    recipe_to_use = [(int(k), float(v)) for k, v in recipe_dict.items()]
                except:
                    recipe_to_use = None

            if not recipe_to_use:
                cursor.execute("SELECT nguyen_lieu_id, so_luong_tru FROM cong_thuc WHERE do_uong_id = ?", (item["do_uong_id"],))
                recipe_to_use = cursor.fetchall()

            for nguyen_lieu_id, so_luong_tru in recipe_to_use:
                deduct_qty = float(so_luong_tru) * so_luong_mon
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