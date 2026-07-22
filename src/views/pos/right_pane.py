import customtkinter as ctk
import tkinter.messagebox as messagebox
import json
import sqlite3
import datetime
from src.config import DB_PATH
from src.utils.printer_helper import PrinterHelper

class RightPane(ctk.CTkFrame):
    def __init__(self, master, controller, on_bill_cleared):
        super().__init__(master, fg_color="#212121", corner_radius=8, border_width=1, border_color="#333333")
        self.controller = controller
        self.on_bill_cleared = on_bill_cleared 
        self.printer = PrinterHelper()
        
        self.current_order_id = None
        self.current_table_id = None
        
        # Biến nhớ Khuyến mãi
        self.subtotal = 0
        self.current_discount_amount = 0
        self.current_discount_code = None
        
        self.build_ui()

    def build_ui(self):
        self.bill_header = ctk.CTkFrame(self, fg_color="transparent")
        self.bill_header.pack(fill="x", padx=15, pady=15)
        self.lbl_table_name = ctk.CTkLabel(self.bill_header, text="📄 CHƯA CHỌN BÀN", font=ctk.CTkFont(size=14, weight="bold"), text_color="white")
        self.lbl_table_name.pack(side="left")

        ctk.CTkFrame(self, height=1, fg_color="#333333").pack(fill="x")
        self.order_list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.order_list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        ctk.CTkFrame(self, height=1, fg_color="#333333").pack(fill="x")

        # --- THANH TOÁN & MÃ GIẢM GIÁ ---
        self.summary_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.summary_frame.pack(fill="x", padx=15, pady=10)

       # 1. Menu chọn mã giảm giá (Thay vì nhập tay)
        self.discount_frame = ctk.CTkFrame(self.summary_frame, fg_color="transparent")
        self.discount_frame.pack(fill="x", pady=5)
        
        self.var_discount_code = ctk.StringVar(value="-- Chọn mã giảm giá --")
        
        # OptionMenu tự động gọi hàm apply_discount khi user chọn
        self.opt_discount = ctk.CTkOptionMenu(
            self.discount_frame, 
            variable=self.var_discount_code, 
            values=["-- Chọn mã giảm giá --"], 
            height=30, 
            fg_color="#121212", 
            button_color="#333333",
            command=self.apply_discount
        )
        self.opt_discount.pack(side="left", fill="x", expand=True)

        # 2. Hiển thị Tiền giảm giá
        self.row_discount = ctk.CTkFrame(self.summary_frame, fg_color="transparent")
        self.row_discount.pack(fill="x", pady=2)
        ctk.CTkLabel(self.row_discount, text="GIẢM GIÁ:", font=ctk.CTkFont(weight="bold"), text_color="#AAAAAA").pack(side="left")
        self.lbl_discount_amount = ctk.CTkLabel(self.row_discount, text="0 đ", font=ctk.CTkFont(weight="bold"), text_color="#2ECC71")
        self.lbl_discount_amount.pack(side="right")

        # 3. Tổng tiền
        row_total = ctk.CTkFrame(self.summary_frame, fg_color="transparent")
        row_total.pack(fill="x", pady=5)
        ctk.CTkLabel(row_total, text="TỔNG TIỀN PHẢI TRẢ:", font=ctk.CTkFont(weight="bold"), text_color="white").pack(side="left")
        self.lbl_total_price = ctk.CTkLabel(row_total, text="0 đ", font=ctk.CTkFont(size=18, weight="bold"), text_color="#E74C3C")
        self.lbl_total_price.pack(side="right")

        pay_frame = ctk.CTkFrame(self.summary_frame, fg_color="transparent")
        pay_frame.pack(fill="x", pady=(10, 5))
        
        col_khach = ctk.CTkFrame(pay_frame, fg_color="transparent")
        col_khach.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(col_khach, text="TIỀN KHÁCH ĐƯA", font=ctk.CTkFont(size=10), text_color="#AAAAAA").pack(anchor="w")
        self.var_khach = ctk.StringVar()
        self.var_khach.trace_add("write", self.calc_change)
        self.entry_khach = ctk.CTkEntry(col_khach, textvariable=self.var_khach, fg_color="#121212", border_color="#333333")
        self.entry_khach.pack(fill="x")

        col_thua = ctk.CTkFrame(pay_frame, fg_color="transparent")
        col_thua.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(col_thua, text="TIỀN THỪA", font=ctk.CTkFont(size=10), text_color="#AAAAAA").pack(anchor="w")
        self.lbl_thua = ctk.CTkLabel(col_thua, text="0 đ", font=ctk.CTkFont(weight="bold"), text_color="#2ECC71")
        self.lbl_thua.pack(fill="x", pady=5)

        btn_action = ctk.CTkFrame(self.summary_frame, fg_color="transparent")
        btn_action.pack(fill="x", pady=(15, 5))
        
        self.chk_print_var = ctk.StringVar(value="off")
        ctk.CTkCheckBox(btn_action, text="In Hóa Đơn", variable=self.chk_print_var, onvalue="on", offvalue="off", text_color="#AAAAAA", checkbox_height=20, checkbox_width=20).pack(side="left", padx=5)

        ctk.CTkButton(btn_action, text="Hủy đơn", width=80, fg_color="transparent", border_width=1, border_color="#E74C3C", text_color="#E74C3C", hover_color="#641E16", command=self.ui_cancel_order).pack(side="right", padx=(5, 0))
        ctk.CTkButton(btn_action, text="🧾 THANH TOÁN", fg_color="#E67E22", hover_color="#D35400", text_color="white", command=self.ui_checkout).pack(side="right", fill="x", expand=True)

    def load_order(self, order_id, table_id, table_name):
        self.current_order_id = order_id
        self.current_table_id = table_id
        self.lbl_table_name.configure(text=f"📄 {table_name} " + (f"(Đơn #{order_id})" if order_id else ""))
        
        # 1. BẢO TỒN MÃ GIẢM GIÁ: Lưu tạm mã cũ trước khi load lại bill
        old_discount_code = self.current_discount_code

        for widget in self.order_list_frame.winfo_children(): widget.destroy()

        items = self.controller.get_order_items(order_id)
        self.subtotal = self.controller.get_order_total(order_id)
        self.lbl_total_price.configure(text=f"{self.subtotal:,.0f} đ".replace(",", "."))
        self.calc_change()

        # 2. Reset UI giảm giá tạm thời
        self.current_discount_amount = 0
        self.current_discount_code = None
        self.var_discount_code.set("-- Chọn mã giảm giá --")
        self.lbl_discount_amount.configure(text="0 đ")

        # 3. Load danh sách mã có hiệu lực (Sử dụng localtime để khớp chính xác giờ Việt Nam)
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT ma_code FROM ma_giam_gia WHERE datetime('now', 'localtime') >= ngay_bat_dau AND datetime('now', 'localtime') <= ngay_ket_thuc")
            valid_codes = ["-- Chọn mã giảm giá --"] + [r[0] for r in cursor.fetchall()]
            self.opt_discount.configure(values=valid_codes)
            
            # 4. Tự động áp dụng LẠI mã giảm giá cũ nếu nó vẫn còn hợp lệ
            if old_discount_code in valid_codes and items:
                self.apply_discount(old_discount_code)
        except: pass
        finally:
            if 'conn' in locals(): conn.close()

        if not items:
            ctk.CTkLabel(self.order_list_frame, text="🛍\nCHƯA CÓ MÓN NÀO", text_color="#AAAAAA").pack(pady=100)
            if order_id: self.on_bill_cleared()
            return

        for item in items:
            item_id, do_uong_id, ten_mon, so_luong, don_gia, ghi_chu, thanh_tien, custom_recipe = item
            card = ctk.CTkFrame(self.order_list_frame, fg_color="#121212", corner_radius=6, border_width=1, border_color="#333333")
            card.pack(fill="x", pady=4)
            
            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=10, pady=(10, 5))
            ctk.CTkLabel(top_row, text=ten_mon, font=ctk.CTkFont(weight="bold"), text_color="white").pack(side="left")
            ctk.CTkLabel(top_row, text=f"{thanh_tien:,.0f} đ".replace(",", "."), text_color="#E67E22").pack(side="right")

            mid_row = ctk.CTkFrame(card, fg_color="transparent")
            mid_row.pack(fill="x", padx=10, pady=2)
            
            var_note = ctk.StringVar(value=ghi_chu or "")
            e_note = ctk.CTkEntry(mid_row, textvariable=var_note, height=24, fg_color="#212121", placeholder_text="Ghi chú...", border_width=0)
            e_note.pack(side="left", fill="x", expand=True, padx=(0, 5))
            e_note.bind("<FocusOut>", lambda e, id=item_id, v=var_note: self.controller.update_item_note(id, v.get()))
            e_note.bind("<Return>", lambda e, id=item_id, v=var_note: self.controller.update_item_note(id, v.get()))

            ctrl = ctk.CTkFrame(mid_row, fg_color="#333333", corner_radius=4)
            ctrl.pack(side="right")
            ctk.CTkButton(ctrl, text="-", width=25, height=24, fg_color="transparent", command=lambda i=item_id, q=so_luong: self.update_qty(i, q-1)).pack(side="left")
            ctk.CTkLabel(ctrl, text=str(so_luong), width=25).pack(side="left")
            ctk.CTkButton(ctrl, text="+", width=25, height=24, fg_color="transparent", command=lambda i=item_id, q=so_luong: self.update_qty(i, q+1)).pack(side="left")

            btn_recipe = ctk.CTkButton(card, text="⚙️ Sửa CT", height=20, fg_color="transparent", text_color="#8E44AD", hover_color="#2A2A2A", 
                                       command=lambda i=item_id, d=do_uong_id, c=custom_recipe: self.ui_custom_recipe(i, d, c))
            btn_recipe.pack(anchor="e", padx=10, pady=(0, 5))

    def apply_discount(self, selected_code=None):
        # SỬA LỖI UI: Lấy trực tiếp tham số selected_code do Tkinter truyền vào 
        # (Thay vì dùng self.var_discount_code.get() vì nó cập nhật chậm 1 nhịp)
        code = selected_code if selected_code else self.var_discount_code.get()
        
        # Cập nhật chữ hiển thị ngay lập tức
        self.var_discount_code.set(code)

        # Nếu user chọn "Không dùng mã" thì reset về 0
        if code == "-- Chọn mã giảm giá --":
            self.current_discount_amount = 0
            self.current_discount_code = None
            self.lbl_discount_amount.configure(text="0 đ")
            self.lbl_total_price.configure(text=f"{self.subtotal:,.0f} đ".replace(",", "."))
            self.calc_change()
            return
            
        if not self.current_order_id or self.subtotal == 0: 
            self.var_discount_code.set("-- Chọn mã giảm giá --")
            return messagebox.showwarning("Lỗi", "Đơn hàng trống, không thể áp dụng!")

        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ma_giam_gia WHERE ma_code = ?", (code,))
            km = cursor.fetchone()

            if not km: 
                return messagebox.showerror("Lỗi", "Mã giảm giá không tồn tại!")

            gia_tri = km['gia_tri']
            discount = self.subtotal * (gia_tri / 100) if km['loai_giam'] == 'phan_tram' else gia_tri
            
            # Không được giảm lố tổng tiền của hóa đơn
            if discount > self.subtotal: discount = self.subtotal

            # Áp dụng thành công, lưu lại trạng thái
            self.current_discount_amount = discount
            self.current_discount_code = code
            
            self.lbl_discount_amount.configure(text=f"- {discount:,.0f} đ".replace(",", "."))
            
            final_total = self.subtotal - discount
            self.lbl_total_price.configure(text=f"{final_total:,.0f} đ".replace(",", "."))
            self.calc_change()
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Hệ thống gặp sự cố khi áp mã: {e}")
        finally:
            if 'conn' in locals(): conn.close()

    def update_qty(self, item_id, qty):
        self.controller.update_item_qty(item_id, qty)
        self.load_order(self.current_order_id, self.current_table_id, self.lbl_table_name.cget("text").split("(")[0].strip().replace("📄 ", ""))

    def calc_change(self, *args):
        try:
            k = float(self.var_khach.get().replace(".", ""))
            # Lấy Tổng tiền (đã trừ giảm giá)
            t = float(self.lbl_total_price.cget("text").replace(" đ", "").replace(".", ""))
            thua = k - t
            self.lbl_thua.configure(text=f"{thua:,.0f} đ".replace(",", "."), text_color="#2ECC71" if thua >= 0 else "#E74C3C")
        except:
            self.lbl_thua.configure(text="0 đ", text_color="#AAAAAA")

    def ui_checkout(self):
        if not self.current_order_id: return
        if self.subtotal == 0: return self.ui_cancel_order()

        try: k = float(self.var_khach.get().replace(".", ""))
        except: return messagebox.showerror("Lỗi", "Nhập tiền khách đưa")
        
        # Gọi thẳng Controller, truyền thêm thông tin giảm giá
        final, change = self.controller.close_order(
            self.current_order_id, 
            k, 
            self.current_discount_amount, 
            self.current_discount_code
        )
        
        # Nếu change trả về None nghĩa là khách đưa thiếu tiền (Model đã chặn lại)
        if change is None: return messagebox.showerror("Lỗi", "Khách đưa chưa đủ tiền!")

        # Xử lý In Hóa Đơn
        if self.chk_print_var.get() == "on":
            items_for_print = self.controller.get_order_items(self.current_order_id)
            t_name = self.lbl_table_name.cget("text").split("(")[0].strip().replace("📄 ", "")
            try: self.printer.print_receipt(self.current_order_id, t_name, items_for_print, final, k, change)
            except Exception as e: messagebox.showerror("Lỗi Máy In", f"Không thể xuất hóa đơn: {e}")

        messagebox.showinfo("Xong", f"Thanh toán hoàn tất!\nTiền thừa: {change:,.0f} đ".replace(",", "."))
        self.clear_ui()
        self.on_bill_cleared() # Hàm này kích hoạt làm mới màu Bàn bên Left Pane

    def ui_cancel_order(self):
        if not self.current_order_id: return
        if messagebox.askyesno("Hủy", "Hủy toàn bộ đơn này?"):
            self.controller.cancel_order(self.current_order_id, self.current_table_id)
            self.clear_ui()
            self.on_bill_cleared()

    def clear_ui(self):
        self.current_order_id = None
        self.current_table_id = None
        self.lbl_table_name.configure(text="📄 CHƯA CHỌN BÀN")
        self.var_khach.set("")
        self.load_order(None, None, "CHƯA CHỌN BÀN")