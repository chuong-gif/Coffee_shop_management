from src.models.menu_model import MenuModel

class MenuController:
    def __init__(self):
        self.model = MenuModel()

    def get_menu(self):
        return self.model.get_all_drinks()

    def get_drink(self, drink_id):
        return self.model.get_drink_by_id(drink_id)

    def get_recipe(self, drink_id):
        return self.model.get_recipe_by_drink_id(drink_id)

    def get_categories(self):
        return self.model.get_all_categories()

    def get_ingredients(self):
        return self.model.get_ingredients()

    def add_item(self, ten_mon, phan_loai, gia_ban, hinh_anh=None, recipe_data=None):
        if not ten_mon or not phan_loai or not str(gia_ban).isdigit():
            return False
        self.model.add_category_if_missing(phan_loai)
        self.model.add_drink(ten_mon, phan_loai, int(gia_ban), hinh_anh, recipe_data)
        return True

    def update_item(self, drink_id, ten_mon, phan_loai, gia_ban, hinh_anh=None, recipe_data=None):
        if not ten_mon or not phan_loai or not str(gia_ban).isdigit():
            return False
        self.model.add_category_if_missing(phan_loai)
        self.model.update_drink(drink_id, ten_mon, phan_loai, int(gia_ban), hinh_anh, recipe_data=recipe_data)
        return True

    def delete_item(self, drink_id):
        self.model.delete_drink(drink_id)

    def toggle_item_status(self, drink_id, current_status):
        self.model.toggle_status(drink_id, current_status)

    def add_category(self, category_name):
        self.model.add_category(category_name)

    def rename_category(self, old_category, new_category):
        self.model.rename_category(old_category, new_category)

    def delete_category(self, category_name):
        self.model.delete_category(category_name)
