import tkinter as tk
import customtkinter as ctk
import tkinter.messagebox as messagebox
from PIL import Image
import os
 
class LeftPane(ctk.CTkFrame):
    def __init__(self, master, controller, on_table_select, on_item_add):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.on_table_select = on_table_select # Hàm callback gọi sang Main
        self.on_item_add = on_item_add         # Hàm callback gọi sang Main
 
        self.current_category = "Tất cả"
        self.selected_table_id = None
 
        # Bảng màu
        self.card_color = "#212121"
        self.border_color = "#333333"
        self.color_empty = "#196F3D"
        self.color_occupied = "#922B21"
        self.color_accent = "#E67E22"
 
        # [FIX #5]: Kích thước tối thiểu mỗi thẻ để tự tính số cột theo bề rộng thực tế
        self.min_table_card_w = 120
        self.min_menu_card_w = 190
        self.table_cols = 4
        self.menu_cols = 3  # mặc định 1 hàng 3 món thay vì 2
        self._resize_jobs = {}
 
        self.build_ui()
 
    def build_ui(self):
        # [FIX #5]: PanedWindow dọc -> kéo được ranh giới giữa "Sơ đồ bàn" và "Menu"
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
        ctk.CTkButton(t_header, text="+ Thiết lập bàn", width=90, height=24, fg_color="transparent", border_width=1, border_color=self.color_accent, text_color=self.color_accent, hover_color="#3E2723", command=self.ui_add_table_popup).pack(side="left", padx=10)
 
        legend_frame = ctk.CTkFrame(t_header, fg_color="transparent")
        legend_frame.pack(side="right")
        self.lbl_legend_trong = ctk.CTkLabel(legend_frame, text="🟢 Trống", text_color="#AAAAAA", font=ctk.CTkFont(size=11))
        self.lbl_legend_trong.pack(side="left", padx=5)
        self.lbl_legend_khach = ctk.CTkLabel(legend_frame, text="🔴 Có khách", text_color="#AAAAAA", font=ctk.CTkFont(size=11))
        self.lbl_legend_khach.pack(side="left", padx=5)
 
        self.table_grid = ctk.CTkScrollableFrame(self.table_card, fg_color="transparent")
        self.table_grid.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.table_grid.bind("<Configure>", self._on_table_grid_resize)
 
        # [FIX]: stretch="always" -> khi kéo cao/thấp, không gian dư chia tỉ lệ cho cả 2 khung
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
 
        # [FIX]: Đặt sash dựa trên sự kiện <Configure> có kích thước thật, thay vì timer cố định
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
 
    # --- [FIX #5]: Responsive column count ---
 
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
        cols = max(2, width // self.min_table_card_w)
        if cols != self.table_cols:
            self.table_cols = cols
            self.refresh_tables()
 
    def _recompute_menu_cols(self, width):
        cols = max(2, width // self.min_menu_card_w)
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
                self.refresh_tables() # Update border color
                self.on_table_select(tid, tname)
 
            card.bind("<Button-1>", click_ev)
            lbl = ctk.CTkLabel(card, text=f"{t_name}\n({t_status})", font=ctk.CTkFont(size=12, weight="bold"), text_color="white")
            lbl.place(relx=0.5, rely=0.4, anchor="center")
            lbl.bind("<Button-1>", click_ev)
 
            # [FIX #3]: Icon sửa tên / xóa bàn đặt ở góc phải DƯỚI, dùng icon đơn sắc + màu trung tính
            # cho hợp tổng thể (tránh emoji nhiều màu, tránh che khuất tên bàn ở giữa thẻ)
            icon_row = ctk.CTkFrame(card, fg_color="transparent")
            icon_row.place(relx=1.0, rely=1.0, anchor="se", x=-4, y=-4)
            ctk.CTkButton(icon_row, text="✎", width=20, height=18, corner_radius=5,
                          fg_color="#161616", hover_color="#3A3A3A", text_color="#DDDDDD",
                          font=ctk.CTkFont(size=11),
                          command=lambda tid=t_id, tname=t_name: self.ui_rename_table_popup(tid, tname)).pack(side="left", padx=(0, 3))
            ctk.CTkButton(icon_row, text="✕", width=20, height=18, corner_radius=5,
                          fg_color="#161616", hover_color="#5A1F1A", text_color="#DDDDDD",
                          font=ctk.CTkFont(size=11),
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
 
            img_obj = self.get_image(hinh_anh)
            if img_obj:
                ctk.CTkLabel(card, image=img_obj, text="").pack(side="left", padx=10, pady=10)
            else:
                icon = ctk.CTkFrame(card, width=40, height=40, corner_radius=8, fg_color=f"#{abs(hash(phan_loai)) % 0xFFFFFF:06x}")
                icon.pack(side="left", padx=10, pady=10)
                icon.pack_propagate(False)
                ctk.CTkLabel(icon, text=ten_mon[:2].upper(), text_color="white", font=ctk.CTkFont(weight="bold")).pack(expand=True)
 
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True, pady=10)
            ctk.CTkLabel(info, text=ten_mon, font=ctk.CTkFont(size=12, weight="bold"), text_color="white", anchor="w").pack(fill="x")
            ctk.CTkLabel(info, text=f"{gia_ban:,.0f} đ".replace(",", "."), font=ctk.CTkFont(size=12, weight="bold"), text_color=self.color_accent, anchor="w").pack(fill="x", side="bottom")
 
            ctk.CTkButton(card, text="+", width=30, height=30, fg_color="#333333", command=lambda id=d_id: self.on_item_add(id)).pack(side="right", padx=10)
 
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
 
    # [FIX #3]: Popup sửa tên bàn
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
 
    # [FIX #3]: Xóa bàn có xác nhận
    def ui_delete_table_confirm(self, table_id, table_name):
        if messagebox.askyesno("Xóa bàn", f"Xóa bàn '{table_name}'?\n(Chỉ nên xóa bàn đang Trống, không có đơn mở)"):
            self.controller.delete_table(table_id)
            if self.selected_table_id == table_id:
                self.selected_table_id = None
            self.refresh_tables()