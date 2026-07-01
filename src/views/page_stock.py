import customtkinter as ctk
import tkinter.messagebox as messagebox
from src.controllers.stock_controller import StockController

class PageStock(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="#121212")
        self.controller = StockController()

        self.bg_color = "#121212"
        self.card_color = "#212121"
        self.border_color = "#333333"
        self.text_main = "white"
        self.text_sub = "#AAAAAA"
        self.color_accent = "#E67E22"

        self.build_ui()

    def build_ui(self):
        # ==========================================
        # 1. HEADER & CỤM NÚT CHỨC NĂNG TỔNG
        # ==========================================
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=(10, 5))

        self.title_group = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.title_group.pack(side="left")
        ctk.CTkLabel(self.title_group, text="QUẢN LÝ KHO NGUYÊN LIỆU THÔ", font=ctk.CTkFont(size=20, weight="bold"), text_color=self.text_main).pack(anchor="w")
        ctk.CTkLabel(self.title_group, text="Theo dõi tồn lý thuyết song song với tồn thực tế, quản lý chênh lệch hao hụt.", font=ctk.CTkFont(size=13), text_color=self.text_sub).pack(anchor="w")

        self.btn_group = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.btn_group.pack(side="right", pady=5)

        self.btn_add = ctk.CTkButton(self.btn_group, text="+ Thêm nguyên liệu thô", fg_color="#196F3D", hover_color="#145A32", text_color="white", command=self.ui_add_ingredient_popup)
        self.btn_add.pack(side="left", padx=5)

        self.btn_audit = ctk.CTkButton(self.btn_group, text="🔄 Kiểm kho (Định mức thực tế)", fg_color=self.color_accent, hover_color="#D35400", text_color="white", command=self.ui_sync_stock_popup)
        self.btn_audit.pack(side="left", padx=5)

        self.btn_restock = ctk.CTkButton(self.btn_group, text="+ Nhập thêm nguyên liệu", fg_color="transparent", border_width=1, border_color=self.text_sub, text_color=self.text_main, hover_color="#333333", command=self.ui_restock_popup)
        self.btn_restock.pack(side="left", padx=5)

        self.banner_frame = ctk.CTkFrame(self, fg_color=self.card_color, border_width=1, border_color=self.border_color, corner_radius=8)
        self.banner_frame.pack(fill="x", padx=20, pady=(10, 15))
        ctk.CTkLabel(self.banner_frame, text="ⓘ Cơ chế tự động: Mỗi ly bán hàng thành công ở trang 1 sẽ trừ thô nguyên vật liệu tương ứng.", font=ctk.CTkFont(size=13), text_color=self.color_accent).pack(anchor="w", padx=15, pady=10)

        # ==========================================
        # 2. KHU VỰC LƯỚI KHO (CỐ ĐỊNH TIÊU ĐỀ)
        # ==========================================
        self.list_container = ctk.CTkFrame(self, fg_color=self.card_color, corner_radius=8, border_width=1, border_color=self.border_color)
        self.list_container.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Tiêu đề cố định
        self.stock_header_frame = ctk.CTkFrame(self.list_container, fg_color="transparent")
        self.stock_header_frame.pack(fill="x", padx=(10, 26), pady=(10, 5))
        self.setup_stock_grid(self.stock_header_frame)

        headers = ["MÃ NL", "TÊN NGUYÊN LIỆU", "TỒN LÝ THUYẾT", "TỒN THỰC TẾ ĐẾM", "ĐƠN GIÁ VỐN NHẬP", "TỔNG GIÁ TRỊ TỒN THỰC", "TRẠNG THÁI", "HÀNH ĐỘNG"]
        for col_idx, col_name in enumerate(headers):
            ctk.CTkLabel(self.stock_header_frame, text=col_name, anchor="w", font=ctk.CTkFont(size=12, weight="bold"), text_color=self.text_sub).grid(row=0, column=col_idx, sticky="w", padx=5)

        ctk.CTkFrame(self.list_container, height=1, fg_color="#333333").pack(fill="x", padx=10)

        # Lưới cuộn dữ liệu Kho
        self.stock_scroll_frame = ctk.CTkScrollableFrame(self.list_container, fg_color="transparent")
        self.stock_scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.setup_stock_grid(self.stock_scroll_frame)

        # ==========================================
        # 3. KHU VỰC LỊCH SỬ HAO HỤT (CỐ ĐỊNH TIÊU ĐỀ)
        # ==========================================
        self.history_container = ctk.CTkFrame(self, fg_color=self.card_color, corner_radius=8, border_width=1, border_color=self.border_color, height=250)
        self.history_container.pack(fill="x", padx=20, pady=(0, 20))
        self.history_container.pack_propagate(False)

        ctk.CTkLabel(self.history_container, text="LỊCH SỬ CHÊNH LỆCH & HAO HỤT THỰC TẾ", font=ctk.CTkFont(size=14, weight="bold"), text_color=self.text_main).pack(anchor="w", padx=15, pady=(15, 10))

        # Tiêu đề cố định
        self.hist_header_frame = ctk.CTkFrame(self.history_container, fg_color="transparent")
        self.hist_header_frame.pack(fill="x", padx=(10, 26), pady=(0, 5))
        self.setup_hist_grid(self.hist_header_frame)

        h_cols = ["THỜI GIAN", "TÊN NGUYÊN LIỆU", "LÝ THUYẾT", "THỰC TẾ", "LỆCH HAO HỤT", "LÝ DO ĐIỀU CHỈNH"]
        for col_idx, col_name in enumerate(h_cols):
            ctk.CTkLabel(self.hist_header_frame, text=col_name, anchor="w", font=ctk.CTkFont(size=12, weight="bold"), text_color=self.text_sub).grid(row=0, column=col_idx, sticky="w", padx=5)

        ctk.CTkFrame(self.history_container, height=1, fg_color="#333333").pack(fill="x", padx=10)

        # Lưới cuộn dữ liệu Lịch sử
        self.hist_scroll_frame = ctk.CTkScrollableFrame(self.history_container, fg_color="transparent")
        self.hist_scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.setup_hist_grid(self.hist_scroll_frame)

        self.refresh_stock_list()

    def setup_stock_grid(self, parent):
        parent.grid_columnconfigure(0, weight=1) 
        parent.grid_columnconfigure(1, weight=3) 
        parent.grid_columnconfigure(2, weight=2) 
        parent.grid_columnconfigure(3, weight=2) 
        parent.grid_columnconfigure(4, weight=2) 
        parent.grid_columnconfigure(5, weight=2) 
        parent.grid_columnconfigure(6, weight=2) 
        parent.grid_columnconfigure(7, weight=2) 

    def setup_hist_grid(self, parent):
        parent.grid_columnconfigure(0, weight=2)
        parent.grid_columnconfigure(1, weight=3)
        parent.grid_columnconfigure(2, weight=1)
        parent.grid_columnconfigure(3, weight=1)
        parent.grid_columnconfigure(4, weight=1)
        parent.grid_columnconfigure(5, weight=3)

    def format_currency(self, amount):
        return f"{amount:,.0f} đ".replace(",", ".")

    # ==========================================
    # CÁC HÀM RENDER DỮ LIỆU
    # ==========================================
    def refresh_stock_list(self):
        for widget in self.stock_scroll_frame.winfo_children():
            widget.destroy()

        items = self.controller.get_inventory()

        for i, item in enumerate(items):
            i_id, i_name, i_unit, i_theory, i_actual, i_warn, i_cost = item
            
            i_theory, i_actual, i_warn, i_cost = float(i_theory or 0), float(i_actual or 0), float(i_warn or 0), float(i_cost or 0)
            total_val = i_actual * i_cost
            is_warning = i_actual <= i_warn or i_theory <= i_warn
            r = (i * 2)

            ctk.CTkLabel(self.stock_scroll_frame, text=f"NL_{i_id:03d}", anchor="w", text_color=self.text_sub).grid(row=r, column=0, sticky="w", padx=5, pady=8)
            
            name_frame = ctk.CTkFrame(self.stock_scroll_frame, fg_color="transparent")
            name_frame.grid(row=r, column=1, sticky="w", padx=5)
            ctk.CTkLabel(name_frame, text=i_name, anchor="w", font=ctk.CTkFont(weight="bold"), text_color="#E74C3C" if is_warning else self.text_main).pack(anchor="w")
            ctk.CTkLabel(name_frame, text=f"Mức an toàn tối thiểu: {i_warn:g} {i_unit}", anchor="w", font=ctk.CTkFont(size=11), text_color=self.text_sub).pack(anchor="w")

            ctk.CTkLabel(self.stock_scroll_frame, text=f"{i_theory:g} {i_unit}", anchor="w", text_color=self.text_sub).grid(row=r, column=2, sticky="w", padx=5)
            ctk.CTkLabel(self.stock_scroll_frame, text=f"{i_actual:g} {i_unit}", anchor="w", font=ctk.CTkFont(weight="bold"), text_color=self.text_main).grid(row=r, column=3, sticky="w", padx=5)
            
            ctk.CTkLabel(self.stock_scroll_frame, text=f"{self.format_currency(i_cost)} / {i_unit}", anchor="w", text_color=self.text_sub).grid(row=r, column=4, sticky="w", padx=5)
            ctk.CTkLabel(self.stock_scroll_frame, text=self.format_currency(total_val), anchor="w", text_color="#E74C3C", font=ctk.CTkFont(weight="bold")).grid(row=r, column=5, sticky="w", padx=5)

            status_text = "⚠ BÁO ĐỘNG" if is_warning else "✔ AN TOÀN"
            status_color = "#E74C3C" if is_warning else "#2ECC71"
            ctk.CTkLabel(self.stock_scroll_frame, text=status_text, text_color=status_color, font=ctk.CTkFont(size=11, weight="bold")).grid(row=r, column=6, sticky="w", padx=5)

            # Khối nút Sửa / Xóa
            action_frame = ctk.CTkFrame(self.stock_scroll_frame, fg_color="transparent")
            action_frame.grid(row=r, column=7, sticky="w", padx=5)
            ctk.CTkButton(action_frame, text="Sửa", width=40, fg_color="#333333", text_color="white", hover_color="#555555", command=lambda id=i_id, n=i_name, u=i_unit, w=i_warn: self.ui_edit_ingredient_popup(id, n, u, w)).pack(side="left", padx=2)
            ctk.CTkButton(action_frame, text="Xóa", width=40, fg_color="transparent", border_width=1, border_color="#E74C3C", text_color="#E74C3C", hover_color="#641E16", command=lambda id=i_id, n=i_name: self.ui_delete_ingredient(id, n)).pack(side="left", padx=2)

            ctk.CTkFrame(self.stock_scroll_frame, height=1, fg_color=self.border_color).grid(row=r+1, column=0, columnspan=8, sticky="ew", pady=2)

        if not items:
            ctk.CTkLabel(self.stock_scroll_frame, text="Kho đang trống. Hãy thêm nguyên vật liệu mới.", text_color=self.text_sub).grid(row=0, column=0, columnspan=8, pady=40)

        self.render_history()

    def render_history(self):
        for widget in self.hist_scroll_frame.winfo_children(): 
            widget.destroy()

        history_items = self.controller.get_stock_history(limit=20)
        for i, item in enumerate(history_items):
            h_id, name, theo, actual, diff, reason, time_stamp = item
            r = i * 2
            
            # Ép kiểu float và làm tròn để loại bỏ lỗi số học máy tính (VD: 7.10543e-15)
            theo, actual, diff = float(theo or 0), float(actual or 0), float(diff or 0)
            diff = round(actual - theo, 3)

            ctk.CTkLabel(self.hist_scroll_frame, text=time_stamp, anchor="w", text_color=self.text_sub).grid(row=r, column=0, sticky="w", padx=5, pady=8)
            ctk.CTkLabel(self.hist_scroll_frame, text=name, anchor="w", text_color=self.text_main).grid(row=r, column=1, sticky="w", padx=5, pady=8)
            ctk.CTkLabel(self.hist_scroll_frame, text=f"{theo:g}", anchor="w", text_color=self.text_sub).grid(row=r, column=2, sticky="w", padx=5, pady=8)
            ctk.CTkLabel(self.hist_scroll_frame, text=f"{actual:g}", anchor="w", text_color=self.text_main).grid(row=r, column=3, sticky="w", padx=5, pady=8)
            
            diff_color = "#E74C3C" if diff < 0 else "#2ECC71" if diff > 0 else self.text_sub
            ctk.CTkLabel(self.hist_scroll_frame, text=f"{diff:g}", anchor="w", text_color=diff_color, font=ctk.CTkFont(weight="bold")).grid(row=r, column=4, sticky="w", padx=5, pady=8)
            ctk.CTkLabel(self.hist_scroll_frame, text=reason or "-", anchor="w", text_color=self.text_sub).grid(row=r, column=5, sticky="w", padx=5, pady=8)

            ctk.CTkFrame(self.hist_scroll_frame, height=1, fg_color=self.border_color).grid(row=r+1, column=0, columnspan=6, sticky="ew", pady=2)

        if not history_items:
            ctk.CTkLabel(self.hist_scroll_frame, text="Chưa có lịch sử biến động.", text_color=self.text_sub).grid(row=0, column=0, columnspan=6, pady=20)


    # ==========================================
    # CÁC HÀM POP-UP (TOPLEVEL)
    # ==========================================
    def create_popup(self, title, size):
        popup = ctk.CTkToplevel(self)
        popup.title(title)
        popup.geometry(size)
        popup.attributes("-topmost", True)
        popup.configure(fg_color=self.bg_color)
        popup.grab_set() 
        return popup

    def ui_add_ingredient_popup(self):
        popup = self.create_popup("Thêm Nguyên Liệu Thô", "450x650")
        
        ctk.CTkLabel(popup, text="THÊM NGUYÊN LIỆU THÔ MỚI", font=ctk.CTkFont(size=18, weight="bold"), text_color=self.text_main).pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(popup, text="Hệ thống sẽ tự động tính Đơn Giá Vốn dựa trên tổng tiền\nbạn thanh toán chia cho số lượng nhập vào.", justify="left", text_color=self.text_sub).pack(anchor="w", padx=20, pady=(0, 20))

        ctk.CTkLabel(popup, text="TÊN NGUYÊN LIỆU THÔ:", font=ctk.CTkFont(size=11, weight="bold"), text_color=self.text_sub).pack(anchor="w", padx=20)
        e_name = ctk.CTkEntry(popup, placeholder_text="e.g. Hạt Cà Phê Robusta", height=40, fg_color=self.card_color, border_color=self.border_color, text_color=self.text_main)
        e_name.pack(fill="x", padx=20, pady=(5, 15))

        row2 = ctk.CTkFrame(popup, fg_color="transparent")
        row2.pack(fill="x", padx=20, pady=5)
        col1 = ctk.CTkFrame(row2, fg_color="transparent")
        col1.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(col1, text="ĐƠN VỊ ĐẾM (UNIT):", font=ctk.CTkFont(size=11, weight="bold"), text_color=self.text_sub).pack(anchor="w")
        e_unit = ctk.CTkEntry(col1, placeholder_text="Kg, Hộp, Chai...", height=40, fg_color=self.card_color, border_color=self.border_color, text_color=self.text_main)
        e_unit.pack(fill="x", pady=(5, 0))

        col2 = ctk.CTkFrame(row2, fg_color="transparent")
        col2.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(col2, text="MỨC BÁO ĐỘNG HẾT KHO:", font=ctk.CTkFont(size=11, weight="bold"), text_color=self.text_sub).pack(anchor="w")
        e_warn = ctk.CTkEntry(col2, placeholder_text="e.g. 2.5", height=40, fg_color=self.card_color, border_color=self.border_color, text_color=self.text_main)
        e_warn.pack(fill="x", pady=(5, 0))

        row3 = ctk.CTkFrame(popup, fg_color="transparent")
        row3.pack(fill="x", padx=20, pady=15)
        col3 = ctk.CTkFrame(row3, fg_color="transparent")
        col3.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(col3, text="SỐ LƯỢNG NHẬP VÀO:", font=ctk.CTkFont(size=11, weight="bold"), text_color=self.text_sub).pack(anchor="w")
        e_qty = ctk.CTkEntry(col3, placeholder_text="e.g. 10", height=40, fg_color=self.card_color, border_color=self.border_color, text_color=self.text_main)
        e_qty.pack(fill="x", pady=(5, 0))

        col4 = ctk.CTkFrame(row3, fg_color="transparent")
        col4.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(col4, text="TỔNG TIỀN THANH TOÁN (VND):", font=ctk.CTkFont(size=11, weight="bold"), text_color=self.text_sub).pack(anchor="w")
        e_cost = ctk.CTkEntry(col4, placeholder_text="e.g. 1500000", height=40, fg_color=self.card_color, border_color=self.border_color, text_color=self.text_main)
        e_cost.pack(fill="x", pady=(5, 0))

        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=30)
        ctk.CTkButton(btn_frame, text="Đóng", fg_color="transparent", border_width=1, border_color=self.text_sub, text_color=self.text_main, hover_color="#333333", height=45, command=popup.destroy).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        def submit_add():
            success, msg = self.controller.add_item(e_name.get(), e_unit.get(), e_warn.get(), e_qty.get(), e_cost.get())
            if success:
                self.refresh_stock_list()
                popup.destroy()
            else:
                messagebox.showerror("Lỗi", msg, parent=popup)

        ctk.CTkButton(btn_frame, text="Thêm vào kho", fg_color=self.color_accent, hover_color="#D35400", text_color="white", height=45, font=ctk.CTkFont(weight="bold"), command=submit_add).pack(side="right", fill="x", expand=True, padx=(5, 0))

    def ui_edit_ingredient_popup(self, ing_id, name, unit, warn):
        popup = self.create_popup("Sửa Nguyên Liệu", "450x400")
        
        ctk.CTkLabel(popup, text="CHỈNH SỬA NGUYÊN LIỆU", font=ctk.CTkFont(size=18, weight="bold"), text_color=self.text_main).pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(popup, text="Bạn chỉ có thể đổi tên, đơn vị và mức báo động. Để đổi\nsố lượng hay giá tiền, vui lòng dùng chức năng Nhập Hàng.", justify="left", text_color=self.text_sub).pack(anchor="w", padx=20, pady=(0, 20))

        ctk.CTkLabel(popup, text="TÊN NGUYÊN LIỆU:", font=ctk.CTkFont(size=11, weight="bold"), text_color=self.text_sub).pack(anchor="w", padx=20)
        e_name = ctk.CTkEntry(popup, height=40, fg_color=self.card_color, border_color=self.border_color, text_color=self.text_main)
        e_name.insert(0, name)
        e_name.pack(fill="x", padx=20, pady=(5, 15))

        row2 = ctk.CTkFrame(popup, fg_color="transparent")
        row2.pack(fill="x", padx=20, pady=5)
        col1 = ctk.CTkFrame(row2, fg_color="transparent")
        col1.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(col1, text="ĐƠN VỊ ĐẾM:", font=ctk.CTkFont(size=11, weight="bold"), text_color=self.text_sub).pack(anchor="w")
        e_unit = ctk.CTkEntry(col1, height=40, fg_color=self.card_color, border_color=self.border_color, text_color=self.text_main)
        e_unit.insert(0, unit)
        e_unit.pack(fill="x", pady=(5, 0))

        col2 = ctk.CTkFrame(row2, fg_color="transparent")
        col2.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(col2, text="MỨC BÁO ĐỘNG:", font=ctk.CTkFont(size=11, weight="bold"), text_color=self.text_sub).pack(anchor="w")
        e_warn = ctk.CTkEntry(col2, height=40, fg_color=self.card_color, border_color=self.border_color, text_color=self.text_main)
        e_warn.insert(0, str(warn))
        e_warn.pack(fill="x", pady=(5, 0))

        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=30)
        ctk.CTkButton(btn_frame, text="Đóng", fg_color="transparent", border_width=1, border_color=self.text_sub, text_color=self.text_main, hover_color="#333333", height=45, command=popup.destroy).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        def submit_edit():
            success, msg = self.controller.update_item(ing_id, e_name.get().strip(), e_unit.get().strip(), e_warn.get().strip())
            if success:
                self.refresh_stock_list()
                popup.destroy()
            else:
                messagebox.showerror("Lỗi", msg, parent=popup)

        ctk.CTkButton(btn_frame, text="Lưu thay đổi", fg_color=self.color_accent, hover_color="#D35400", text_color="white", height=45, font=ctk.CTkFont(weight="bold"), command=submit_edit).pack(side="right", fill="x", expand=True, padx=(5, 0))

    def ui_delete_ingredient(self, ing_id, ing_name):
        msg = f"CẢNH BÁO: Xóa nguyên liệu '{ing_name}'?\n\nViệc này sẽ xóa sạch nguyên liệu này khỏi:\n1. Công thức của tất cả đồ uống đang dùng nó.\n2. Lịch sử chi phí nhập kho của món này trong quá khứ.\n\nNếu muốn giữ lại chi phí cũ, hãy Sửa mức báo động về 0 thay vì Xóa."
        if messagebox.askyesno("Xóa nguyên liệu thô", msg):
            self.controller.delete_item(ing_id)
            self.refresh_stock_list()

    def ui_restock_popup(self):
        items = self.controller.get_inventory()
        if not items:
            return messagebox.showwarning("Cảnh báo", "Kho trống. Vui lòng tạo nguyên liệu trước!")

        popup = self.create_popup("Nhập Thêm Nguyên Liệu", "450x450")

        ctk.CTkLabel(popup, text="NHẬP THÊM NGUYÊN LIỆU VÀO KHO", font=ctk.CTkFont(size=18, weight="bold"), text_color=self.text_main).pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(popup, text="Ghi nhận chứng từ nhập kho nguyên liệu thô để hệ thống\ntự động tính trung bình Đơn giá vốn mới.", justify="left", text_color=self.text_sub).pack(anchor="w", padx=20, pady=(0, 20))

        ctk.CTkLabel(popup, text="CHỌN NGUYÊN LIỆU NHẬP:", font=ctk.CTkFont(size=12, weight="bold"), text_color=self.text_sub).pack(anchor="w", padx=20)
        
        item_names = [f"{item[1]} ({item[2]})" for item in items]
        item_map = {f"{item[1]} ({item[2]})": item[0] for item in items}
        
        combo_item = ctk.CTkComboBox(popup, values=item_names, height=40, fg_color=self.card_color, border_color=self.border_color, text_color=self.text_main)
        combo_item.pack(fill="x", padx=20, pady=(5, 15))

        row2 = ctk.CTkFrame(popup, fg_color="transparent")
        row2.pack(fill="x", padx=20, pady=5)
        
        col1 = ctk.CTkFrame(row2, fg_color="transparent")
        col1.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(col1, text="SỐ LƯỢNG NHẬP THÊM:", font=ctk.CTkFont(size=12, weight="bold"), text_color=self.text_sub).pack(anchor="w")
        e_qty = ctk.CTkEntry(col1, placeholder_text="e.g. 5.5", height=40, fg_color=self.card_color, border_color=self.border_color, text_color=self.text_main)
        e_qty.pack(fill="x", pady=(5, 0))

        col2 = ctk.CTkFrame(row2, fg_color="transparent")
        col2.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(col2, text="TỔNG TIỀN THANH TOÁN:", font=ctk.CTkFont(size=12, weight="bold"), text_color=self.text_sub).pack(anchor="w")
        e_cost = ctk.CTkEntry(col2, placeholder_text="e.g. 120000", height=40, fg_color=self.card_color, border_color=self.border_color, text_color=self.text_main)
        e_cost.pack(fill="x", pady=(5, 0))

        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=30)
        
        ctk.CTkButton(btn_frame, text="Bỏ qua", fg_color="transparent", border_width=1, border_color=self.text_sub, text_color=self.text_main, hover_color="#333333", height=45, command=popup.destroy).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        def submit_restock():
            ing_id = item_map.get(combo_item.get())
            success, msg = self.controller.restock_item(ing_id, e_qty.get().strip(), e_cost.get().strip())
            if success:
                self.refresh_stock_list()
                popup.destroy()
            else:
                messagebox.showerror("Lỗi", msg, parent=popup)

        ctk.CTkButton(btn_frame, text="Cập nhật hóa đơn", fg_color=self.color_accent, hover_color="#D35400", text_color="white", height=45, font=ctk.CTkFont(weight="bold"), command=submit_restock).pack(side="right", fill="x", expand=True, padx=(5, 0))

    def ui_sync_stock_popup(self):
        items = self.controller.get_inventory()
        if not items:
            return messagebox.showwarning("Cảnh báo", "Kho trống, không có gì để kiểm!")

        popup = self.create_popup("Kiểm Kho Thực Tế", "700x600")

        ctk.CTkLabel(popup, text="KIỂM KHO VÀ ĐỐI CHIẾU HAO HỤT THỰC TẾ", font=ctk.CTkFont(size=18, weight="bold"), text_color=self.text_main).pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(popup, text="Hãy nhập số lượng 'Tồn thực tế' mà bạn đếm được dưới đây. Hệ thống tự so\nsánh chênh lệch lý thuyết và tính toán hao hụt.", justify="left", text_color=self.text_sub).pack(anchor="w", padx=20, pady=(0, 15))

        scroll_frame = ctk.CTkScrollableFrame(popup, fg_color=self.card_color, corner_radius=8, border_width=1, border_color=self.border_color)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        entry_list = [] 

        for item in items:
            i_id, i_name, i_unit, i_theory, _, _, _ = item
            i_theory = float(i_theory or 0)

            row = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            row.pack(fill="x", pady=10, padx=10)

            info_frame = ctk.CTkFrame(row, fg_color="transparent")
            info_frame.pack(side="left")
            ctk.CTkLabel(info_frame, text=f"{i_name} ({i_unit})", font=ctk.CTkFont(weight="bold"), text_color=self.text_main).pack(anchor="w")
            ctk.CTkLabel(info_frame, text=f"Tồn lý thuyết: {i_theory:g} {i_unit}", text_color=self.text_sub, font=ctk.CTkFont(size=12)).pack(anchor="w")

            lbl_status = ctk.CTkLabel(row, text="Cân bằng", text_color=self.text_sub, font=ctk.CTkFont(slant="italic", size=12))
            lbl_status.pack(side="right", padx=10)

            var_actual = ctk.StringVar(value=f"{i_theory:g}") 
            entry = ctk.CTkEntry(row, textvariable=var_actual, width=120, height=35, justify="center", fg_color=self.bg_color, border_color=self.border_color, text_color=self.text_main)
            entry.pack(side="right", padx=10)
            
            entry_list.append({"id": i_id, "theory": i_theory, "var": var_actual, "lbl": lbl_status})

            def calc_diff_popup(*args, theo=i_theory, var=var_actual, lbl=lbl_status):
                try:
                    act = float(var.get())
                    diff = round(act - theo, 3) # Fix float precision
                    if diff == 0:
                        lbl.configure(text="Cân bằng", text_color=self.text_sub)
                    elif diff < 0:
                        lbl.configure(text=f"Lệch: {diff:g}", text_color="#E74C3C")
                    else:
                        lbl.configure(text=f"Dư: +{diff:g}", text_color="#2ECC71")
                except ValueError:
                    lbl.configure(text="Lỗi số", text_color="#E74C3C")

            var_actual.trace_add("write", calc_diff_popup)

            ctk.CTkFrame(scroll_frame, height=1, fg_color=self.border_color).pack(fill="x", padx=10)

        ctk.CTkLabel(popup, text="LÝ DO ĐIỀU CHỈNH (Áp dụng chung nếu có lệch):", font=ctk.CTkFont(size=12, weight="bold"), text_color=self.text_sub).pack(anchor="w", padx=20, pady=(10, 0))
        e_reason_common = ctk.CTkEntry(popup, placeholder_text="e.g. Kiểm kho định kỳ cuối tuần...", height=40, fg_color=self.card_color, border_color=self.border_color, text_color=self.text_main)
        e_reason_common.pack(fill="x", padx=20, pady=(5, 10))

        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        ctk.CTkButton(btn_frame, text="Hủy bỏ phiếu kiểm", fg_color="transparent", border_width=1, border_color=self.text_sub, text_color=self.text_main, hover_color="#333333", height=45, command=popup.destroy).pack(side="left", fill="x", expand=True, padx=(0, 5))

        def submit_sync_all():
            reason = e_reason_common.get().strip()
            has_error = False
            has_diff = False
            
            for item in entry_list:
                try:
                    act = float(item["var"].get())
                    if act != item["theory"]:
                        has_diff = True
                        if not reason:
                            has_error = True
                            break
                        self.controller.sync_stock(item["id"], item["theory"], act, reason)
                except ValueError:
                    continue 

            if has_error:
                messagebox.showerror("Thiếu thông tin", "Phát hiện có chênh lệch tồn kho. Bắt buộc phải nhập LÝ DO ĐIỀU CHỈNH chung ở dưới cùng!", parent=popup)
                return

            if not has_diff:
                messagebox.showinfo("Hoàn tất", "Tất cả hàng hóa đều khớp với lý thuyết. Không có chênh lệch nào được lưu.", parent=popup)
            
            self.refresh_stock_list()
            popup.destroy()

        ctk.CTkButton(btn_frame, text="Cập nhật kho thực tế & Lưu lịch sử", fg_color=self.color_accent, hover_color="#D35400", text_color="white", height=45, font=ctk.CTkFont(weight="bold"), command=submit_sync_all).pack(side="right", fill="x", expand=True, padx=(5, 0))