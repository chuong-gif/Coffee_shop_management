import customtkinter as ctk
import tkinter.messagebox as messagebox
from src.controllers.stock_controller import StockController

class PageStock(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.controller = StockController()

        # ==========================================
        # 1. HEADER & CỤM NÚT CHỨC NĂNG TỔNG
        # ==========================================
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=(10, 5))

        # Tiêu đề bên trái
        self.title_group = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.title_group.pack(side="left")
        ctk.CTkLabel(self.title_group, text="QUẢN LÝ KHO NGUYÊN LIỆU THÔ", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(self.title_group, text="Theo dõi tồn lý thuyết song song với tồn thực tế, quản lý chênh lệch hao hụt.", font=ctk.CTkFont(size=13), text_color="gray").pack(anchor="w")

        # Cụm 3 nút bên phải
        self.btn_group = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.btn_group.pack(side="right", fill="y", pady=5)

        self.btn_add = ctk.CTkButton(self.btn_group, text="+ Thêm nguyên liệu thô", fg_color="#009432", hover_color="#006266", command=self.ui_add_ingredient_popup)
        self.btn_add.pack(side="left", padx=5)

        self.btn_audit = ctk.CTkButton(self.btn_group, text="🔄 Kiểm kho (Định mức thực tế)", fg_color="#E67E22", hover_color="#D35400", command=self.ui_sync_stock_popup)
        self.btn_audit.pack(side="left", padx=5)

        self.btn_restock = ctk.CTkButton(self.btn_group, text="+ Nhập thêm nguyên liệu", fg_color="transparent", border_width=1, text_color=("black", "white"), command=self.ui_restock_popup)
        self.btn_restock.pack(side="left", padx=5)

        # ==========================================
        # 2. BANNER THÔNG BÁO (INFO BANNER)
        # ==========================================
        self.banner_frame = ctk.CTkFrame(self, fg_color=("#FDFEFE", "#2C3E50"), border_width=1, border_color="#D5D8DC", corner_radius=8)
        self.banner_frame.pack(fill="x", padx=20, pady=(10, 15))
        ctk.CTkLabel(self.banner_frame, text="ⓘ Cơ chế tự động: Mỗi ly bán hàng thành công ở trang 1 sẽ trừ thô nguyên vật liệu tương ứng. Nhân viên nên đếm tồn kho thực tế định kỳ.", font=ctk.CTkFont(size=13), text_color="#E67E22").pack(anchor="w", padx=15, pady=10)

        # ==========================================
        # 3. LƯỚI QUẢN LÝ KHO CHÍNH (MAIN GRID)
        # ==========================================
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color=("white", "#1E1E1E"), corner_radius=8, border_width=1, border_color="#E5E8E8")
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # ==========================================
        # 4. KHUNG LỊCH SỬ CHÊNH LỆCH
        # ==========================================
        self.history_frame = ctk.CTkFrame(self, fg_color=("white", "#1E1E1E"), corner_radius=8, border_width=1, border_color="#E5E8E8", height=250)
        self.history_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Tải dữ liệu lần đầu
        self.refresh_stock_list()

    # ==========================================
    # CÁC HÀM RENDER UI (VẼ GIAO DIỆN)
    # ==========================================
    def format_currency(self, amount):
        """Hàm tiện ích để format tiền tệ chuẩn Việt Nam"""
        return f"{amount:,.0f} đ".replace(",", ".")

    def refresh_stock_list(self):
        """Vẽ lại bảng danh sách tồn kho chính"""
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        items = self.controller.get_inventory()

        # Header của bảng Kho
        header = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        header.pack(fill="x", pady=(5, 10))
        
        headers = [
            ("MÃ NL", 80), ("TÊN NGUYÊN LIỆU", 220), ("TỒN LÝ THUYẾT", 120), 
            ("TỒN THỰC TẾ ĐẾM", 130), ("ĐƠN GIÁ VỐN NHẬP", 140), 
            ("TỔNG GIÁ TRỊ TỒN THỰC", 160), ("TRẠNG THÁI", 100)
        ]
        for col_name, col_width in headers:
            ctk.CTkLabel(header, text=col_name, width=col_width, anchor="w", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray").pack(side="left", padx=5)

        ctk.CTkFrame(self.list_frame, height=1, fg_color="#E5E8E8").pack(fill="x", pady=2) # Line phân cách

        # Render từng dòng nguyên liệu
        for item in items:
            i_id, i_name, i_unit, i_theory, i_actual, i_warn, i_cost = item
            
            # Format số liệu
            i_theory, i_actual, i_warn, i_cost = float(i_theory or 0), float(i_actual or 0), float(i_warn or 0), float(i_cost or 0)
            total_val = i_actual * i_cost
            is_warning = i_actual <= i_warn or i_theory <= i_warn

            row = ctk.CTkFrame(self.list_frame, fg_color="transparent")
            row.pack(fill="x", pady=8)

            # Mã NL (Tự render dạng NL_001)
            ctk.CTkLabel(row, text=f"NL_{i_id:03d}", width=80, anchor="w", text_color="gray").pack(side="left", padx=5)
            
            # Tên & Cảnh báo nhỏ
            name_frame = ctk.CTkFrame(row, width=220, fg_color="transparent")
            name_frame.pack(side="left", padx=5, fill="y")
            name_frame.pack_propagate(False)
            ctk.CTkLabel(name_frame, text=i_name, anchor="w", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
            ctk.CTkLabel(name_frame, text=f"Mức an toàn tối thiểu: {i_warn:g} {i_unit}", anchor="w", font=ctk.CTkFont(size=11), text_color="gray").pack(anchor="w")

            # Tồn kho
            ctk.CTkLabel(row, text=f"{i_theory:g} {i_unit}", width=120, anchor="w", text_color="gray").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=f"{i_actual:g} {i_unit}", width=130, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            
            # Đơn giá & Tổng trị giá
            ctk.CTkLabel(row, text=f"{self.format_currency(i_cost)} / {i_unit}", width=140, anchor="w", text_color="gray").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=self.format_currency(total_val), width=160, anchor="w", text_color="#E74C3C", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)

            # Trạng thái (Pill)
            status_text = "⚠ BÁO ĐỘNG" if is_warning else "✔ AN TOÀN"
            status_color = "#E74C3C" if is_warning else "#2ECC71"
            pill = ctk.CTkLabel(row, text=status_text, width=100, height=24, fg_color="transparent", text_color=status_color, font=ctk.CTkFont(size=11, weight="bold"))
            pill.pack(side="left", padx=5)

            ctk.CTkFrame(self.list_frame, height=1, fg_color="#F2F3F4").pack(fill="x", pady=2) # Line phân cách mỏng

        if not items:
            ctk.CTkLabel(self.list_frame, text="Kho đang trống. Hãy thêm nguyên vật liệu mới.", text_color="gray").pack(pady=40)

        self.render_history()

    def render_history(self):
        """Vẽ lại bảng lịch sử chênh lệch ở dưới cùng"""
        ctk.CTkLabel(self.history_frame, text="LỊCH SỬ CHÊNH LỆCH & HAO HỤT THỰC TẾ", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(15, 10))
        
        hist_scroll = ctk.CTkScrollableFrame(self.history_frame, fg_color="transparent", height=180)
        hist_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        header = ctk.CTkFrame(hist_scroll, fg_color="transparent")
        header.pack(fill="x", pady=2)
        
        h_cols = [("THỜI GIAN GHI NHẬN", 150), ("TÊN NGUYÊN LIỆU", 200), ("LÝ THUYẾT", 90), ("THỰC TẾ", 90), ("LỆCH HAO HỤT", 100), ("LÝ DO ĐIỀU CHỈNH", 250)]
        for col_name, col_width in h_cols:
            ctk.CTkLabel(header, text=col_name, width=col_width, anchor="w", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray").pack(side="left", padx=5)

        history_items = self.controller.get_stock_history(limit=10)
        for h_id, name, theo, actual, diff, reason, time_stamp in history_items:
            row = ctk.CTkFrame(hist_scroll, fg_color="transparent")
            row.pack(fill="x", pady=5)
            
            ctk.CTkLabel(row, text=time_stamp, width=150, anchor="w", text_color="gray").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=name, width=200, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=f"{theo:g}", width=90, anchor="w", text_color="gray").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=f"{actual:g}", width=90, anchor="w").pack(side="left", padx=5)
            
            diff_color = "#E74C3C" if diff < 0 else "#2ECC71" if diff > 0 else "gray"
            ctk.CTkLabel(row, text=f"{diff:g}", width=100, anchor="w", text_color=diff_color, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=reason or "-", width=250, anchor="w", text_color="gray").pack(side="left", padx=5)
            ctk.CTkFrame(hist_scroll, height=1, fg_color="#F2F3F4").pack(fill="x")

    # ==========================================
    # CÁC HÀM POP-UP (TOPLEVEL) TƯƠNG TÁC
    # ==========================================
    def create_popup(self, title, size):
        """Hàm tiện ích tạo khung cửa sổ Pop-up chuẩn"""
        popup = ctk.CTkToplevel(self)
        popup.title(title)
        popup.geometry(size)
        popup.attributes("-topmost", True) # Giữ popup nổi lên trên
        popup.grab_set() # Khóa cửa sổ chính cho đến khi đóng popup
        return popup

    def ui_add_ingredient_popup(self):
        """Pop-up 1: Thêm nguyên liệu thô mới"""
        popup = self.create_popup("Thêm Nguyên Liệu Thô", "450x550")
        
        ctk.CTkLabel(popup, text="THÊM NGUYÊN LIỆU THÔ MỚI", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(popup, text="Cấu hình thông số định mức tối thiểu và đơn giá vốn\nđể hệ thống ghi nhận hao hụt và cảnh báo.", justify="left", text_color="gray").pack(anchor="w", padx=20, pady=(0, 20))

        # Khung nhập liệu
        ctk.CTkLabel(popup, text="TÊN NGUYÊN LIỆU THÔ:", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray").pack(anchor="w", padx=20)
        e_name = ctk.CTkEntry(popup, placeholder_text="e.g. Hạt Cà Phê Robusta Buôn Ma Thuột", height=40)
        e_name.pack(fill="x", padx=20, pady=(5, 15))

        row2 = ctk.CTkFrame(popup, fg_color="transparent")
        row2.pack(fill="x", padx=20, pady=5)
        
        col1 = ctk.CTkFrame(row2, fg_color="transparent")
        col1.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(col1, text="ĐƠN VỊ ĐẾM (UNIT):", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray").pack(anchor="w")
        e_unit = ctk.CTkEntry(col1, placeholder_text="Kg, Hộp, Chai...", height=40)
        e_unit.pack(fill="x", pady=(5, 0))

        col2 = ctk.CTkFrame(row2, fg_color="transparent")
        col2.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(col2, text="HẠN MỨC TỐI THIỂU (MIN):", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray").pack(anchor="w")
        e_warn = ctk.CTkEntry(col2, placeholder_text="e.g. 2.5", height=40)
        e_warn.pack(fill="x", pady=(5, 0))

        ctk.CTkLabel(popup, text="ĐƠN GIÁ VỐN CƠ BẢN (Đ/ĐƠN VỊ):", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray").pack(anchor="w", padx=20, pady=(15, 5))
        e_cost = ctk.CTkEntry(popup, placeholder_text="e.g. 150000", height=40)
        e_cost.pack(fill="x", padx=20, pady=(0, 25))

        # Nút xác nhận
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(btn_frame, text="Đóng", fg_color="transparent", border_width=1, text_color=("black", "white"), height=45, command=popup.destroy).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        def submit_add():
            # Tạm thời gán quantity = 0, note rỗng vì đây là định mức
            success, msg = self.controller.add_item(e_name.get(), 0, e_unit.get(), e_cost.get(), "")
            if success:
                self.refresh_stock_list()
                popup.destroy()
            else:
                messagebox.showerror("Lỗi", msg, parent=popup)

        ctk.CTkButton(btn_frame, text="Thêm nguyên liệu thô", fg_color="#E67E22", hover_color="#D35400", height=45, font=ctk.CTkFont(weight="bold"), command=submit_add).pack(side="right", fill="x", expand=True, padx=(5, 0))

    def ui_restock_popup(self):
        """Pop-up 2: Nhập hàng hóa vào kho"""
        items = self.controller.get_inventory()
        if not items:
            return messagebox.showwarning("Cảnh báo", "Kho trống. Vui lòng tạo nguyên liệu trước!")

        popup = self.create_popup("Nhập Thêm Nguyên Liệu", "450x450")

        ctk.CTkLabel(popup, text="NHẬP THÊM NGUYÊN LIỆU VÀO KHO", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(popup, text="Ghi nhận chứng từ nhập kho nguyên liệu thô để cập\nnhật đơn giá vốn trung bình và số lượng tồn.", justify="left", text_color="gray").pack(anchor="w", padx=20, pady=(0, 20))

        ctk.CTkLabel(popup, text="CHỌN NGUYÊN LIỆU NHẬP:", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray").pack(anchor="w", padx=20)
        
        # Tạo danh sách Tên để đưa vào ComboBox, và dictionary map Tên -> ID
        item_names = [f"{item[1]} ({item[2]})" for item in items]
        item_map = {f"{item[1]} ({item[2]})": item[0] for item in items}
        
        combo_item = ctk.CTkComboBox(popup, values=item_names, height=40)
        combo_item.pack(fill="x", padx=20, pady=(5, 15))

        row2 = ctk.CTkFrame(popup, fg_color="transparent")
        row2.pack(fill="x", padx=20, pady=5)
        
        col1 = ctk.CTkFrame(row2, fg_color="transparent")
        col1.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(col1, text="SỐ LƯỢNG NHẬP:", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray").pack(anchor="w")
        e_qty = ctk.CTkEntry(col1, placeholder_text="e.g. 5.5", height=40)
        e_qty.pack(fill="x", pady=(5, 0))

        col2 = ctk.CTkFrame(row2, fg_color="transparent")
        col2.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(col2, text="TỔNG TIỀN NHẬP (VND):", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray").pack(anchor="w")
        e_cost = ctk.CTkEntry(col2, placeholder_text="e.g. 120000", height=40)
        e_cost.pack(fill="x", pady=(5, 0))

        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=30)
        
        ctk.CTkButton(btn_frame, text="Bò qua", fg_color="transparent", border_width=1, text_color=("black", "white"), height=45, command=popup.destroy).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        def submit_restock():
            selected_name = combo_item.get()
            ing_id = item_map.get(selected_name)
            
            qty, cost = e_qty.get().strip(), e_cost.get().strip()
            if not qty or not qty.replace('.', '', 1).isdigit():
                return messagebox.showerror("Lỗi", "Số lượng nhập không hợp lệ", parent=popup)

            success, msg = self.controller.restock_item(ing_id, qty, cost)
            if success:
                self.refresh_stock_list()
                popup.destroy()
            else:
                messagebox.showerror("Lỗi", msg, parent=popup)

        ctk.CTkButton(btn_frame, text="Cập nhật hóa đơn nhập", fg_color="#E67E22", hover_color="#D35400", height=45, font=ctk.CTkFont(weight="bold"), command=submit_restock).pack(side="right", fill="x", expand=True, padx=(5, 0))

    def ui_sync_stock_popup(self):
        """Pop-up 3: Phiếu Kiểm Kho & Báo Cáo Chênh Lệch"""
        items = self.controller.get_inventory()
        if not items:
            return messagebox.showwarning("Cảnh báo", "Kho trống, không có gì để kiểm!")

        popup = self.create_popup("Kiểm Kho Thực Tế", "700x600")

        ctk.CTkLabel(popup, text="KIỂM KHO VÀ ĐỐI CHIẾU HAO HỤT THỰC TẾ", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(popup, text="Hãy nhập số lượng 'Tồn thực tế' mà bạn đếm được dưới đây. Hệ thống tự so\nsánh chênh lệch lý thuyết và tính toán hao hụt.", justify="left", text_color="gray").pack(anchor="w", padx=20, pady=(0, 15))

        # Khu vực cuộn chứa các dòng nguyên liệu để điền
        scroll_frame = ctk.CTkScrollableFrame(popup, fg_color=("white", "#1E1E1E"), corner_radius=8, border_width=1, border_color="#E5E8E8")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Danh sách chứa các biến Entry để lát nữa thu thập dữ liệu
        entry_list = [] 

        for item in items:
            i_id, i_name, i_unit, i_theory, _, _, _ = item
            i_theory = float(i_theory or 0)

            row = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            row.pack(fill="x", pady=10, padx=10)

            # Info cột trái
            info_frame = ctk.CTkFrame(row, fg_color="transparent")
            info_frame.pack(side="left")
            ctk.CTkLabel(info_frame, text=f"{i_name} ({i_unit})", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
            ctk.CTkLabel(info_frame, text=f"Tồn lý thuyết: {i_theory:g} {i_unit}", text_color="gray", font=ctk.CTkFont(size=12)).pack(anchor="w")

            # Label "Cân bằng" bên phải cùng
            lbl_status = ctk.CTkLabel(row, text="Cân bằng", text_color="gray", font=ctk.CTkFont(slant="italic", size=12))
            lbl_status.pack(side="right", padx=10)

            # Ô nhập số liệu
            var_actual = ctk.StringVar(value=f"{i_theory:g}") # Mặc định gán bằng lý thuyết
            entry = ctk.CTkEntry(row, textvariable=var_actual, width=120, height=35, justify="center")
            entry.pack(side="right", padx=10)
            
            # Ghi nhớ id, tồn cũ, biến value, label trạng thái
            entry_list.append({
                "id": i_id, 
                "theory": i_theory,
                "var": var_actual,
                "lbl": lbl_status
            })

            # Tính realtime cho Popup
            def calc_diff_popup(*args, theo=i_theory, var=var_actual, lbl=lbl_status):
                try:
                    act = float(var.get())
                    diff = act - theo
                    if diff == 0:
                        lbl.configure(text="Cân bằng", text_color="gray")
                    elif diff < 0:
                        lbl.configure(text=f"Lệch: {diff:g}", text_color="#E74C3C")
                    else:
                        lbl.configure(text=f"Dư: +{diff:g}", text_color="#2ECC71")
                except ValueError:
                    lbl.configure(text="Lỗi số", text_color="#E74C3C")

            var_actual.trace_add("write", calc_diff_popup)

            ctk.CTkFrame(scroll_frame, height=1, fg_color="#F2F3F4").pack(fill="x", padx=10)

        # Lý do kiểm kho chung
        ctk.CTkLabel(popup, text="LÝ DO ĐIỀU CHỈNH (Áp dụng chung nếu có lệch):", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray").pack(anchor="w", padx=20, pady=(10, 0))
        e_reason_common = ctk.CTkEntry(popup, placeholder_text="e.g. Kiểm kho định kỳ cuối tuần, hao hụt do rách bao bì...", height=40)
        e_reason_common.pack(fill="x", padx=20, pady=(5, 10))

        # Nút xác nhận lưu hàng loạt
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        ctk.CTkButton(btn_frame, text="Hủy bỏ phiếu kiểm", fg_color="transparent", border_width=1, text_color=("black", "white"), height=45, command=popup.destroy).pack(side="left", fill="x", expand=True, padx=(0, 5))

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
                        # Gọi hàm lưu từng món bị lệch
                        self.controller.sync_stock(item["id"], item["theory"], act, reason)
                except ValueError:
                    continue # Bỏ qua ô bị lỗi chữ

            if has_error:
                messagebox.showerror("Thiếu thông tin", "Phát hiện có chênh lệch tồn kho. Bắt buộc phải nhập LÝ DO ĐIỀU CHỈNH chung ở dưới cùng!", parent=popup)
                return

            if not has_diff:
                messagebox.showinfo("Hoàn tất", "Tất cả hàng hóa đều khớp với lý thuyết. Không có chênh lệch nào được lưu.", parent=popup)
            
            self.refresh_stock_list()
            popup.destroy()

        ctk.CTkButton(btn_frame, text="Cập nhật kho thực tế & Lưu lịch sử", fg_color="#E67E22", hover_color="#D35400", height=45, font=ctk.CTkFont(weight="bold"), command=submit_sync_all).pack(side="right", fill="x", expand=True, padx=(5, 0))