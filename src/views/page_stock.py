import customtkinter as ctk
import tkinter.messagebox as messagebox
from src.controllers.stock_controller import StockController

class PageStock(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.controller = StockController()

        self.lbl_title = ctk.CTkLabel(self, text="QUẢN LÝ KHO & RÀ SOÁT HAO HỤT", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_title.pack(pady=(10, 5))
        self.lbl_note = ctk.CTkLabel(self, text="Nhập số lượng thực tế tại cột 'Nhập thực tế' rồi bấm 'Kiểm Kho' để lưu.", font=ctk.CTkFont(size=12), text_color="#BDC3C7")
        self.lbl_note.pack(pady=(0, 10))

        # --- THÊM NGUYÊN LIỆU MỚI ---
        self.add_frame = ctk.CTkFrame(self)
        self.add_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.entry_name = ctk.CTkEntry(self.add_frame, placeholder_text="Tên nguyên liệu")
        self.entry_name.pack(side="left", padx=5, pady=10, expand=True, fill="x")

        self.entry_qty = ctk.CTkEntry(self.add_frame, placeholder_text="Số lượng ban đầu")
        self.entry_qty.pack(side="left", padx=5, pady=10, expand=True, fill="x")

        self.entry_unit = ctk.CTkEntry(self.add_frame, placeholder_text="Đơn vị (kg, ml, g)")
        self.entry_unit.pack(side="left", padx=5, pady=10, expand=True, fill="x")

        self.entry_cost = ctk.CTkEntry(self.add_frame, placeholder_text="Giá vốn (VNĐ)")
        self.entry_cost.pack(side="left", padx=5, pady=10, expand=True, fill="x")

        self.entry_note = ctk.CTkEntry(self.add_frame, placeholder_text="Ghi chú/diễn giải")
        self.entry_note.pack(side="left", padx=5, pady=10, expand=True, fill="x")

        self.btn_add = ctk.CTkButton(self.add_frame, text="+ Thêm nguyên liệu", command=self.ui_add_ingredient)
        self.btn_add.pack(side="left", padx=5, pady=10)

        # --- LƯỚI QUẢN LÝ KHO CHÍNH ---
        self.list_frame = ctk.CTkScrollableFrame(self)
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        self.history_frame = ctk.CTkFrame(self)
        self.history_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.refresh_stock_list()

    def refresh_stock_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        items = self.controller.get_inventory()

        # Header
        header = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        header.pack(fill="x", pady=5)
        ctk.CTkLabel(header, text="Nguyên Liệu", width=140, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Tồn Lý Thuyết", width=100, anchor="w", font=ctk.CTkFont(weight="bold"), text_color="#3498DB").pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Tồn Thực Tế", width=90, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Nhập thực tế", width=100, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Độ Lệch", width=80, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Giá Vốn", width=90, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Lý do / Thao tác", width=160, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)

        for item in items:
            i_id, i_name, i_unit, i_theory, i_actual, i_warn, i_cost = item
            try:
                i_theory = float(i_theory)
            except (TypeError, ValueError):
                i_theory = 0.0
            try:
                i_actual = float(i_actual)
            except (TypeError, ValueError):
                i_actual = 0.0
            try:
                i_warn = float(i_warn)
            except (TypeError, ValueError):
                i_warn = 0.0

            diff_value = i_actual - i_theory
            is_warning = i_actual <= i_warn or i_theory <= i_warn

            row_color = "#5D0000" if is_warning else "transparent"
            row = ctk.CTkFrame(self.list_frame, fg_color=row_color)
            row.pack(fill="x", pady=2)

            text_color = "#F1948A" if is_warning else ("white", "black")
            ctk.CTkLabel(row, text=i_name, width=160, anchor="w", text_color=text_color).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=f"{i_theory:g} {i_unit}", width=110, anchor="w", text_color="#3498DB", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=f"{i_actual:g} {i_unit}", width=90, anchor="w").pack(side="left", padx=5)
            var_actual = ctk.StringVar(value=f"{i_actual:g}")
            entry_actual = ctk.CTkEntry(row, width=100, textvariable=var_actual, placeholder_text="Thực tế")
            entry_actual.pack(side="left", padx=5)

            lbl_diff = ctk.CTkLabel(row, text=f"{diff_value:g}", width=80, anchor="w")
            lbl_diff.pack(side="left", padx=5)

            def calc_diff(*args, theo=i_theory, label=lbl_diff, var=var_actual):
                try:
                    actual = float(var.get())
                    diff = actual - float(theo)
                    color = "#E74C3C" if diff < 0 else "#2ECC71" if diff > 0 else "white"
                    label.configure(text=f"{diff:g}", text_color=color)
                except ValueError:
                    label.configure(text="...", text_color="gray")

            var_actual.trace_add("write", calc_diff)

            ctk.CTkLabel(row, text=f"{i_cost:g} đ" if i_cost else "-", width=90, anchor="w").pack(side="left", padx=5)
            entry_reason = ctk.CTkEntry(row, width=150, placeholder_text="Lý do lệch...")
            entry_reason.pack(side="left", padx=5)

            btn_sync = ctk.CTkButton(row, text="✔ Kiểm Kho", width=90, fg_color="#2980B9", hover_color="#21618C",
                                     command=lambda id=i_id, old=i_theory, e_act=entry_actual, e_rs=entry_reason: self.ui_sync_stock(id, old, e_act, e_rs))
            btn_sync.pack(side="left", padx=5)

            btn_restock = ctk.CTkButton(row, text="📦 Nhập hàng", width=90, fg_color="#D35400", hover_color="#A04000",
                                        command=lambda id=i_id, name=i_name: self.ui_restock_popup(id, name))
            btn_restock.pack(side="right", padx=5)

        if not items:
            ctk.CTkLabel(self.list_frame, text="Chưa có nguyên liệu trong kho. Hãy thêm nguyên vật liệu mới.", font=ctk.CTkFont(size=14), text_color="#BDC3C7").pack(pady=40)

        self.render_history()

    def render_history(self):
        history_items = self.controller.get_stock_history(limit=10)
        title = ctk.CTkLabel(self.history_frame, text="Lịch sử kiểm kho gần nhất", font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(anchor="w", padx=5, pady=(10, 5))

        history_list = ctk.CTkScrollableFrame(self.history_frame, fg_color="transparent", height=180)
        history_list.pack(fill="both", expand=True)

        header = ctk.CTkFrame(history_list, fg_color="transparent")
        header.pack(fill="x", pady=2)
        
        # SỬA LẠI CÁC DÒNG LABEL DƯỚI ĐÂY
        ctk.CTkLabel(header, text="Nguyên liệu", width=140, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Tồn Lý Thuyết", width=100, anchor="w", font=ctk.CTkFont(weight="bold"), text_color="#3498DB").pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Tồn Thực Tế", width=100, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Lệch", width=80, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Lý do", width=180, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)

        if not history_items:
            ctk.CTkLabel(history_list, text="Chưa có lịch sử kiểm kho.", font=ctk.CTkFont(size=14), text_color="#BDC3C7").pack(pady=20)
            return

        for _, name, theo, actual, diff, reason, checked_at in history_items:
            row = ctk.CTkFrame(history_list, fg_color="#2C3E50")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=name, width=140, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=f"{theo:g}", width=100, anchor="w", text_color="#3498DB").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=f"{actual:g}", width=100, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=f"{diff:g}", width=80, anchor="w", text_color="#F39C12").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=reason or "-", width=180, anchor="w").pack(side="left", padx=5)

    # --- CÁC HÀM XỬ LÝ ---
    def ui_add_ingredient(self):
        success, msg = self.controller.add_item(
            self.entry_name.get(),
            self.entry_qty.get(),
            self.entry_unit.get(),
            self.entry_cost.get(),
            self.entry_note.get(),
        )
        if success:
            self.entry_name.delete(0, 'end')
            self.entry_qty.delete(0, 'end')
            self.entry_unit.delete(0, 'end')
            self.entry_cost.delete(0, 'end')
            self.entry_note.delete(0, 'end')
            self.refresh_stock_list()
        else:
            messagebox.showerror("Lỗi", msg)

    def ui_sync_stock(self, ing_id, old_stock, entry_actual, entry_reason):
        if not entry_actual.get():
            return messagebox.showwarning("Cảnh báo", "Hãy nhập số lượng thực tế đếm được!")
        
        success, msg = self.controller.sync_stock(ing_id, old_stock, entry_actual.get(), entry_reason.get())
        if success:
            self.refresh_stock_list()
        else:
            messagebox.showerror("Lỗi", msg)

    def ui_restock_popup(self, ing_id, ing_name):
        """Mở cửa sổ nhỏ để nhập hàng và giá vốn"""
        popup = ctk.CTkToplevel(self)
        popup.title(f"Nhập hàng: {ing_name}")
        popup.geometry("350x280")
        popup.attributes("-topmost", True)

        ctk.CTkLabel(popup, text=f"Nhập thêm: {ing_name}", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        
        e_qty = ctk.CTkEntry(popup, placeholder_text="Số lượng nhập thêm")
        e_qty.pack(pady=10, padx=20, fill="x")

        e_cost = ctk.CTkEntry(popup, placeholder_text="Tổng Giá vốn (VNĐ)")
        e_cost.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(popup, text="(Nhập số hoặc để trống nếu không biết giá vốn)", font=ctk.CTkFont(size=12)).pack(pady=(0, 5))

        def submit():
            qty = e_qty.get().strip()
            cost = e_cost.get().strip()
            if not qty or not qty.replace('.', '', 1).isdigit():
                return messagebox.showerror("Lỗi", "Số lượng nhập không hợp lệ", parent=popup)

            success, msg = self.controller.restock_item(ing_id, qty, cost)
            if success:
                self.refresh_stock_list()
                popup.destroy()
            else:
                messagebox.showerror("Lỗi", msg, parent=popup)

        ctk.CTkButton(popup, text="Xác nhận Nhập kho", command=submit).pack(pady=10)