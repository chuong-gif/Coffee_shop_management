from src.models.stock_model import StockModel

class StockController:
    def __init__(self):
        self.model = StockModel()

    def get_inventory(self):
        return self.model.get_all_ingredients()

    def get_stock_history(self, limit=20):
        return self.model.get_inventory_history(limit)

    def add_item(self, name, quantity, unit, cost, note):
        if not name or not unit:
            return False, "Tên và đơn vị không được để trống"
        try:
            qty = float(quantity) if quantity else 0.0
            if qty < 0:
                return False, "Số lượng không được âm"
        except ValueError:
            return False, "Số lượng phải là số hợp lệ"
        try:
            gia = float(cost) if cost else 0.0
            if gia < 0:
                return False, "Giá vốn không được âm"
        except ValueError:
            return False, "Giá vốn phải là số hợp lệ"
        self.model.add_ingredient(name, unit, qty, gia, note)
        return True, "Thành công"

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