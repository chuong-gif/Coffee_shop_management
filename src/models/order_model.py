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

    # ==========================================
    # LOGIC KẾ TOÁN DỒN TÍCH (TÍNH GIÁ VỐN)
    # ==========================================
    def _calculate_cogs(self, cursor, do_uong_id):
        """Tính giá vốn của 1 ly đồ uống dựa trên định mức công thức chuẩn và giá trị kho hiện tại"""
        cursor.execute("""
            SELECT ct.so_luong_tru, k.gia_von 
            FROM cong_thuc ct
            JOIN kho_nguyen_lieu k ON ct.nguyen_lieu_id = k.id
            WHERE ct.do_uong_id = ?
        """, (do_uong_id,))
        ingredients = cursor.fetchall()
        
        cogs = 0
        for qty, unit_cost in ingredients:
            cogs += (qty * unit_cost)
            
        return int(cogs)

    # ==========================================
    # CÁC THAO TÁC ĐƠN HÀNG
    # ==========================================
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
        
        # 1. Lấy giá bán
        cursor.execute("SELECT gia_ban FROM do_uong WHERE id = ?", (do_uong_id,))
        row = cursor.fetchone()
        if not row: return
        don_gia = int(row[0])

        # 2. Tính giá vốn của món này tại khoảnh khắc hiện tại
        gia_von_1_ly = self._calculate_cogs(cursor, do_uong_id)

        # 3. Lưu vào DB kèm theo Giá vốn (Để báo cáo Lãi/Lỗ sau này không bị sai lệch)
        if not ghi_chu:
            cursor.execute("SELECT id, so_luong FROM chi_tiet_don_hang WHERE don_hang_id = ? AND do_uong_id = ? AND (ghi_chu IS NULL OR ghi_chu = '') AND cong_thuc_tuy_chinh IS NULL", (order_id, do_uong_id))
            existing = cursor.fetchone()
            if existing:
                item_id, existing_qty = existing
                cursor.execute("UPDATE chi_tiet_don_hang SET so_luong = ? WHERE id = ?", (existing_qty + quantity, item_id))
            else:
                cursor.execute("INSERT INTO chi_tiet_don_hang (don_hang_id, do_uong_id, so_luong, don_gia, gia_von, ghi_chu) VALUES (?, ?, ?, ?, ?, ?)", (order_id, do_uong_id, quantity, don_gia, gia_von_1_ly, ghi_chu))
        else:
            cursor.execute("INSERT INTO chi_tiet_don_hang (don_hang_id, do_uong_id, so_luong, don_gia, gia_von, ghi_chu) VALUES (?, ?, ?, ?, ?, ?)", (order_id, do_uong_id, quantity, don_gia, gia_von_1_ly, ghi_chu))
        
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

    def close_order(self, order_id, tien_khach_dua, tien_giam_gia=0, ma_giam_gia=None):
        total_goc = self.calculate_order_total(order_id)
        final_total = total_goc - tien_giam_gia # Trừ tiền giảm giá để ra tổng cuối

        # So sánh tiền khách đưa với tổng cuối (thay vì tổng gốc)
        if tien_khach_dua < final_total: return final_total, None
        tien_thua = int(tien_khach_dua - final_total)

        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT ban_id FROM don_hang WHERE id = ?", (order_id,))
        row = cursor.fetchone()
        ban_id = row[0] if row else None

        order_items = self.get_order_items(order_id)
        recipe_items = [{"do_uong_id": item[1], "so_luong": item[3], "cong_thuc_tuy_chinh": item[7]} for item in order_items]
        
        if recipe_items:
            self.stock_model.deduct_ingredients(recipe_items)

        # Cập nhật thông tin thanh toán (Giữ ngày cũ nếu có)
        cursor.execute("""
            UPDATE don_hang 
            SET tong_tien = ?, 
                tien_giam_gia = ?,
                ma_giam_gia_ap_dung = ?,
                tien_khach_dua = ?, 
                tien_thua = ?, 
                trang_thai = 'Đã Thanh Toán', 
                thoi_gian_thanh_toan = COALESCE(thoi_gian_thanh_toan, CURRENT_TIMESTAMP)
            WHERE id = ?
        """, (final_total, tien_giam_gia, ma_giam_gia, tien_khach_dua, tien_thua, order_id))
        
        conn.commit()
        conn.close()

        if ban_id is not None:
            self.table_model.set_table_status(ban_id, "Trống")
            
        return final_total, tien_thua

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
        
        # [CẬP NHẬT KẾ TOÁN]: Tính lại giá vốn nếu khách hàng thay đổi định lượng nguyên liệu
        cogs = 0
        if recipe_str:
            try:
                recipe_dict = json.loads(recipe_str)
                for nl_id, qty in recipe_dict.items():
                    cursor.execute("SELECT gia_von FROM kho_nguyen_lieu WHERE id = ?", (nl_id,))
                    row = cursor.fetchone()
                    if row:
                        cogs += float(qty) * float(row[0])
            except:
                pass
        else:
            # Nếu khách reset về công thức gốc, tính lại giá vốn gốc
            cursor.execute("SELECT do_uong_id FROM chi_tiet_don_hang WHERE id = ?", (item_id,))
            do_uong_row = cursor.fetchone()
            if do_uong_row:
                cogs = self._calculate_cogs(cursor, do_uong_row[0])

        cursor.execute("UPDATE chi_tiet_don_hang SET cong_thuc_tuy_chinh = ?, gia_von = ? WHERE id = ?", (recipe_str, int(cogs), item_id))
        conn.commit()
        conn.close()

    def cancel_order(self, order_id, table_id=None):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE don_hang SET trang_thai = 'Đã Hủy' WHERE id = ?", (order_id,))
        if table_id: cursor.execute("UPDATE ban SET trang_thai = 'Trống' WHERE id = ?", (table_id,))
        conn.commit()
        conn.close()

    # ==========================================
    # QUẢN LÝ MẪU HÓA ĐƠN
    # ==========================================
    def get_receipt_template(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mau_hoa_don (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                ten_quan TEXT,
                dia_chi TEXT,
                dien_thoai TEXT,
                loi_cam_on TEXT
            )
        """)
        cursor.execute("SELECT ten_quan, dia_chi, dien_thoai, loi_cam_on FROM mau_hoa_don WHERE id = 1")
        row = cursor.fetchone()
        
        if not row:
            cursor.execute("INSERT INTO mau_hoa_don (id, ten_quan, dia_chi, dien_thoai, loi_cam_on) VALUES (1, 'COFFEE SHOP OFFLINE', '123 Thôn Phi Có, Đam Rông 3', 'Hotline: 0123 456 789', 'Xin chân thành cảm ơn và hẹn gặp lại quý khách!')")
            conn.commit()
            row = ('COFFEE SHOP OFFLINE', '123 Thôn Phi Có, Đam Rông 3', 'Hotline: 0123 456 789', 'Xin chân thành cảm ơn và hẹn gặp lại quý khách!')
        conn.close()
        
        return {"ten_quan": row[0], "dia_chi": row[1], "dien_thoai": row[2], "loi_cam_on": row[3]}

    def save_receipt_template(self, ten_quan, dia_chi, dien_thoai, loi_cam_on):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE mau_hoa_don 
            SET ten_quan = ?, dia_chi = ?, dien_thoai = ?, loi_cam_on = ? 
            WHERE id = 1
        """, (ten_quan, dia_chi, dien_thoai, loi_cam_on))
        conn.commit()
        conn.close()
    
   # ==========================================
    # TÍNH NĂNG 2: LỊCH SỬ HÓA ĐƠN & KẾ TOÁN (ĐÃ FIX MÚI GIỜ)
    # ==========================================
    def get_history_orders(self, start_date, end_date):
        conn = self._connect()
        cursor = conn.cursor()
        # Dùng localtime để chuyển giờ UTC sang giờ Việt Nam
        query = """
            SELECT id, ma_don, loai_don, tong_tien, trang_thai, datetime(thoi_gian_thanh_toan, 'localtime') as local_time
            FROM don_hang
            WHERE datetime(thoi_gian_thanh_toan, 'localtime') >= ? 
              AND datetime(thoi_gian_thanh_toan, 'localtime') <= ?
              AND trang_thai IN ('Đã Thanh Toán', 'Đã Hủy')
            ORDER BY local_time DESC
        """
        cursor.execute(query, (f"{start_date} 00:00:00", f"{end_date} 23:59:59"))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_order_summary(self, order_id):
        conn = self._connect()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        # Lấy thêm trường local_time
        cursor.execute("SELECT *, datetime(thoi_gian_thanh_toan, 'localtime') as local_time FROM don_hang WHERE id=?", (order_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def void_paid_order(self, order_id):
        """Hủy hóa đơn đã thanh toán: Trả lại kho và Xóa doanh thu"""
        conn = self._connect()
        cursor = conn.cursor()
        
        # [BẢO MẬT KẾ TOÁN]: Chỉ cho phép hoàn kho nếu đơn đang thực sự ở trạng thái 'Đã Thanh Toán'
        # Tránh trường hợp user click đúp hoặc lỗi mạng gọi hàm 2 lần làm kho tăng gấp đôi
        cursor.execute("SELECT trang_thai FROM don_hang WHERE id=?", (order_id,))
        row = cursor.fetchone()
        if not row or row[0] != 'Đã Thanh Toán':
            conn.close()
            return False
            
        # 1. Lấy chi tiết món để hoàn kho
        cursor.execute("SELECT do_uong_id, so_luong, cong_thuc_tuy_chinh FROM chi_tiet_don_hang WHERE don_hang_id=?", (order_id,))
        items = cursor.fetchall()
        
        for item in items:
            do_uong_id, so_luong, custom_recipe = item
            recipe_to_restore = {}
            
            if custom_recipe:
                try: recipe_to_restore = json.loads(custom_recipe)
                except: pass
            
            if not recipe_to_restore:
                cursor.execute("SELECT nguyen_lieu_id, so_luong_tru FROM cong_thuc WHERE do_uong_id=?", (do_uong_id,))
                for nl_id, qty in cursor.fetchall():
                    recipe_to_restore[str(nl_id)] = qty
            
            # [FIX LỖI KHO]: CHỈ cộng trả lại nguyên liệu cho TỒN LÝ THUYẾT.
            # TUYỆT ĐỐI KHÔNG đụng vào Tồn Thực Tế.
            for nl_id, qty_per_drink in recipe_to_restore.items():
                total_to_add = float(qty_per_drink) * so_luong
                cursor.execute("""
                    UPDATE kho_nguyen_lieu 
                    SET ton_ly_thuyet = ton_ly_thuyet + ? 
                    WHERE id = ?
                """, (total_to_add, int(nl_id)))
        
        # 2. Cập nhật trạng thái đơn thành 'Đã Hủy'
        cursor.execute("UPDATE don_hang SET trang_thai='Đã Hủy' WHERE id=?", (order_id,))
        conn.commit()
        conn.close()
        return True

    def reopen_order(self, order_id):
        conn = self._connect()
        cursor = conn.cursor()
        
        # [BẢO MẬT KẾ TOÁN]: Tương tự, chỉ mở lại nếu đơn đang Đã Thanh Toán
        cursor.execute("SELECT trang_thai FROM don_hang WHERE id=?", (order_id,))
        row = cursor.fetchone()
        if not row or row[0] != 'Đã Thanh Toán':
            conn.close()
            return False
            
        # 1. Tự động hoàn lại nguyên liệu vào kho
        cursor.execute("SELECT do_uong_id, so_luong, cong_thuc_tuy_chinh FROM chi_tiet_don_hang WHERE don_hang_id=?", (order_id,))
        items = cursor.fetchall()
        
        for item in items:
            do_uong_id, so_luong, custom_recipe = item
            recipe_to_restore = {}
            if custom_recipe:
                try: recipe_to_restore = json.loads(custom_recipe)
                except: pass
            if not recipe_to_restore:
                cursor.execute("SELECT nguyen_lieu_id, so_luong_tru FROM cong_thuc WHERE do_uong_id=?", (do_uong_id,))
                for nl_id, qty in cursor.fetchall(): recipe_to_restore[str(nl_id)] = qty
                
           # [FIX LỖI KHO]: CHỈ cộng trả lại nguyên liệu cho TỒN LÝ THUYẾT.
            # TUYỆT ĐỐI KHÔNG đụng vào Tồn Thực Tế.
            for nl_id, qty_per_drink in recipe_to_restore.items():
                total_to_add = float(qty_per_drink) * so_luong
                cursor.execute("""
                    UPDATE kho_nguyen_lieu 
                    SET ton_ly_thuyet = ton_ly_thuyet + ? 
                    WHERE id = ?
                """, (total_to_add, int(nl_id)))
        
        # 2. Kiểm tra thông minh: Tránh kẹt Bàn
        cursor.execute("SELECT ban_id FROM don_hang WHERE id=?", (order_id,))
        ban_row = cursor.fetchone()
        ban_id = ban_row[0] if ban_row else None
        
        if ban_id:
            cursor.execute("SELECT trang_thai FROM ban WHERE id=?", (ban_id,))
            trang_thai_ban = cursor.fetchone()[0]
            if trang_thai_ban == 'Có khách':
                cursor.execute("UPDATE don_hang SET ban_id=NULL, loai_don='Mang về' WHERE id=?", (order_id,))
            else:
                cursor.execute("UPDATE ban SET trang_thai='Có khách' WHERE id=?", (ban_id,))

        # 3. Đưa đơn về trạng thái Mở
        cursor.execute("""
            UPDATE don_hang 
            SET trang_thai='Mở', tien_khach_dua=0, tien_thua=0, tien_giam_gia=0, ma_giam_gia_ap_dung=NULL
            WHERE id=?
        """, (order_id,))
        
        conn.commit()
        conn.close()
        return True