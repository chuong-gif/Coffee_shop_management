# Truy vấn thêm/sửa/xóa đồ uống, bật/tắt trạng thái món
import sqlite3
import time
from src.config import DB_PATH
from src.models.stock_model import StockModel

class MenuModel:
    def __init__(self):
        self.db_path = str(DB_PATH)
        self.stock_model = StockModel()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _generate_item_code(self, ten_mon):
        base = ''.join(ch for ch in ten_mon.upper() if ch.isalnum())[:6]
        return f"{base}_{int(time.time()) % 10000}"

    def get_all_drinks(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, ma_mon, ten_mon, phan_loai, gia_ban, con_hang, hinh_anh FROM do_uong ORDER BY phan_loai, ten_mon"
        )
        drinks = cursor.fetchall()
        conn.close()
        return drinks

    def get_available_menu(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, ma_mon, ten_mon, phan_loai, gia_ban, con_hang, hinh_anh FROM do_uong WHERE con_hang = 1 ORDER BY phan_loai, ten_mon"
        )
        drinks = cursor.fetchall()
        conn.close()
        return drinks

    def get_menu_categories(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT ten_danh_muc FROM danh_muc UNION SELECT DISTINCT phan_loai FROM do_uong WHERE phan_loai IS NOT NULL ORDER BY 1"
        )
        categories = [row[0] for row in cursor.fetchall() if row[0]]
        conn.close()
        return categories

    def get_all_categories(self):
        return self.get_menu_categories()

    def add_category_if_missing(self, category_name):
        if not category_name or not category_name.strip():
            return
        self.add_category(category_name)

    def get_ingredients(self):
        return self.stock_model.get_all_ingredients()

    def add_category(self, category_name):
        if not category_name.strip():
            return
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO danh_muc (ten_danh_muc) VALUES (?)",
            (category_name.strip(),),
        )
        conn.commit()
        conn.close()

    def rename_category(self, old_category, new_category):
        if not old_category or not new_category.strip():
            return
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE danh_muc SET ten_danh_muc = ? WHERE ten_danh_muc = ?",
            (new_category.strip(), old_category),
        )
        cursor.execute(
            "UPDATE do_uong SET phan_loai = ? WHERE phan_loai = ?",
            (new_category.strip(), old_category),
        )
        conn.commit()
        conn.close()

    def delete_category(self, category):
        if not category:
            return
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM danh_muc WHERE ten_danh_muc = ?", (category,))
        cursor.execute("UPDATE do_uong SET phan_loai = 'Khác' WHERE phan_loai = ?", (category,))
        conn.commit()
        conn.close()

    def get_drink_by_id(self, drink_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, ma_mon, ten_mon, phan_loai, gia_ban, con_hang, hinh_anh FROM do_uong WHERE id = ?",
            (drink_id,),
        )
        drink = cursor.fetchone()
        conn.close()
        return drink

    def get_recipe_by_drink_id(self, drink_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT nguyen_lieu_id, so_luong_tru FROM cong_thuc WHERE do_uong_id = ?",
            (drink_id,),
        )
        recipe = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        return recipe

    def add_drink(self, ten_mon, phan_loai, gia_ban, hinh_anh=None, recipe=None, ma_mon=None):
        ma_mon = ma_mon or self._generate_item_code(ten_mon)
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO do_uong (ma_mon, ten_mon, phan_loai, gia_ban, hinh_anh, con_hang) VALUES (?, ?, ?, ?, ?, 1)",
            (ma_mon, ten_mon, phan_loai, gia_ban, hinh_anh),
        )
        drink_id = cursor.lastrowid
        if recipe:
            self.save_recipe(drink_id, recipe, cursor)
        conn.commit()
        conn.close()
        return drink_id

    def update_drink(self, drink_id, ten_mon, phan_loai, gia_ban, hinh_anh=None, con_hang=1, recipe=None):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE do_uong SET ten_mon = ?, phan_loai = ?, gia_ban = ?, hinh_anh = ?, con_hang = ? WHERE id = ?",
            (ten_mon, phan_loai, gia_ban, hinh_anh, con_hang, drink_id),
        )
        if recipe is not None:
            self.save_recipe(drink_id, recipe, cursor)
        conn.commit()
        conn.close()

    def delete_drink(self, drink_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cong_thuc WHERE do_uong_id = ?", (drink_id,))
        cursor.execute("DELETE FROM do_uong WHERE id = ?", (drink_id,))
        conn.commit()
        conn.close()

    def toggle_status(self, drink_id, current_status):
        new_status = 0 if current_status == 1 else 1
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE do_uong SET con_hang = ? WHERE id = ?", (new_status, drink_id))
        conn.commit()
        conn.close()

    def save_recipe(self, drink_id, recipe, cursor=None):
        close_conn = cursor is None
        if close_conn:
            conn = self._connect()
            cursor = conn.cursor()
        cursor.execute("DELETE FROM cong_thuc WHERE do_uong_id = ?", (drink_id,))
        for ingredient_id, quantity in recipe.items():
            try:
                amount = float(quantity)
            except (TypeError, ValueError):
                continue
            if amount > 0:
                cursor.execute(
                    "INSERT INTO cong_thuc (do_uong_id, nguyen_lieu_id, so_luong_tru) VALUES (?, ?, ?)",
                    (drink_id, ingredient_id, amount),
                )
        if close_conn:
            conn.commit()
            conn.close()