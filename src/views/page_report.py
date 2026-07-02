import os
import customtkinter as ctk
import tkinter as tk
from src.controllers.report_controller import ReportController
import datetime
from dateutil.relativedelta import relativedelta
from PIL import Image
from tkcalendar import Calendar 

class PageReport(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="#121212") 
        self.controller = ReportController()

        # Bảng màu Dark Theme
        self.bg_color = "#121212"
        self.card_bg = "#212121"
        self.border_color = "#333333"
        self.text_main = "white"
        self.text_sub = "#AAAAAA"
        self.color_accent = "#E67E22"

        self.top_n = 5 

        # Thiết lập Master Grid: 4 cột bằng nhau (khớp với 4 thẻ KPI hàng 1)
        self.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="maincol")
        self.grid_rowconfigure(0, weight=0)   # Bộ lọc thời gian
        self.grid_rowconfigure(1, weight=0)   # Hàng KPI 1 (4 thẻ)
        self.grid_rowconfigure(2, weight=0)   # Hàng KPI 2 (3 thẻ) + đỉnh thẻ Top món
        self.grid_rowconfigure(3, weight=1)   # Biểu đồ + phần còn lại của Top món

        # ==========================================
        # 1. BỘ LỌC THỜI GIAN (TOP BAR)
        # ==========================================
        self.filter_card = ctk.CTkFrame(self, fg_color=self.card_bg, corner_radius=8, border_width=1, border_color=self.border_color)
        self.filter_card.grid(row=0, column=0, columnspan=4, sticky="ew", padx=20, pady=(20, 10))
        self.filter_card.grid_columnconfigure(0, weight=1)
        self.filter_card.grid_columnconfigure(1, weight=0)

        title_group = ctk.CTkFrame(self.filter_card, fg_color="transparent")
        title_group.grid(row=0, column=0, sticky="w", padx=20, pady=15)
        ctk.CTkLabel(title_group, text="LỌC THỜI GIAN TÀI CHÍNH & DOANH THU", font=ctk.CTkFont(size=14, weight="bold"), text_color=self.text_main).pack(anchor="w")
        ctk.CTkLabel(title_group, text="Tra cứu theo khoảng thời gian để tính toán Lãi/Lỗ chính xác.", font=ctk.CTkFont(size=12), text_color=self.text_sub).pack(anchor="w")

        action_group = ctk.CTkFrame(self.filter_card, fg_color="transparent")
        action_group.grid(row=0, column=1, sticky="e", padx=20, pady=15)

        date_input_group = ctk.CTkFrame(action_group, fg_color="transparent")
        date_input_group.pack(side="left", padx=10)
        
        ctk.CTkLabel(date_input_group, text="TỪ NGÀY:", font=ctk.CTkFont(size=10, weight="bold"), text_color=self.text_sub).grid(row=0, column=0, columnspan=2, sticky="w", padx=2)
        ctk.CTkLabel(date_input_group, text="ĐẾN NGÀY:", font=ctk.CTkFont(size=10, weight="bold"), text_color=self.text_sub).grid(row=0, column=2, columnspan=2, sticky="w", padx=10)
        
        self.entry_from = ctk.CTkEntry(date_input_group, width=110, fg_color=self.card_bg, border_color=self.border_color, text_color=self.text_main)
        self.entry_from.grid(row=1, column=0, padx=(2, 0), pady=2)
        ctk.CTkButton(date_input_group, text="📅", width=30, fg_color="#333333", hover_color="#555555", command=lambda: self.open_calendar(self.entry_from)).grid(row=1, column=1, padx=(2, 10))

        self.entry_to = ctk.CTkEntry(date_input_group, width=110, fg_color=self.card_bg, border_color=self.border_color, text_color=self.text_main)
        self.entry_to.grid(row=1, column=2, padx=(2, 0), pady=2)
        ctk.CTkButton(date_input_group, text="📅", width=30, fg_color="#333333", hover_color="#555555", command=lambda: self.open_calendar(self.entry_to)).grid(row=1, column=3, padx=(2, 10))

        btn_group = ctk.CTkFrame(action_group, fg_color="transparent")
        btn_group.pack(side="left", padx=10)
        ctk.CTkLabel(btn_group, text="PHẠM VI NHANH:", font=ctk.CTkFont(size=10, weight="bold"), text_color=self.text_sub).pack(anchor="w", padx=2)
        
        btn_row = ctk.CTkFrame(btn_group, fg_color="transparent")
        btn_row.pack(fill="x")
        
        self.btn_today = ctk.CTkButton(btn_row, text="Hôm nay", width=60, fg_color="#333333", text_color="white", hover_color="#555555", command=lambda: self.set_quick_date("today", self.btn_today))
        self.btn_today.pack(side="left", padx=2)
        
        self.btn_7days = ctk.CTkButton(btn_row, text="7 ngày qua", width=70, fg_color=self.color_accent, text_color="white", hover_color="#D35400", command=lambda: self.set_quick_date("7days", self.btn_7days))
        self.btn_7days.pack(side="left", padx=2)
        
        self.btn_month = ctk.CTkButton(btn_row, text="Tháng này", width=70, fg_color="#333333", text_color="white", hover_color="#555555", command=lambda: self.set_quick_date("month", self.btn_month))
        self.btn_month.pack(side="left", padx=2)
        
        ctk.CTkButton(action_group, text="Lọc Dữ Liệu", width=60, fg_color="#2980B9", hover_color="#1F618D", command=self.manual_filter).pack(side="left", padx=(10,0), pady=(15,0))

        # ==========================================
        # 2. BẢY THẺ KPI (Chuẩn Kế toán 2 Hàng: 4 + 3)
        # ==========================================
        # --- HÀNG 1 (4 Thẻ): Tài chính Cốt lõi — đặt trực tiếp lên lưới chính (cột 0-3) ---
        self.lbl_net_profit, self.border_net = self.create_kpi_card(self, 1, 0, "1. LỢI NHUẬN ĐÃ TRỪ VỐN", "#2ECC71", "Lãi gộp trừ tiếp tiền nhập hàng (Dòng tiền)", border_left=self.color_accent)
        self.lbl_gross_profit, self.border_gross = self.create_kpi_card(self, 1, 1, "2. LỢI NHUẬN CHƯA TRỪ VỐN", "#2ECC71", "Doanh thu trừ Giá trị bán ra (Lãi gộp)", border_left=self.color_accent)
        self.lbl_revenue, _ = self.create_kpi_card(self, 1, 2, "3. DOANH THU BÁN HÀNG", "#3498DB", "Tổng tiền khách đã thanh toán")
        self.lbl_restock, _ = self.create_kpi_card(self, 1, 3, "4. TIỀN NHẬP KHO", "#E74C3C", "Tổng giá trị tiền chi ra nhập hàng")

        # --- HÀNG 2 (3 Thẻ): Số liệu Vận hành — chỉ chiếm cột 0-2, nhường cột 3 cho Top món ---
        self.lbl_cogs, _ = self.create_kpi_card(self, 2, 0, "5. GIÁ TRỊ BÁN RA (COGS)", "#E67E22", "Tổng giá vốn nguyên liệu của các đơn đã bán")
        self.lbl_orders, _ = self.create_kpi_card(self, 2, 1, "6. SỐ ĐƠN BÁN RA", "#F39C12", "Sản lượng hóa đơn hoàn thành")
        self.lbl_avg_order, _ = self.create_kpi_card(self, 2, 2, "7. GIÁ TRỊ TRUNG BÌNH ĐƠN", "#9B59B6", "Doanh thu chia cho Số lượng đơn")

        # ==========================================
        # 3. KHU VỰC BIỂU ĐỒ (trái, hàng 3) VÀ TOP MÓN (phải, kéo dài từ hàng 2 -> hàng 3)
        # ==========================================
        # Trái: Biểu đồ — chiếm 3 cột (0-2), chỉ nằm ở hàng cuối (hàng giãn nở)
        self.chart_card = ctk.CTkFrame(self, fg_color=self.card_bg, corner_radius=8, border_width=1, border_color=self.border_color)
        self.chart_card.grid(row=3, column=0, columnspan=3, sticky="nsew", padx=5, pady=(5, 15))

        ctk.CTkLabel(self.chart_card, text="PHÂN TÍCH DOANH THU THEO THỜI GIAN", font=ctk.CTkFont(size=14, weight="bold"), text_color=self.text_main).pack(anchor="w", padx=20, pady=(20, 0))
        self.chart_desc = ctk.CTkLabel(self.chart_card, text="Đang tính toán...", font=ctk.CTkFont(size=11), text_color=self.text_sub)
        self.chart_desc.pack(anchor="w", padx=20, pady=(0, 20))
        
        self.canvas_frame = ctk.CTkFrame(self.chart_card, fg_color="transparent")
        self.canvas_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Phải: Top N món — chiếm cột 3, KÉO LÊN từ hàng 2 (khỏa lấp vị trí "thẻ 8" còn trống)
        # xuống hết hàng 3 => cao hơn hẳn, nhưng chỉ rộng bằng 1 cột KPI (hẹp hơn trước).
        self.top_card = ctk.CTkFrame(self, fg_color=self.card_bg, corner_radius=8, border_width=1, border_color=self.border_color)
        self.top_card.grid(row=2, column=3, rowspan=2, sticky="nsew", padx=5, pady=(5, 15))

        top_header_frame = ctk.CTkFrame(self.top_card, fg_color="transparent")
        top_header_frame.pack(fill="x", padx=15, pady=(15, 0))
        
        self.lbl_top_title = ctk.CTkLabel(top_header_frame, text=f"TOP {self.top_n} MÓN BÁN CHẠY", font=ctk.CTkFont(size=13, weight="bold"), text_color=self.text_main)
        self.lbl_top_title.pack(side="left")

        ctrl_top = ctk.CTkFrame(top_header_frame, fg_color="#333333", corner_radius=4)
        ctrl_top.pack(side="right")
        ctk.CTkButton(ctrl_top, text="-", width=24, height=24, fg_color="transparent", text_color="white", command=self.decrease_top_n).pack(side="left")
        ctk.CTkButton(ctrl_top, text="+", width=24, height=24, fg_color="transparent", text_color="white", command=self.increase_top_n).pack(side="left")

        ctk.CTkLabel(self.top_card, text="Theo sản lượng hóa đơn", font=ctk.CTkFont(size=11), text_color=self.text_sub).pack(anchor="w", padx=15, pady=(0, 12))
        
        self.top_items_list = ctk.CTkScrollableFrame(self.top_card, fg_color="transparent")
        self.top_items_list.pack(fill="both", expand=True, padx=8, pady=(0, 10))

        self.after(200, lambda: self.set_quick_date("7days", self.btn_7days))

    # ==========================================
    # POPUP CHỌN LỊCH 
    # ==========================================
    def open_calendar(self, target_entry):
        popup = ctk.CTkToplevel(self)
        popup.title("Chọn Ngày")
        popup.geometry("320x340")
        popup.attributes("-topmost", True)
        popup.grab_set() 
        popup.configure(fg_color=self.bg_color)

        cal = Calendar(popup, selectmode='day', date_pattern='y-mm-dd',
                       background='#121212', foreground='white', bordercolor='#333333',
                       headersbackground='#212121', headersforeground='white',
                       selectbackground=self.color_accent, selectforeground='white',
                       normalbackground='#333333', normalforeground='white',
                       bottombackground='#212121')
        cal.pack(fill="both", expand=True, padx=15, pady=(15, 10))

        current_val = target_entry.get().strip()
        if current_val:
            try:
                dt = datetime.datetime.strptime(current_val, "%Y-%m-%d").date()
                cal.selection_set(dt)
            except ValueError:
                pass

        def confirm():
            target_entry.delete(0, "end")
            target_entry.insert(0, cal.get_date())
            popup.destroy()

        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))
        ctk.CTkButton(btn_frame, text="Hủy", fg_color="transparent", border_width=1, border_color=self.text_sub, text_color="white", hover_color="#333333", command=popup.destroy).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(btn_frame, text="Xác nhận", fg_color=self.color_accent, hover_color="#D35400", text_color="white", font=ctk.CTkFont(weight="bold"), command=confirm).pack(side="right", fill="x", expand=True, padx=(5, 0))


    # ==========================================
    # CÁC HÀM TIỆN ÍCH & TƯƠNG TÁC
    # ==========================================
    def create_kpi_card(self, parent, row, col, title, value_color, desc, border_left=None):
        card = ctk.CTkFrame(parent, fg_color=self.card_bg, corner_radius=8, border_width=1, border_color=self.border_color, height=120)
        card.grid(row=row, column=col, sticky="nsew", padx=5, pady=5) 
        card.pack_propagate(False)   # Khóa chiều cao cố định (con bên trong dùng pack, nên phải dùng pack_propagate)

        border_frame = None
        if border_left:
            border_frame = ctk.CTkFrame(card, width=4, fg_color=border_left, corner_radius=4)
            border_frame.pack(side="left", fill="y", pady=15, padx=(10, 0))
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        
        ctk.CTkLabel(inner, text=title, font=ctk.CTkFont(size=11, weight="bold"), text_color=self.text_sub).pack(anchor="w")
        
        lbl_val = ctk.CTkLabel(inner, text="0 ₫", font=ctk.CTkFont(size=22, weight="bold"), text_color=value_color)
        lbl_val.pack(anchor="w", pady=5)
        
        ctk.CTkLabel(inner, text=desc, font=ctk.CTkFont(size=10), text_color=self.text_sub).pack(anchor="w")
        
        return lbl_val, border_frame

    def get_image(self, path, size=(40, 40)):
        if path and os.path.exists(path):
            try: return ctk.CTkImage(light_image=Image.open(path), size=size)
            except Exception: pass
        return None

    def increase_top_n(self):
        self.top_n += 1
        self.lbl_top_title.configure(text=f"TOP {self.top_n} MÓN BÁN CHẠY")
        self.load_report()

    def decrease_top_n(self):
        if self.top_n > 1:
            self.top_n -= 1
            self.lbl_top_title.configure(text=f"TOP {self.top_n} MÓN BÁN CHẠY")
            self.load_report()

    def set_quick_date(self, mode, active_btn):
        for btn in [self.btn_today, self.btn_7days, self.btn_month]:
            btn.configure(fg_color="#333333")
        
        active_btn.configure(fg_color=self.color_accent)

        today = datetime.date.today()
        if mode == "today":
            start, end = today, today
        elif mode == "7days":
            start, end = today - datetime.timedelta(days=6), today
        elif mode == "month":
            start = today.replace(day=1)
            next_month = start.replace(day=28) + datetime.timedelta(days=4)
            end = next_month - datetime.timedelta(days=next_month.day)

        self.entry_from.delete(0, 'end')
        self.entry_from.insert(0, start.strftime("%Y-%m-%d"))
        
        self.entry_to.delete(0, 'end')
        self.entry_to.insert(0, end.strftime("%Y-%m-%d"))
        
        self.load_report()

    def manual_filter(self):
        for btn in [self.btn_today, self.btn_7days, self.btn_month]:
            btn.configure(fg_color="#333333")
        self.load_report()

    # ==========================================
    # CẬP NHẬT DỮ LIỆU BÁO CÁO KẾ TOÁN
    # ==========================================
    def load_report(self):
        start_date = self.entry_from.get().strip()
        end_date = self.entry_to.get().strip()
        
        try: datetime.datetime.strptime(start_date, "%Y-%m-%d")
        except: start_date = datetime.date.today().strftime("%Y-%m-%d")
        
        try: datetime.datetime.strptime(end_date, "%Y-%m-%d")
        except: end_date = datetime.date.today().strftime("%Y-%m-%d")

        # 1. KPI CARDS (LOGIC KẾ TOÁN 7 THẺ)
        report = self.controller.get_sales_summary(start_date, end_date)
        revenue = int(report.get('total_revenue', 0))
        orders = int(report.get('total_orders', 0))
        restock_cost = int(report.get('total_restock_cost', 0))
        cogs = int(report.get('total_cogs', 0))
        
        avg_order = int(revenue / orders) if orders > 0 else 0

        # Lãi gộp (Chưa trừ phí nhập) = Doanh thu - Giá vốn
        gross_profit = revenue - cogs
        
        # Dòng tiền (Đã trừ phí nhập) = Lãi gộp - Chi phí nhập hàng
        net_profit = gross_profit - restock_cost

        # --- Xử lý Màu sắc & Format cho Lãi Gộp ---
        if gross_profit > 0:
            color_gross = "#2ECC71" 
            gross_str = f"+{gross_profit:,} ₫".replace(",", ".")
        elif gross_profit < 0:
            color_gross = "#E74C3C" 
            gross_str = f"{gross_profit:,} ₫".replace(",", ".")
        else:
            color_gross = "#E67E22" 
            gross_str = "0 ₫"

        # --- Xử lý Màu sắc & Format cho Dòng Tiền Thuần ---
        if net_profit > 0:
            color_net = "#2ECC71" 
            net_str = f"+{net_profit:,} ₫".replace(",", ".")
        elif net_profit < 0:
            color_net = "#E74C3C" 
            net_str = f"{net_profit:,} ₫".replace(",", ".")
        else:
            color_net = "#E67E22" 
            net_str = "0 ₫"

        # Đổ dữ liệu lên UI
        self.lbl_net_profit.configure(text=net_str, text_color=color_net)
        if self.border_net: self.border_net.configure(fg_color=color_net)

        self.lbl_gross_profit.configure(text=gross_str, text_color=color_gross)
        if self.border_gross: self.border_gross.configure(fg_color=color_gross)

        self.lbl_revenue.configure(text=f"{revenue:,} ₫".replace(",", "."), text_color="#3498DB")
        self.lbl_restock.configure(text=f"{restock_cost:,} ₫".replace(",", "."), text_color="#E74C3C")
        self.lbl_cogs.configure(text=f"{cogs:,} ₫".replace(",", "."), text_color="#E67E22")
        self.lbl_orders.configure(text=f"{orders} đơn", text_color="#F39C12") 
        self.lbl_avg_order.configure(text=f"{avg_order:,} ₫".replace(",", "."), text_color="#9B59B6")

        # 2. TOP N MÓN
        for widget in self.top_items_list.winfo_children(): widget.destroy()

        top_items = self.controller.get_top_selling_items(start_date, end_date, limit=self.top_n)
        for i, item in enumerate(top_items):
            d_id, ten_mon, phan_loai, hinh_anh, count, rev = item
            
            row = ctk.CTkFrame(self.top_items_list, fg_color="transparent")
            row.pack(fill="x", pady=6)
            
            num_box = ctk.CTkFrame(row, width=25, height=25, corner_radius=5, fg_color="#333333")
            num_box.pack(side="left")
            num_box.pack_propagate(False)
            ctk.CTkLabel(num_box, text=str(i+1), font=ctk.CTkFont(weight="bold"), text_color=self.color_accent).pack(expand=True)

            img_obj = self.get_image(hinh_anh)
            if img_obj:
                ctk.CTkLabel(row, image=img_obj, text="").pack(side="left", padx=(10, 0))
            else:
                bg_color = f"#{abs(hash(phan_loai or 'X')) % 0xFFFFFF:06x}"
                icon = ctk.CTkFrame(row, width=40, height=40, corner_radius=8, fg_color=bg_color)
                icon.pack(side="left", padx=(10, 0))
                icon.pack_propagate(False)
                ctk.CTkLabel(icon, text=ten_mon[:2].upper(), text_color="white", font=ctk.CTkFont(weight="bold")).pack(expand=True)

            text_box = ctk.CTkFrame(row, fg_color="transparent")
            text_box.pack(side="left", padx=10, fill="x", expand=True)
            ctk.CTkLabel(text_box, text=ten_mon, font=ctk.CTkFont(weight="bold", size=13), text_color=self.text_main).pack(anchor="w")
            ctk.CTkLabel(text_box, text=f"Doanh thu: {int(rev):,} ₫".replace(",", "."), font=ctk.CTkFont(size=11), text_color=self.text_sub).pack(anchor="w")

            ctk.CTkLabel(row, text=f"{count} ly", font=ctk.CTkFont(weight="bold", size=13), text_color=self.text_main).pack(side="right")
            ctk.CTkFrame(self.top_items_list, height=1, fg_color=self.border_color).pack(fill="x", pady=2)

        if not top_items:
            ctk.CTkLabel(self.top_items_list, text="Không có dữ liệu trong khoảng này.", text_color=self.text_sub).pack(pady=20)

        # 3. BIỂU ĐỒ 
        raw_data = self.controller.get_revenue_by_date(start_date, end_date)
        processed_data, date_type = self.group_chart_data(raw_data, start_date, end_date)
        
        self.chart_desc.configure(text=f"Biểu đồ biểu diễn dòng tiền bán hàng từ {start_date} đến {end_date} (Nhóm theo {date_type})")
        self.draw_bar_chart(processed_data)

    def group_chart_data(self, raw_data, start_str, end_str):
        try:
            d1 = datetime.datetime.strptime(start_str, "%Y-%m-%d")
            d2 = datetime.datetime.strptime(end_str, "%Y-%m-%d")
            delta = (d2 - d1).days
        except:
            return raw_data, "Ngày"

        if delta <= 31:
            date_type = "Ngày"
            step = datetime.timedelta(days=1)
        elif delta <= 90:
            date_type = "Tuần"
            step = datetime.timedelta(days=7)
            d1 = d1 - datetime.timedelta(days=d1.weekday())
        elif delta <= 365:
            date_type = "Tháng"
            step = relativedelta(months=1)
            d1 = d1.replace(day=1)
        else:
            date_type = "Năm"
            step = relativedelta(years=1)
            d1 = d1.replace(month=1, day=1)

        buckets = {}
        curr = d1
        while curr <= d2:
            if date_type == "Ngày": 
                label = curr.strftime("%d/%m")
            elif date_type == "Tuần": 
                label = f"Tuần {curr.strftime('%d/%m')}"
            elif date_type == "Tháng": 
                label = curr.strftime("T%m/%Y")
            else: 
                label = curr.strftime("Năm %Y")
            
            buckets[label] = 0
            curr += step

        for date_str, rev in raw_data:
            try:
                d_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                if date_type == "Ngày": 
                    label = d_obj.strftime("%d/%m")
                elif date_type == "Tuần": 
                    start_of_week = d_obj - datetime.timedelta(days=d_obj.weekday())
                    label = f"Tuần {start_of_week.strftime('%d/%m')}"
                elif date_type == "Tháng": 
                    label = d_obj.strftime("T%m/%Y")
                else: 
                    label = d_obj.strftime("Năm %Y")
                
                if label in buckets:
                    buckets[label] += rev
                else:
                    buckets[label] = rev 
            except:
                pass
        
        return list(buckets.items()), date_type

    def draw_bar_chart(self, data):
        self.current_chart_data = data 
        
        for widget in self.canvas_frame.winfo_children(): 
            widget.destroy()
            
        if not data:
            ctk.CTkLabel(self.canvas_frame, text="Không có dữ liệu giao dịch trong khoảng thời gian này.", text_color=self.text_sub).pack(expand=True)
            return

        self.chart_canvas = tk.Canvas(self.canvas_frame, bg=self.card_bg, highlightthickness=0)
        self.chart_canvas.pack(fill="both", expand=True)

        self.resize_timer = None
        self.chart_canvas.bind("<Configure>", self.on_canvas_resize)

        self.update_idletasks()
        self.render_canvas_graphics()

    def on_canvas_resize(self, event):
        if self.resize_timer is not None:
            self.after_cancel(self.resize_timer)
        self.resize_timer = self.after(100, self.render_canvas_graphics)

    def render_canvas_graphics(self):
        if not hasattr(self, 'chart_canvas') or not self.chart_canvas.winfo_exists():
            return
            
        self.chart_canvas.delete("all") 
        
        c_width = self.chart_canvas.winfo_width()
        c_height = self.chart_canvas.winfo_height()
        
        if c_width <= 10 or c_height <= 10:
            return

        data = getattr(self, 'current_chart_data', [])
        if not data: return

        padding_left = 60
        padding_bottom = 30
        padding_top = 20
        chart_height = c_height - padding_bottom - padding_top
        chart_width = c_width - padding_left

        max_val = max((row[1] for row in data), default=0)
        if max_val == 0: max_val = 100000

        for i in range(5):
            y = padding_top + chart_height - (i * chart_height / 4)
            val_label = int(max_val * i / 4)
            
            if val_label >= 1000000: text_y = f"{val_label/1000000:g}M"
            else: text_y = f"{val_label//1000}k" if val_label > 0 else "0"
                
            self.chart_canvas.create_text(padding_left - 10, y, text=text_y, anchor="e", fill="#BDC3C7", font=("Arial", 9))
            self.chart_canvas.create_line(padding_left, y, c_width, y, fill="#4D5656", dash=(4, 2))

        num_bars = len(data)
        bar_width = min(40, chart_width / num_bars * 0.6)
        spacing = chart_width / num_bars

        label_step = 1
        if num_bars > 20: label_step = 3
        elif num_bars > 12: label_step = 2

        for i, (label_x, rev) in enumerate(data):
            x_center = padding_left + (i * spacing) + (spacing / 2)
            bar_h = (rev / max_val) * chart_height
            y_top = padding_top + chart_height - bar_h
            y_bottom = padding_top + chart_height

            if rev > 0:
                self.chart_canvas.create_rectangle(x_center - bar_width/2, y_top, x_center + bar_width/2, y_bottom, fill=self.color_accent, outline="")
            
            if i % label_step == 0 or i == num_bars - 1:
                self.chart_canvas.create_text(x_center, y_bottom + 15, text=label_x, fill="#BDC3C7", font=("Arial", 9))