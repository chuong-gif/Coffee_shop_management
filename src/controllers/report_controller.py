from src.models.report_model import ReportModel

class ReportController:
    def __init__(self):
        self.model = ReportModel()

    def get_sales_summary(self, start_date, end_date):
        return self.model.get_sales_summary(start_date, end_date)

    def get_top_selling_items(self, start_date, end_date, limit=5):
        return self.model.get_top_selling_items(start_date, end_date, limit)

    def get_revenue_by_date(self, start_date, end_date):
        return self.model.get_revenue_by_date(start_date, end_date)