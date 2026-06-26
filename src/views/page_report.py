import customtkinter as ctk
import tkinter as tk
from src.controllers.report_controller import ReportController
import datetime
from dateutil.relativedelta import relativedelta
from tkcalendar import DateEntry  # Thêm thư viện Lịch

class PageReport(ctk.CTkFrame):
    def __init__(self, master):
        # Đổi nền chính sang màu đen nhạt
        super().__init__(master, corner_radius=0, fg_color="#121212") 
        self.controller = ReportController()

        # Định nghĩa các màu chuẩn cho Dark Theme
        self.card_bg = "#212121"
        self.border_color = "#333333"
        self.text_main = "white"
        self.text_sub = "#AAAAAA"

        # ==========================================
        # 1. BỘ LỌC THỜI GIAN (TOP BAR)
        # ==========================================
        self.filter_card = ctk.CTkFrame(self, fg_color=self.card_bg, corner_radius=8, border_width=1, border_color=self.border_color)
        self.filter_card.pack(fill="x", padx=20, pady=(20, 10))

        # Nhóm Title bên trái
        title_group = ctk.CTkFrame(self.filter_card, fg_color="transparent")
        title_group.pack(side="left", padx=20, pady=15)
        ctk.CTkLabel(title_group, text="LỌC THỜI GIAN DOANH THU & THEO DÕI HAO HỤT", font=ctk.CTkFont(size=14, weight="bold"), text_color=self.text_main).pack(anchor="w")
        ctk.CTkLabel(title_group, text="Chọn thời điểm từ ngày đến ngày để tra cứu chi tiết.", font=ctk.CTkFont(size=12), text_color=self.text_sub).pack(anchor="w")

        # Nhóm input Date & Buttons bên phải
        action_group = ctk.CTkFrame(self.filter_card, fg_color="transparent")
        action_group.pack(side="right", padx=20, pady=15)

        # CỤM LỊCH (DATE PICKER)
        date_input_group = ctk.CTkFrame(action_group, fg_color="transparent")
        date_input_group.pack(side="left", padx=10)
        
        ctk.CTkLabel(date_input_group, text="TỪ NGÀY:", font=ctk.CTkFont(size=10, weight="bold"), text_color=self.text_sub).grid(row=0, column=0, sticky="w", padx=2)
        ctk.CTkLabel(date_input_group, text="ĐẾN NGÀY:", font=ctk.CTkFont(size=10, weight="bold"), text_color=self.text_sub).grid(row=0, column=1, sticky="w", padx=2)
        
        # Thay thế Entry bằng DateEntry
        self.entry_from = DateEntry(date_input_group, width=12, background='#2980B9', foreground='white', borderwidth=0, date_pattern='y-mm-dd', font=('Arial', 11))
        self.entry_from.grid(row=1, column=0, padx=2, pady=2, ipady=3)
        
        self.entry_to = DateEntry(date_input_group, width=12, background='#2980B9', foreground='white', borderwidth=0, date_pattern='y-mm-dd', font=('Arial', 11))
        self.entry_to.grid(row=1, column=1, padx=2, pady=2, ipady=3)

        # Quick Filters
        btn_group = ctk.CTkFrame(action_group, fg_color="transparent")
        btn_group.pack(side="left", padx=10)
        ctk.CTkLabel(btn_group, text="PHẠM VI NHANH:", font=ctk.CTkFont(size=10, weight="bold"), text_color=self.text_sub).pack(anchor="w", padx=2)
        
        btn_row = ctk.CTkFrame(btn_group, fg_color="transparent")
        btn_row.pack(fill="x")
        ctk.CTkButton(btn_row, text="Hôm nay", width=60, fg_color="#333333", text_color="white", hover_color="#444444", command=lambda: self.set_quick_date("today")).pack(side="left", padx=2)
        ctk.CTkButton(btn_row, text="7 ngày qua", width=70, fg_color="#E67E22", text_color="white", hover_color="#D35400", command=lambda: self.set_quick_date("7days")).pack(side="left", padx=2)
        ctk.CTkButton(btn_row, text="Tháng này", width=70, fg_color="#333333", text_color="white", hover_color="#444444", command=lambda: self.set_quick_date("month")).pack(side="left", padx=2)
        
        ctk.CTkButton(action_group, text="Lọc", width=50, fg_color="#2980B9", command=self.load_report).pack(side="left", padx=(10,0), pady=(15,0))

        # ==========================================
        # 2. BỐN THẺ KPI (KPI CARDS)
        # ==========================================
        self.kpi_container = ctk.CTkFrame(self, fg_color="transparent")
        self.kpi_container.pack(fill="x", padx=15, pady=5)
        
        self.val_revenue = ctk.StringVar(value="0 đ")
        self.val_orders = ctk.StringVar(value="0 đơn")
        self.val_avg = ctk.StringVar(value="0 đ")
        self.val_loss = ctk.StringVar(value="0 đ")

        self.create_kpi_card(self.kpi_container, "TỔNG DOANH THU TRONG KỲ", self.val_revenue, "#2ECC71", "Tổng số tiền hoàn thành từ đơn hàng đã lọc")
        self.create_kpi_card(self.kpi_container, "ĐƠN HÀNG ĐÃ XUẤT (BILLS)", self.val_orders, "#F39C12", "Tổng sản lượng đơn hàng trong khoảng đã lọc")
        self.create_kpi_card(self.kpi_container, "GIÁ TRỊ ĐH TRUNG BÌNH", self.val_avg, "#3498DB", "Tổng doanh thu chia cho số lượng hóa đơn")
        self.create_kpi_card(self.kpi_container, "⚠ HAO HỤT TÀI CHÍNH (THẤT THOÁT)", self.val_loss, "#E74C3C", "Quy đổi lệch nguyên vật liệu trong kỳ", border_left="#E74C3C")

        # ==========================================
        # 3. KHU VỰC BIỂU ĐỒ VÀ TOP MÓN (BOTTOM AREA)
        # ==========================================
        self.bottom_container = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_container.pack(fill="both", expand=True, padx=15, pady=10)

        # Trái: Biểu đồ
        self.chart_card = ctk.CTkFrame(self.bottom_container, fg_color=self.card_bg, corner_radius=8, border_width=1, border_color=self.border_color)
        self.chart_card.pack(side="left", fill="both", expand=True, padx=5)
        
        ctk.CTkLabel(self.chart_card, text="PHÂN TÍCH DOANH THU THEO NGÀY", font=ctk.CTkFont(size=14, weight="bold"), text_color=self.text_main).pack(anchor="w", padx=20, pady=(20, 0))
        self.chart_desc = ctk.CTkLabel(self.chart_card, text="Biểu đồ biểu diễn dòng tiền bán hàng các ngày gần nhất", font=ctk.CTkFont(size=11), text_color=self.text_sub)
        self.chart_desc.pack(anchor="w", padx=20, pady=(0, 20))
        
        # Vùng chứa Canvas vẽ biểu đồ
        self.canvas_frame = ctk.CTkFrame(self.chart_card, fg_color="transparent")
        self.canvas_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Phải: Top 5 món
        self.top_card = ctk.CTkFrame(self.bottom_container, fg_color=self.card_bg, corner_radius=8, border_width=1, border_color=self.border_color, width=350)
        self.top_card.pack(side="right", fill="both", padx=5)
        self.top_card.pack_propagate(False)

        ctk.CTkLabel(self.top_card, text="TOP 5 MÓN BÁN CHẠY NHẤT", font=ctk.CTkFont(size=14, weight="bold"), text_color=self.text_main).pack(anchor="w", padx=20, pady=(20, 0))
        ctk.CTkLabel(self.top_card, text="Xếp hạng dựa trên sản lượng đơn hàng đã xuất", font=ctk.CTkFont(size=11), text_color=self.text_sub).pack(anchor="w", padx=20, pady=(0, 20))
        
        self.top_items_list = ctk.CTkFrame(self.top_card, fg_color="transparent")
        self.top_items_list.pack(fill="both", expand=True, padx=20)

        # Khởi tạo dữ liệu mặc định (7 ngày qua)
        self.set_quick_date("7days")

    def create_kpi_card(self, parent, title, text_var, value_color, desc, border_left=None):
        card = ctk.CTkFrame(parent, fg_color=self.card_bg, corner_radius=8, border_width=1, border_color=self.border_color)
        card.pack(side="left", fill="both", expand=True, padx=5)
        
        if border_left:
            ctk.CTkFrame(card, width=4, fg_color=border_left, corner_radius=4).pack(side="left", fill="y", pady=15, padx=(10, 0))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(side="left", fill="both", expand=True, padx=15, pady=20)

        ctk.CTkLabel(inner, text=title, font=ctk.CTkFont(size=11, weight="bold"), text_color=self.text_sub).pack(anchor="w")
        ctk.CTkLabel(inner, textvariable=text_var, font=ctk.CTkFont(size=24, weight="bold"), text_color=value_color).pack(anchor="w", pady=5)
        ctk.CTkLabel(inner, text=desc, font=ctk.CTkFont(size=10), text_color=self.text_sub).pack(anchor="w")

    def set_quick_date(self, mode):
        today = datetime.date.today()
        if mode == "today":
            start = today
            end = today
        elif mode == "7days":
            start = today - datetime.timedelta(days=6)
            end = today
        elif mode == "month":
            start = today.replace(day=1)
            next_month = start.replace(day=28) + datetime.timedelta(days=4)
            end = next_month - datetime.timedelta(days=next_month.day)

        # Cập nhật lịch bằng lệnh set_date
        self.entry_from.set_date(start)
        self.entry_to.set_date(end)
        
        self.load_report()

    def load_report(self):
        # Lấy giá trị chuỗi ngày YYYY-MM-DD từ đối tượng Lịch
        start_date = self.entry_from.get_date().strftime("%Y-%m-%d")
        end_date = self.entry_to.get_date().strftime("%Y-%m-%d")

        # 1. CẬP NHẬT KPI CARDS
        report = self.controller.get_sales_summary(start_date, end_date)
        revenue = int(report['total_revenue'])
        orders = int(report['total_orders'])
        loss = int(report['total_loss'])
        avg_order = int(revenue / orders) if orders > 0 else 0

        self.val_revenue.set(f"{revenue:,} ₫".replace(",", "."))
        self.val_orders.set(f"{orders} đơn")
        self.val_avg.set(f"{avg_order:,} ₫".replace(",", "."))
        self.val_loss.set(f"{loss:,} ₫".replace(",", "."))

        # 2. CẬP NHẬT TOP 5 MÓN
        for widget in self.top_items_list.winfo_children():
            widget.destroy()

        top_items = self.controller.get_top_selling_items(start_date, end_date)
        for i, (name, count, rev) in enumerate(top_items):
            row = ctk.CTkFrame(self.top_items_list, fg_color="transparent")
            row.pack(fill="x", pady=10)
            
            num_box = ctk.CTkFrame(row, width=25, height=25, corner_radius=5, fg_color="#3E2723")
            num_box.pack(side="left")
            num_box.pack_propagate(False)
            ctk.CTkLabel(num_box, text=str(i+1), font=ctk.CTkFont(weight="bold"), text_color="#E67E22").pack(expand=True)

            text_box = ctk.CTkFrame(row, fg_color="transparent")
            text_box.pack(side="left", padx=15, fill="x", expand=True)
            ctk.CTkLabel(text_box, text=name, font=ctk.CTkFont(weight="bold", size=13), text_color=self.text_main).pack(anchor="w")
            ctk.CTkLabel(text_box, text=f"Doanh thu: {int(rev):,} ₫".replace(",", "."), font=ctk.CTkFont(size=11), text_color=self.text_sub).pack(anchor="w")

            ctk.CTkLabel(row, text=f"{count} ly", font=ctk.CTkFont(weight="bold", size=13), text_color=self.text_main).pack(side="right")
            
            ctk.CTkFrame(self.top_items_list, height=1, fg_color=self.border_color).pack(fill="x")

        # 3. VẼ BIỂU ĐỒ CỘT DARK THEME
        self.chart_desc.configure(text=f"Biểu đồ biểu diễn dòng tiền bán hàng từ {start_date} đến {end_date}")
        chart_data = self.controller.get_revenue_by_date(start_date, end_date)
        self.draw_bar_chart(chart_data)

    def draw_bar_chart(self, data):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
            
        if not data:
            ctk.CTkLabel(self.canvas_frame, text="Không có dữ liệu giao dịch trong khoảng thời gian này.", text_color=self.text_sub).pack(expand=True)
            return

        # Đổi màu nền Canvas tiệp với màu thẻ Dark Mode
        canvas = tk.Canvas(self.canvas_frame, bg=self.card_bg, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        self.update_idletasks()
        c_width = canvas.winfo_width()
        c_height = canvas.winfo_height()

        padding_left = 50
        padding_bottom = 30
        padding_top = 20
        chart_height = c_height - padding_bottom - padding_top
        chart_width = c_width - padding_left

        max_val = max(row[1] for row in data)
        if max_val == 0:
            max_val = 100000

        grid_steps = 4
        for i in range(grid_steps + 1):
            y = padding_top + chart_height - (i * chart_height / grid_steps)
            val_label = int(max_val * i / grid_steps)
            # Chữ hệ trục toạ độ màu xám sáng
            canvas.create_text(padding_left - 10, y, text=f"{val_label//1000}k", anchor="e", fill="#BDC3C7", font=("Arial", 9))
            # Đường line màu xám đậm
            canvas.create_line(padding_left, y, c_width, y, fill="#4D5656", dash=(4, 2))

        bar_width = min(40, chart_width / len(data) * 0.6)
        spacing = chart_width / len(data)

        for i, (date_str, rev) in enumerate(data):
            x_center = padding_left + (i * spacing) + (spacing / 2)
            bar_h = (rev / max_val) * chart_height
            y_top = padding_top + chart_height - bar_h
            y_bottom = padding_top + chart_height

            canvas.create_rectangle(x_center - bar_width/2, y_top, x_center + bar_width/2, y_bottom, fill="#E67E22", outline="")

            try:
                d_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                short_date = d_obj.strftime("%d-%m")
            except:
                short_date = date_str
                
            canvas.create_text(x_center, y_bottom + 15, text=short_date, fill="#BDC3C7", font=("Arial", 9))