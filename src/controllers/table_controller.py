from src.models.table_model import TableModel

class TableController:
    def __init__(self):
        self.model = TableModel()

    def get_tables(self):
        return self.model.get_all_tables()

    def add_table(self, name):
        if name.strip():
            self.model.add_table(name)
            return True
        return False

    def delete_table(self, table_id):
        self.model.delete_table(table_id)

    def rename_table(self, table_id, new_name):
        if new_name.strip():
            self.model.update_table_name(table_id, new_name)
            return True
        return False

    def set_status(self, table_id, status):
        if status in ["Trống", "Có khách"]:
            self.model.set_table_status(table_id, status)
            return True
        return False
