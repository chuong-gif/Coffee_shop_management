from src.models.stock_model import StockModel

class StockController:
    def __init__(self):
        self.model = StockModel()

    def get_inventory(self):
        return self.model.get_all_ingredients()

    def get_stock_history(self, limit=20):
        return self.model.get_inventory_history(limit)

    def add_item(self, name, unit, warn_level_str, quantity_str, cost_str):
        if not name or not unit:
            return False, "Tên và đơn vị không được để trống"
        try:
            warn = float(warn_level_str) if warn_level_str else 0.0
            qty = float(quantity_str) if quantity_str else 0.0
            cost = float(cost_str) if cost_str else 0.0
            if qty < 0 or cost < 0 or warn < 0:
                return False, "Các chỉ số không được âm"
            self.model.add_ingredient(name, unit, warn, qty, cost)
            return True, "Thành công"
        except ValueError:
            return False, "Vui lòng nhập số hợp lệ"

    def update_item(self, ing_id, name, unit, warn_level_str):
        if not name or not unit:
            return False, "Tên và đơn vị không được để trống"
        try:
            warn = float(warn_level_str) if warn_level_str else 0.0
            self.model.update_ingredient(ing_id, name, unit, warn)
            return True, "Cập nhật thành công"
        except ValueError:
            return False, "Mức cảnh báo phải là số"

    def delete_item(self, ing_id):
        self.model.delete_ingredient(ing_id)

    def sync_stock(self, ing_id, old_stock, new_stock_str, reason):
        try:
            new_stock = float(new_stock_str)
            diff = new_stock - old_stock
            if diff != 0 and not reason.strip():
                return False, "Kho bị lệch, bắt buộc phải nhập Ghi chú/Lý do!"
            self.model.update_inventory(ing_id, new_stock, diff, reason)
            return True, "Cập nhật thành công"
        except ValueError:
            return False, "Số lượng thực tế phải là số hợp lệ"

    def restock_item(self, ing_id, add_qty, total_cost):
        try:
            qty = float(add_qty)
            cost = float(total_cost) if total_cost else 0.0
            if qty <= 0:
                return False, "Số lượng nhập phải lớn hơn 0"
            self.model.restock_inventory(ing_id, qty, cost)
            return True, "Nhập hàng thành công"
        except ValueError:
            return False, "Số lượng hoặc tiền vốn phải là số hợp lệ"