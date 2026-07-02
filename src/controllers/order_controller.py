from src.models.table_model import TableModel
from src.models.order_model import OrderModel
from src.models.menu_model import MenuModel

class OrderController:
    def __init__(self):
        self.table_model = TableModel()
        self.order_model = OrderModel()
        self.menu_model = MenuModel()

    def get_tables_data(self):
        return self.table_model.get_all_tables()

    def open_table_order(self, table_id, ten_ban):
        order_id = self.order_model.get_or_create_open_order(table_id=table_id, loai_don="Tại bàn")
        note = self.order_model.get_order_note_by_order_id(order_id)
        return {
            "table_id": table_id,
            "ten_ban": ten_ban,
            "order_id": order_id,
            "order_items": self.order_model.get_order_items(order_id),
            "order_total": self.order_model.calculate_order_total(order_id),
            "order_note": note,
            "menu": self.menu_model.get_available_menu(),
        }

    def add_new_table(self, ten_ban):
        if ten_ban.strip() != "":
            self.table_model.add_table(ten_ban)
            return True
        return False

    def delete_table(self, table_id):
        self.table_model.delete_table(table_id)

    def rename_table(self, table_id, new_name):
        if new_name.strip() != "":
            self.table_model.update_table_name(table_id, new_name.strip())
            return True
        return False

    def handle_table_click(self, table_id, ten_ban):
        order = self.order_model.get_open_order_by_table(table_id)
        order_id = order[0] if order else None
        note = self.order_model.get_order_note_by_order_id(order_id) if order_id else None
        return {
            "table_id": table_id,
            "ten_ban": ten_ban,
            "order_id": order_id,
            "order_items": self.order_model.get_order_items(order_id) if order_id else [],
            "order_total": self.order_model.calculate_order_total(order_id) if order_id else 0,
            "order_note": note,
            "menu": self.menu_model.get_available_menu(),
        }

    # [FIX #1]: Chỉ TÌM đơn Mang Về đang mở (nếu có), KHÔNG tạo mới ngay.
    # Đơn thật sự chỉ được tạo trong create_takeaway_order() khi món đầu tiên được thêm.
    def get_takeaway_pane_data(self):
        order = self.order_model.get_open_order_by_table(None)
        order_id = order[0] if order else None
        note = self.order_model.get_order_note_by_order_id(order_id) if order_id else None
        return {
            "table_id": None,
            "ten_ban": "Đơn Mang Về",
            "order_id": order_id,
            "order_items": self.order_model.get_order_items(order_id) if order_id else [],
            "order_total": self.order_model.calculate_order_total(order_id) if order_id else 0,
            "order_note": note,
            "menu": self.menu_model.get_available_menu(),
        }

    def create_takeaway_order(self):
        order_id = self.order_model.get_or_create_open_order(table_id=None, loai_don="Mang về")
        note = self.order_model.get_order_note_by_order_id(order_id)
        return {
            "table_id": None,
            "ten_ban": "Đơn Mang Về",
            "order_id": order_id,
            "order_items": self.order_model.get_order_items(order_id),
            "order_total": self.order_model.calculate_order_total(order_id),
            "order_note": note,
            "menu": self.menu_model.get_available_menu(),
        }

    def get_order_items(self, order_id):
        return self.order_model.get_order_items(order_id) if order_id else []

    def get_order_total(self, order_id):
        return self.order_model.calculate_order_total(order_id) if order_id else 0

    def add_item_to_order(self, table_id, do_uong_id, order_id=None, quantity=1, ghi_chu=None, loai_don="Tại bàn"):
        if order_id is None:
            order_id = self.order_model.get_or_create_open_order(table_id=table_id, loai_don=loai_don)
        self.order_model.add_order_item(order_id, do_uong_id, quantity, ghi_chu)
        return {
            "order_items": self.order_model.get_order_items(order_id),
            "order_total": self.order_model.calculate_order_total(order_id),
            "order_id": order_id,
        }

    def save_order_note(self, order_id, ghi_chu):
        self.order_model.update_order_note(order_id, ghi_chu)

    # [FIX CỐT LÕI]: Truyền trực tiếp order_id xuống để khỏi phải tìm kiếm mông lung
    def move_order_to_table(self, order_id, source_table_id, target_table_name):
        target_table = self.table_model.get_table_by_name(target_table_name)
        if not target_table:
            return False, "Không tìm thấy bàn đích.", None
        
        target_table_id = target_table[0]
        if source_table_id == target_table_id:
            return False, "Bàn nguồn và bàn đích trùng nhau.", None

        new_order_id = self.order_model.move_order(order_id, source_table_id, target_table_id)
        if new_order_id:
            return True, "Chuyển bàn/thực hiện gộp đơn thành công.", new_order_id
        return False, "Lỗi cơ sở dữ liệu khi chuyển đơn.", None

    def close_order(self, order_id, tien_khach_dua):
        return self.order_model.close_order(order_id, tien_khach_dua)
        
    def update_item_qty(self, item_id, new_qty):
        if new_qty <= 0:
            self.order_model.remove_order_item(item_id)
        else:
            self.order_model.update_item_quantity(item_id, new_qty)

    def update_item_note(self, item_id, note):
        self.order_model.update_item_note(item_id, note)

    def cancel_order(self, order_id, table_id):
        self.order_model.cancel_order(order_id, table_id)

    # === BỔ SUNG CHO TÍNH NĂNG CÔNG THỨC TÙY CHỈNH ===
    def get_ingredients(self):
        return self.menu_model.get_ingredients()

    def get_drink_base_recipe(self, do_uong_id):
        return self.menu_model.get_recipe_by_drink_id(do_uong_id)

    def save_custom_recipe(self, item_id, recipe_dict):
        import json
        recipe_str = json.dumps(recipe_dict) if recipe_dict else None
        self.order_model.update_custom_recipe(item_id, recipe_str)

    def get_receipt_template(self):
        return self.order_model.get_receipt_template()

    def save_receipt_template(self, template_data):
        self.order_model.save_receipt_template(
            template_data.get('ten_quan', ''),
            template_data.get('dia_chi', ''),
            template_data.get('dien_thoai', ''),
            template_data.get('loi_cam_on', '')
        )
        return True, "Cập nhật mẫu hóa đơn thành công!"