import tkinter as tk
import customtkinter as ctk
import tkinter.messagebox as messagebox
from PIL import Image
import os
import datetime
from src.utils import session
from tkcalendar import DateEntry
 
class LeftPane(ctk.CTkFrame):
    def __init__(self, master, controller, on_table_select, on_item_add):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.on_table_select = on_table_select 
        self.on_item_add = on_item_add         
 
        self.current_category = "Tất cả"
        self.selected_table_id = None
 
        # Bảng màu
        self.card_color = "#212121"
        self.border_color = "#333333"
        self.color_empty = "#196F3D"
        self.color_occupied = "#922B21"
        self.color_accent = "#E67E22"
 
        # [FIX]: Tăng kích thước tối thiểu và đặt mặc định
        self.min_table_card_w = 120
        self.min_menu_card_w = 230  # Tăng lên 230px để thẻ món ăn rộng rãi hơn
        self.table_cols = 4
        self.menu_cols = 4  
        self._resize_jobs = {}
 
        self.build_ui()
 
    def build_ui(self):
        self.v_paned = tk.PanedWindow(
            self, orient="vertical", sashwidth=6, sashrelief="flat",
            bg="#121212", bd=0, opaqueresize=True
        )
        self.v_paned.pack(fill="both", expand=True)
 
        # --- BÀN ---
        self.table_card = ctk.CTkFrame(self.v_paned, fg_color=self.card_color, corner_radius=8, border_width=1, border_color=self.border_color)
 
        t_header = ctk.CTkFrame(self.table_card, fg_color="transparent")
        t_header.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(t_header, text="SƠ ĐỒ BÀN KHÁCH", font=ctk.CTkFont(size=14, weight="bold"), text_color="white").pack(side="left")
        
        # [TÍNH NĂNG MỚI]: Thêm nút sửa mẫu hóa đơn
        ctk.CTkButton(t_header, text="+ Thiết lập bàn", width=90, height=24, fg_color="transparent", border_width=1, border_color=self.color_accent, text_color=self.color_accent, hover_color="#3E2723", command=self.ui_add_table_popup).pack(side="left", padx=(15, 5))
        ctk.CTkButton(t_header, text="🧾 Mẫu hóa đơn", width=90, height=24, fg_color="transparent", border_width=1, border_color="#3498DB", text_color="#3498DB", hover_color="#1A5276", command=self.ui_receipt_template_popup).pack(side="left", padx=5)

        # [TÍNH NĂNG MỚI]: Nút quản lý Mã giảm giá (Chỉ hiện nếu có quyền)
        if session.current_user.get("quyen_ma_giam_gia", 0) == 1:
            ctk.CTkButton(t_header, text="🎟️ Mã giảm giá", width=90, height=24, fg_color="transparent", border_width=1, border_color="#9B59B6", text_color="#9B59B6", hover_color="#5B2C6F", command=self.ui_discount_popup).pack(side="left", padx=5)


        legend_frame = ctk.CTkFrame(t_header, fg_color="transparent")
        legend_frame.pack(side="right")
        self.lbl_legend_trong = ctk.CTkLabel(legend_frame, text="🟢 Trống", text_color="#AAAAAA", font=ctk.CTkFont(size=11))
        self.lbl_legend_trong.pack(side="left", padx=5)
        self.lbl_legend_khach = ctk.CTkLabel(legend_frame, text="🔴 Có khách", text_color="#AAAAAA", font=ctk.CTkFont(size=11))
        self.lbl_legend_khach.pack(side="left", padx=5)
 
        self.table_grid = ctk.CTkScrollableFrame(self.table_card, fg_color="transparent")
        self.table_grid.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.table_grid.bind("<Configure>", self._on_table_grid_resize)
 
        self.v_paned.add(self.table_card, minsize=170, stretch="always")
 
        # --- KHU DƯỚI: Mang về + Menu ---
        self.bottom_frame = ctk.CTkFrame(self.v_paned, fg_color="transparent")
 
        self.btn_takeaway = ctk.CTkButton(self.bottom_frame, text="🛍  MANG VỀ\nXử lý nhanh đơn mang đi, không thuộc sơ đồ bàn",
                                          height=60, fg_color=self.card_color, text_color="white", border_width=1, border_color=self.border_color,
                                          hover_color="#333333", font=ctk.CTkFont(weight="bold"), command=lambda: self.on_table_select(None, "Đơn Mang Về"))
        self.btn_takeaway.pack(fill="x", pady=(0, 10))
 
        self.menu_card = ctk.CTkFrame(self.bottom_frame, fg_color=self.card_color, corner_radius=8, border_width=1, border_color=self.border_color)
        self.menu_card.pack(fill="both", expand=True)
 
        m_header = ctk.CTkFrame(self.menu_card, fg_color="transparent")
        m_header.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(m_header, text="CHỌN MÓN VÀO HÓA ĐƠN", font=ctk.CTkFont(size=14, weight="bold"), text_color="white").pack(side="left")
 
        self.cat_scroll = ctk.CTkScrollableFrame(m_header, orientation="horizontal", height=30, fg_color="transparent")
        self.cat_scroll.pack(side="right", fill="x", expand=True, padx=(20, 0))
 
        self.menu_list_frame = ctk.CTkScrollableFrame(self.menu_card, fg_color="transparent")
        self.menu_list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.menu_list_frame.bind("<Configure>", self._on_menu_grid_resize)
 
        self.v_paned.add(self.bottom_frame, minsize=280, stretch="always")
 
        self._v_sash_initialized = False
        self.v_paned.bind("<Configure>", self._on_v_paned_configure)
 
    def _on_v_paned_configure(self, event):
        if not self._v_sash_initialized and event.height > 200:
            self._v_sash_initialized = True
            self.after(10, lambda h=event.height: self._set_initial_v_sash(h))
 
    def _set_initial_v_sash(self, height=None):
        try:
            h = height or self.v_paned.winfo_height()
            if h > 100:
                self.v_paned.sash_place(0, 0, int(h * 0.42))
        except Exception:
            pass
 
    def _debounced(self, key, delay_ms, func):
        job = self._resize_jobs.get(key)
        if job:
            self.after_cancel(job)
        self._resize_jobs[key] = self.after(delay_ms, func)
 
    def _on_table_grid_resize(self, event):
        width = event.width
        self._debounced("table", 150, lambda: self._recompute_table_cols(width))
 
    def _on_menu_grid_resize(self, event):
        width = event.width
        self._debounced("menu", 150, lambda: self._recompute_menu_cols(width))
 
    def _recompute_table_cols(self, width):
        # Trừ hao 40px vùng an toàn cho thanh cuộn (scrollbar) và lề 2 bên
        safe_width = width - 40
        # [SMART LIMIT]: Giới hạn số cột bàn - Tối thiểu 2, tối đa 7
        cols = max(2, min(7, safe_width // self.min_table_card_w))
        if cols != self.table_cols:
            self.table_cols = cols
            self.refresh_tables()
 
    def _recompute_menu_cols(self, width):
        # Trừ hao 40px vùng an toàn
        safe_width = width - 40
        # [SMART LIMIT]: Giới hạn số cột món ăn - Tối thiểu 2, tối đa 4
        cols = max(2, min(4, safe_width // self.min_menu_card_w))
        if cols != self.menu_cols:
            self.menu_cols = cols
            self.refresh_menu()
 
    # --- RENDER ---
    def refresh_tables(self):
        for widget in self.table_grid.winfo_children(): widget.destroy()
        tables = self.controller.get_tables_data()
 
        self.lbl_legend_trong.configure(text=f"🟢 Trống ({sum(1 for t in tables if t[2] == 'Trống')})")
        self.lbl_legend_khach.configure(text=f"🔴 Có khách ({sum(1 for t in tables if t[2] == 'Có khách')})")
 
        cols = self.table_cols
        for c in range(cols):
            self.table_grid.grid_columnconfigure(c, weight=1)
        for i, table in enumerate(tables):
            t_id, t_name, t_status = table
            row_idx, col_idx = i // cols, i % cols
            is_selected = (t_id == self.selected_table_id)
 
            bg = self.color_occupied if t_status == "Có khách" else self.color_empty
            border = self.color_accent if is_selected else bg
 
            card = ctk.CTkFrame(self.table_grid, fg_color=bg, corner_radius=6, border_width=2 if is_selected else 0, border_color=border, height=80)
            card.grid(row=row_idx, column=col_idx, padx=5, pady=5, sticky="nsew")
            card.pack_propagate(False)
 
            def click_ev(event, tid=t_id, tname=t_name):
                self.selected_table_id = tid
                self.refresh_tables() 
                self.on_table_select(tid, tname)
 
            card.bind("<Button-1>", click_ev)
            lbl = ctk.CTkLabel(card, text=f"{t_name}\n({t_status})", font=ctk.CTkFont(size=12, weight="bold"), text_color="white")
            lbl.place(relx=0.5, rely=0.4, anchor="center")
            lbl.bind("<Button-1>", click_ev)
 
            # Đặt khung icon xuống góc dưới bên phải (se), nền hoàn toàn trong suốt
            icon_row = ctk.CTkFrame(card, fg_color="transparent")
            icon_row.place(relx=1.0, rely=1.0, anchor="se", x=-5, y=-5)
            
            # Nút Cài đặt (Sửa) - Đổi sang icon bánh răng, ẩn viền
            ctk.CTkButton(icon_row, text="⚙", width=24, height=24, fg_color="transparent", 
                          hover_color="#333333", text_color="#BDC3C7", font=ctk.CTkFont(size=14),
                          command=lambda tid=t_id, tname=t_name: self.ui_rename_table_popup(tid, tname)).pack(side="left")
            
            # Nút Xóa - Nền trong suốt, khi hover mới hiện màu đỏ
            ctk.CTkButton(icon_row, text="✖", width=24, height=24, fg_color="transparent", 
                          hover_color="#E74C3C", text_color="#BDC3C7", font=ctk.CTkFont(size=12),
                          command=lambda tid=t_id, tname=t_name: self.ui_delete_table_confirm(tid, tname)).pack(side="left")
 
    def refresh_menu(self):
        for widget in self.cat_scroll.winfo_children(): widget.destroy()
        categories = ["Tất cả"] + list(set(item[3] for item in self.controller.menu_model.get_available_menu()))
 
        for cat in categories:
            color = self.color_accent if cat == self.current_category else "transparent"
            t_color = "white" if cat == self.current_category else "#AAAAAA"
            ctk.CTkButton(self.cat_scroll, text=cat, fg_color=color, text_color=t_color, corner_radius=15, height=24,
                          command=lambda c=cat: self.set_category(c)).pack(side="left", padx=5)
 
        for widget in self.menu_list_frame.winfo_children(): widget.destroy()
        filtered_menu = [item for item in self.controller.menu_model.get_available_menu() if self.current_category == "Tất cả" or item[3] == self.current_category]
 
        cols = self.menu_cols
        for c in range(cols):
            self.menu_list_frame.grid_columnconfigure(c, weight=1)
        for i, item in enumerate(filtered_menu):
            d_id, _, ten_mon, phan_loai, gia_ban, _, hinh_anh = item
            card = ctk.CTkFrame(self.menu_list_frame, fg_color="#121212", corner_radius=8, border_width=1, border_color="#333333", height=80)
            card.grid(row=i // cols, column=i % cols, padx=5, pady=5, sticky="nsew")
            card.pack_propagate(False)
 
            # 1. Xếp hình ảnh bên Trái
            img_obj = self.get_image(hinh_anh)
            if img_obj:
                ctk.CTkLabel(card, image=img_obj, text="").pack(side="left", padx=10, pady=10)
            else:
                icon = ctk.CTkFrame(card, width=40, height=40, corner_radius=8, fg_color=f"#{abs(hash(phan_loai)) % 0xFFFFFF:06x}")
                icon.pack(side="left", padx=10, pady=10)
                icon.pack_propagate(False)
                ctk.CTkLabel(icon, text=ten_mon[:2].upper(), text_color="white", font=ctk.CTkFont(weight="bold")).pack(expand=True)
 
            # 2. Xếp nút [+] bên Phải TRƯỚC để nó giữ chỗ an toàn
            ctk.CTkButton(card, text="+", width=30, height=30, fg_color="#333333", command=lambda id=d_id: self.on_item_add(id)).pack(side="right", padx=10)

            # 3. Xếp phần Thông tin vào không gian còn lại ở giữa
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True, pady=10, padx=(0, 5))
            
            # Cỡ chữ tên món có thể giảm xuống 11 để chống tràn nếu tên quá dài
            ctk.CTkLabel(info, text=ten_mon, font=ctk.CTkFont(size=11, weight="bold"), text_color="white", anchor="w").pack(fill="x")
            ctk.CTkLabel(info, text=f"{gia_ban:,.0f} đ".replace(",", "."), font=ctk.CTkFont(size=11, weight="bold"), text_color=self.color_accent, anchor="w").pack(fill="x", side="bottom")
 
    def set_category(self, cat):
        self.current_category = cat
        self.refresh_menu()
 
    def get_image(self, path, size=(40, 40)):
        if path and os.path.exists(path):
            try: return ctk.CTkImage(light_image=Image.open(path), size=size)
            except Exception: pass
        return None
 
    def ui_add_table_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Thêm Bàn Mới")
        popup.geometry("300x180")
        popup.attributes("-topmost", True)
        ctk.CTkLabel(popup, text="NHẬP TÊN BÀN MỚI", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 10))
        e_name = ctk.CTkEntry(popup, placeholder_text="VD: Bàn 5, Bàn VIP...")
        e_name.pack(padx=20, fill="x", pady=10)
        def submit():
            if e_name.get().strip():
                self.controller.add_new_table(e_name.get().strip())
                self.refresh_tables()
                popup.destroy()
        ctk.CTkButton(popup, text="Thêm Bàn", fg_color=self.color_accent, command=submit).pack(pady=10)
 
    def ui_rename_table_popup(self, table_id, current_name):
        popup = ctk.CTkToplevel(self)
        popup.title("Sửa Tên Bàn")
        popup.geometry("300x180")
        popup.attributes("-topmost", True)
        ctk.CTkLabel(popup, text="SỬA TÊN BÀN", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 10))
        e_name = ctk.CTkEntry(popup)
        e_name.insert(0, current_name)
        e_name.pack(padx=20, fill="x", pady=10)
        def submit():
            new_name = e_name.get().strip()
            if new_name:
                self.controller.rename_table(table_id, new_name)
                self.refresh_tables()
                popup.destroy()
        ctk.CTkButton(popup, text="Lưu", fg_color=self.color_accent, command=submit).pack(pady=10)
 
    def ui_delete_table_confirm(self, table_id, table_name):
        if messagebox.askyesno("Xóa bàn", f"Xóa bàn '{table_name}'?\n(Chỉ nên xóa bàn đang Trống, không có đơn mở)"):
            self.controller.delete_table(table_id)
            if self.selected_table_id == table_id:
                self.selected_table_id = None
            self.refresh_tables()

    # ==========================================
    # POPUP CHỈNH SỬA MẪU HÓA ĐƠN (LIVE PREVIEW)
    # ==========================================
    def ui_receipt_template_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Thiết Lập Mẫu Hóa Đơn")
        popup.geometry("800x550")
        popup.attributes("-topmost", True)
        popup.configure(fg_color="#121212")

        popup.grid_columnconfigure(0, weight=1)
        popup.grid_columnconfigure(1, weight=1)
        popup.grid_rowconfigure(0, weight=1)

        # Lấy dữ liệu mẫu hiện tại
        try:
            template_data = self.controller.get_receipt_template()
        except AttributeError:
            template_data = {"ten_quan": "COFFEE SHOP", "dia_chi": "Địa chỉ quán", "dien_thoai": "SĐT", "loi_cam_on": "Cảm ơn quý khách!"}

        var_name = ctk.StringVar(value=template_data.get("ten_quan", ""))
        var_address = ctk.StringVar(value=template_data.get("dia_chi", ""))
        var_phone = ctk.StringVar(value=template_data.get("dien_thoai", ""))
        var_footer = ctk.StringVar(value=template_data.get("loi_cam_on", ""))

        # --- KHUNG BÊN TRÁI: FORM NHẬP LIỆU ---
        form_frame = ctk.CTkFrame(popup, fg_color="#212121", corner_radius=8, border_width=1, border_color="#333333")
        form_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        ctk.CTkLabel(form_frame, text="⚙️ THÔNG TIN IN TRÊN BILL", font=ctk.CTkFont(size=16, weight="bold"), text_color="white").pack(anchor="w", padx=20, pady=(20, 15))

        def create_input(parent, label, var):
            ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=12, weight="bold"), text_color="#AAAAAA").pack(anchor="w", padx=20)
            entry = ctk.CTkEntry(parent, textvariable=var, height=35, fg_color="#121212", border_color="#333333", text_color="white")
            entry.pack(fill="x", padx=20, pady=(5, 15))
            var.trace_add("write", self._update_live_preview)

        create_input(form_frame, "TÊN QUÁN / THƯƠNG HIỆU:", var_name)
        create_input(form_frame, "ĐỊA CHỈ QUÁN:", var_address)
        create_input(form_frame, "SỐ ĐIỆN THOẠI / HOTLINE:", var_phone)
        create_input(form_frame, "LỜI CẢM ƠN (CHÂN TRANG):", var_footer)

        def save_template():
            data = {
                "ten_quan": var_name.get().strip(),
                "dia_chi": var_address.get().strip(),
                "dien_thoai": var_phone.get().strip(),
                "loi_cam_on": var_footer.get().strip()
            }
            try:
                self.controller.save_receipt_template(data)
                messagebox.showinfo("Thành công", "Đã lưu mẫu hóa đơn thành công!", parent=popup)
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu: {e}", parent=popup)

        ctk.CTkButton(form_frame, text="Lưu Cấu Hình Mẫu", fg_color="#3498DB", hover_color="#2980B9", height=45, font=ctk.CTkFont(weight="bold"), command=save_template).pack(fill="x", padx=20, pady=(10, 20), side="bottom")

        # --- KHUNG BÊN PHẢI: LIVE PREVIEW ---
        preview_frame = ctk.CTkFrame(popup, fg_color="#F2F3F4", corner_radius=0)
        preview_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        
        ctk.CTkLabel(preview_frame, text="XEM TRƯỚC HÓA ĐƠN (LIVE PREVIEW)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#7F8C8D").pack(pady=(10, 5))

        # Khung giấy cuộn bill
        paper_frame = ctk.CTkFrame(preview_frame, fg_color="white", corner_radius=0, border_width=1, border_color="#BDC3C7")
        paper_frame.pack(fill="both", expand=True, padx=40, pady=(0, 20))

        # Dùng Font Monospace để mô phỏng chính xác máy in nhiệt K80
        self.preview_text = ctk.CTkTextbox(paper_frame, fg_color="white", text_color="black", font=ctk.CTkFont(family="Courier", size=12), wrap="word")
        self.preview_text.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Lưu các biến để hàm update lấy dữ liệu
        self._preview_vars = (var_name, var_address, var_phone, var_footer)
        self._update_live_preview()

    def _update_live_preview(self, *args):
        if not hasattr(self, 'preview_text'): return
        
        name, addr, phone, footer = [v.get() for v in self._preview_vars]
        divider = "-" * 42
        now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

        # Sử dụng f-string nối dòng để loại bỏ triệt để khoảng trắng thụt lề của code
        bill_content = (
            f"{name.center(42)}\n"
            f"{addr.center(42)}\n"
            f"{phone.center(42)}\n"
            f"{divider}\n"
            f"{'HOA DON THANH TOAN'.center(42)}\n"
            f"So don: #DEMO_123\n"
            f"Thoi gian: {now_str}\n"
            f"{divider}\n"
            f"TEN MON              SL      THANH TIEN\n"
            f"Ca Phe Sua Da        2         50.000 d\n"
            f"Tra Dao Cam Sa       1         45.000 d\n"
            f"Banh Mi Nuong        1         20.000 d\n"
            f"{divider}\n"
            f"TONG CONG:                    115.000 d\n"
            f"{divider}\n"
            f"{footer.center(42)}\n"
        )
        
        self.preview_text.configure(state="normal")
        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("1.0", bill_content)
        self.preview_text.configure(state="disabled")

    # ==========================================
    # POPUP QUẢN LÝ MÀ GIẢM GIÁ (TÍCH HỢP DATE PICKER)
    # ==========================================
    def ui_discount_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Quản Lý Mã Giảm Giá")
        popup.geometry("700x500")
        popup.attributes("-topmost", True)
        popup.configure(fg_color="#121212")

        # --- TRÊN: FORM THÊM MÃ ---
        form_frame = ctk.CTkFrame(popup, fg_color="#212121", corner_radius=8)
        form_frame.pack(fill="x", padx=15, pady=15)
        
        row1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row1.pack(fill="x", padx=10, pady=(10, 5))
        
        col1 = ctk.CTkFrame(row1, fg_color="transparent")
        col1.pack(side="left", padx=5)
        ctk.CTkLabel(col1, text="Mã Code (VD: TET2026)", font=ctk.CTkFont(size=11), text_color="#AAAAAA").pack(anchor="w")
        var_code = ctk.StringVar()
        ctk.CTkEntry(col1, textvariable=var_code, width=150).pack()
        
        col2 = ctk.CTkFrame(row1, fg_color="transparent")
        col2.pack(side="left", padx=5)
        ctk.CTkLabel(col2, text="Loại giảm", font=ctk.CTkFont(size=11), text_color="#AAAAAA").pack(anchor="w")
        var_type = ctk.StringVar(value="% Phần trăm")
        ctk.CTkOptionMenu(col2, variable=var_type, values=["% Phần trăm", "VNĐ Tiền mặt"], width=120, fg_color="#333333").pack()
        
        col3 = ctk.CTkFrame(row1, fg_color="transparent")
        col3.pack(side="left", padx=5)
        ctk.CTkLabel(col3, text="Giá trị", font=ctk.CTkFont(size=11), text_color="#AAAAAA").pack(anchor="w")
        var_value = ctk.StringVar()
        ctk.CTkEntry(col3, textvariable=var_value, width=100).pack()

        row2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row2.pack(fill="x", padx=10, pady=(5, 10))
        
        # --- SỬ DỤNG TKCALENDAR ĐỂ CHỌN NGÀY ---
        col4 = ctk.CTkFrame(row2, fg_color="transparent")
        col4.pack(side="left", padx=5)
        ctk.CTkLabel(col4, text="Ngày bắt đầu", font=ctk.CTkFont(size=11), text_color="#AAAAAA").pack(anchor="w")
        
        # DatePicker Bắt đầu
        cal_start = DateEntry(col4, width=15, background='#E67E22', foreground='white', borderwidth=0, date_pattern='yyyy-mm-dd', font=('Arial', 11))
        cal_start.pack(pady=(2,0))

        col5 = ctk.CTkFrame(row2, fg_color="transparent")
        col5.pack(side="left", padx=15)
        ctk.CTkLabel(col5, text="Ngày kết thúc", font=ctk.CTkFont(size=11), text_color="#AAAAAA").pack(anchor="w")
        
        # DatePicker Kết thúc
        cal_end = DateEntry(col5, width=15, background='#E67E22', foreground='white', borderwidth=0, date_pattern='yyyy-mm-dd', font=('Arial', 11))
        cal_end.pack(pady=(2,0))

        # --- DƯỚI: BẢNG DANH SÁCH MÃ ---
        table_frame = ctk.CTkFrame(popup, fg_color="#212121", corner_radius=8)
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        import tkinter.ttk as ttk
        style = ttk.Style()
        style.configure("Discount.Treeview", background="#2B2B2B", foreground="white", rowheight=30, fieldbackground="#2B2B2B", borderwidth=0)
        style.configure("Discount.Treeview.Heading", background="#333333", foreground="white", font=('Arial', 10, 'bold'))

        tree = ttk.Treeview(table_frame, columns=("id", "code", "type", "value", "start", "end"), show="headings", style="Discount.Treeview")
        tree.heading("id", text="ID"); tree.column("id", width=30, anchor="center")
        tree.heading("code", text="Mã Code"); tree.column("code", width=100)
        tree.heading("type", text="Loại"); tree.column("type", width=80, anchor="center")
        tree.heading("value", text="Giá Trị"); tree.column("value", width=80, anchor="e")
        tree.heading("start", text="Bắt đầu"); tree.column("start", width=130, anchor="center")
        tree.heading("end", text="Kết thúc"); tree.column("end", width=130, anchor="center")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        import sqlite3
        from src.config import DB_PATH

        def load_discounts():
            for i in tree.get_children(): tree.delete(i)
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT id, ma_code, loai_giam, gia_tri, ngay_bat_dau, ngay_ket_thuc FROM ma_giam_gia ORDER BY id DESC")
                for r in cursor.fetchall():
                    val_str = f"{r[3]} %" if r[2] == 'phan_tram' else f"{r[3]:,.0f} đ".replace(",", ".")
                    tree.insert("", "end", values=(r[0], r[1], "Phần trăm" if r[2]=='phan_tram' else "Tiền mặt", val_str, r[4], r[5]))
            except: pass
            finally:
                if 'conn' in locals(): conn.close()

        def add_discount():
            code = var_code.get().strip().upper()
            val = var_value.get().strip()
            
            if not code or not val: return messagebox.showwarning("Lỗi", "Vui lòng nhập đủ Mã Code và Giá trị!", parent=popup)
            try:
                val = int(val)
                type_db = 'phan_tram' if "Phần" in var_type.get() else 'tien_mat'
                
                # Tự động chèn giờ bắt đầu là 00:00:00 và giờ kết thúc là 23:59:59
                start_datetime = f"{cal_start.get()} 00:00:00"
                end_datetime = f"{cal_end.get()} 23:59:59"

                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO ma_giam_gia (ma_code, loai_giam, gia_tri, ngay_bat_dau, ngay_ket_thuc) VALUES (?, ?, ?, ?, ?)", 
                               (code, type_db, val, start_datetime, end_datetime))
                conn.commit()
                
                var_code.set(""); var_value.set("")
                load_discounts()
            except sqlite3.IntegrityError:
                messagebox.showerror("Lỗi", "Mã này đã tồn tại trong hệ thống!", parent=popup)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}", parent=popup)
            finally:
                if 'conn' in locals(): conn.close()

        def del_discount():
            sel = tree.selection()
            if not sel: return messagebox.showwarning("Lỗi", "Vui lòng chọn 1 mã ở bảng bên dưới để xóa", parent=popup)
            if messagebox.askyesno("Xóa", "Bạn có chắc chắn muốn xóa mã giảm giá này?", parent=popup):
                try:
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM ma_giam_gia WHERE id=?", (tree.item(sel[0], "values")[0],))
                    conn.commit()
                    load_discounts()
                finally:
                    if 'conn' in locals(): conn.close()

        ctk.CTkButton(row1, text="Thêm Mã Khuyến Mãi", font=ctk.CTkFont(weight="bold"), fg_color="#2ECC71", hover_color="#27AE60", command=add_discount).pack(side="left", padx=15, pady=(15,0))
        ctk.CTkButton(table_frame, text="🗑️ Xóa Mã Đang Chọn", fg_color="transparent", border_width=1, border_color="#E74C3C", text_color="#E74C3C", command=del_discount).pack(pady=(0, 10))

        load_discounts()