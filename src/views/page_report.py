import customtkinter as ctk
from src.controllers.report_controller import ReportController
import datetime

class PageReport(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.controller = ReportController()

        self.title = ctk.CTkLabel(self, text="THỐNG KÊ DOANH THU & BÁO CÁO", font=ctk.CTkFont(size=20, weight="bold"))
        self.title.pack(pady=(10, 10))

        range_frame = ctk.CTkFrame(self)
        range_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.entry_from = ctk.CTkEntry(range_frame, placeholder_text="Từ ngày (YYYY-MM-DD)")
        self.entry_from.pack(side="left", padx=5, pady=10, expand=True, fill="x")
        self.entry_to = ctk.CTkEntry(range_frame, placeholder_text="Đến ngày (YYYY-MM-DD)")
        self.entry_to.pack(side="left", padx=5, pady=10, expand=True, fill="x")
        self.btn_load = ctk.CTkButton(range_frame, text="Tải báo cáo", command=self.load_report)
        self.btn_load.pack(side="left", padx=5, pady=10)

        self.summary_frame = ctk.CTkFrame(self)
        self.summary_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.lbl_revenue = ctk.CTkLabel(self.summary_frame, text="Tổng doanh thu: 0 đ", anchor="w")
        self.lbl_revenue.pack(fill="x", padx=10, pady=5)
        self.lbl_orders = ctk.CTkLabel(self.summary_frame, text="Tổng đơn đã thanh toán: 0", anchor="w")
        self.lbl_orders.pack(fill="x", padx=10, pady=5)
        self.lbl_items = ctk.CTkLabel(self.summary_frame, text="Tổng số món bán ra: 0", anchor="w")
        self.lbl_items.pack(fill="x", padx=10, pady=5)
        self.lbl_loss = ctk.CTkLabel(self.summary_frame, text="Tổng hao hụt: 0 đ", anchor="w")
        self.lbl_loss.pack(fill="x", padx=10, pady=5)

        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.top_items_label = ctk.CTkLabel(self.top_frame, text="Top món bán chạy", font=ctk.CTkFont(weight="bold"))
        self.top_items_label.pack(anchor="w", padx=10, pady=(5, 10))
        self.top_items_list = ctk.CTkScrollableFrame(self.top_frame, fg_color="transparent")
        self.top_items_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def load_report(self):
        start_date = self.entry_from.get().strip()
        end_date = self.entry_to.get().strip()
        if not start_date or not end_date:
            today = datetime.date.today().strftime("%Y-%m-%d")
            start_date = start_date or today
            end_date = end_date or today

        report = self.controller.get_sales_summary(start_date, end_date)
        self.lbl_revenue.configure(text=f"Tổng doanh thu: {int(report['total_revenue']):,} đ".replace(",", "."))
        self.lbl_orders.configure(text=f"Tổng đơn đã thanh toán: {report['total_orders']}")
        self.lbl_items.configure(text=f"Tổng số món bán ra: {report['total_items']}")
        self.lbl_loss.configure(text=f"Tổng hao hụt: {int(report['total_loss']):,} đ".replace(",", "."))

        for widget in self.top_items_list.winfo_children():
            widget.destroy()

        top_items = self.controller.get_top_selling_items(start_date, end_date)
        if not top_items:
            ctk.CTkLabel(self.top_items_list, text="Không có dữ liệu bán hàng trong khoảng này.").pack(padx=10, pady=5)
            return

        for name, count in top_items:
            item_row = ctk.CTkFrame(self.top_items_list)
            item_row.pack(fill="x", pady=2)
            ctk.CTkLabel(item_row, text=name, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(item_row, text=f"{count} món", anchor="e").pack(side="right", padx=10)
