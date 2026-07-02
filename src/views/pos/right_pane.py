import customtkinter as ctk
import tkinter.messagebox as messagebox
import json
from src.utils.printer_helper import PrinterHelper

class RightPane(ctk.CTkFrame):
    def __init__(self, master, controller, on_bill_cleared):
        super().__init__(master, fg_color="#212121", corner_radius=8, border_width=1, border_color="#333333")
        self.controller = controller
        self.on_bill_cleared = on_bill_cleared # Hàm báo cho Main biết Bill đã xong để reset
        
        self.printer = PrinterHelper()
        self.current_order_id = None
        self.current_table_id = None
        
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

        # --- THANH TOÁN ---
        self.summary_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.summary_frame.pack(fill="x", padx=15, pady=10)

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
        
        # [FIX]: Mặc định BỎ TÍCH "In Hóa Đơn" ngay từ đầu
        self.chk_print_var = ctk.StringVar(value="off")
        ctk.CTkCheckBox(btn_action, text="In Hóa Đơn", variable=self.chk_print_var, onvalue="on", offvalue="off", text_color="#AAAAAA", checkbox_height=20, checkbox_width=20).pack(side="left", padx=5)

        ctk.CTkButton(btn_action, text="Hủy đơn", width=80, fg_color="transparent", border_width=1, border_color="#E74C3C", text_color="#E74C3C", hover_color="#641E16", command=self.ui_cancel_order).pack(side="right", padx=(5, 0))
        ctk.CTkButton(btn_action, text="🧾 THANH TOÁN", fg_color="#E67E22", hover_color="#D35400", text_color="white", command=self.ui_checkout).pack(side="right", fill="x", expand=True)

    def load_order(self, order_id, table_id, table_name):
        self.current_order_id = order_id
        self.current_table_id = table_id
        self.lbl_table_name.configure(text=f"📄 {table_name} " + (f"(Đơn #{order_id})" if order_id else ""))
        
        for widget in self.order_list_frame.winfo_children(): widget.destroy()

        items = self.controller.get_order_items(order_id)
        total = self.controller.get_order_total(order_id)
        self.lbl_total_price.configure(text=f"{total:,.0f} đ".replace(",", "."))
        self.calc_change()

        if not items:
            ctk.CTkLabel(self.order_list_frame, text="🛍\nCHƯA CÓ MÓN NÀO", text_color="#AAAAAA").pack(pady=100)
            if order_id:
                self.on_bill_cleared()
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

            btn_save_note = ctk.CTkButton(
                mid_row, text="💾", width=26, height=24, fg_color="#333333", hover_color="#444444",
                command=lambda id=item_id, v=var_note: self.controller.update_item_note(id, v.get())
            )
            btn_save_note.pack(side="left", padx=(0, 5))

            ctrl = ctk.CTkFrame(mid_row, fg_color="#333333", corner_radius=4)
            ctrl.pack(side="right")
            ctk.CTkButton(ctrl, text="-", width=25, height=24, fg_color="transparent", command=lambda i=item_id, q=so_luong: self.update_qty(i, q-1)).pack(side="left")
            ctk.CTkLabel(ctrl, text=str(so_luong), width=25).pack(side="left")
            ctk.CTkButton(ctrl, text="+", width=25, height=24, fg_color="transparent", command=lambda i=item_id, q=so_luong: self.update_qty(i, q+1)).pack(side="left")

            btn_recipe = ctk.CTkButton(card, text="⚙️ Sửa CT", height=20, fg_color="transparent", text_color="#8E44AD", hover_color="#2A2A2A", 
                                       command=lambda i=item_id, d=do_uong_id, c=custom_recipe: self.ui_custom_recipe(i, d, c))
            btn_recipe.pack(anchor="e", padx=10, pady=(0, 5))

    def update_qty(self, item_id, qty):
        self.controller.update_item_qty(item_id, qty)
        self.load_order(self.current_order_id, self.current_table_id, self.lbl_table_name.cget("text").split("(")[0].strip().replace("📄 ", ""))

    def calc_change(self, *args):
        try:
            k = float(self.var_khach.get().replace(".", ""))
            t = float(self.lbl_total_price.cget("text").replace(" đ", "").replace(".", ""))
            thua = k - t
            self.lbl_thua.configure(text=f"{thua:,.0f} đ".replace(",", "."), text_color="#2ECC71" if thua >= 0 else "#E74C3C")
        except:
            self.lbl_thua.configure(text="0 đ", text_color="#AAAAAA")

    def ui_checkout(self):
        if not self.current_order_id: return
        total = self.controller.get_order_total(self.current_order_id)
        if total == 0: return self.ui_cancel_order()

        try: k = float(self.var_khach.get().replace(".", ""))
        except: return messagebox.showerror("Lỗi", "Nhập tiền khách đưa")

        items_for_print = self.controller.get_order_items(self.current_order_id)
        t_name = self.lbl_table_name.cget("text").split("(")[0].strip().replace("📄 ", "")

        final, change = self.controller.close_order(self.current_order_id, k)
        if change is None: return messagebox.showerror("Lỗi", "Khách đưa chưa đủ tiền")

        # [FIX LOGIC NGƯỢC]: Chỉ xuất hóa đơn nếu có tích "on"
        if self.chk_print_var.get() == "on":
            try:
                self.printer.print_receipt(self.current_order_id, t_name, items_for_print, final, k, change)
            except Exception as e:
                messagebox.showerror("Lỗi Máy In", f"Không thể xuất hóa đơn: {e}")

        messagebox.showinfo("Xong", f"Thanh toán hoàn tất!\nTiền thừa: {change:,.0f} đ".replace(",", "."))
        self.clear_ui()
        self.on_bill_cleared()

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

    def ui_custom_recipe(self, item_id, do_uong_id, current_custom_recipe_str):
        popup = ctk.CTkToplevel(self)
        popup.title("Sửa C.Thức")
        popup.geometry("350x450")
        popup.attributes("-topmost", True)
        
        all_ing = self.controller.get_ingredients()
        base_recipe = self.controller.get_drink_base_recipe(do_uong_id)
        
        recipe_to_load = base_recipe
        if current_custom_recipe_str:
            try: recipe_to_load = json.loads(current_custom_recipe_str)
            except: pass

        scroll = ctk.CTkScrollableFrame(popup)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        entries = []
        for ing in all_ing:
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=ing[1]).pack(side="left")
            var = ctk.StringVar(value=str(recipe_to_load.get(str(ing[0]), recipe_to_load.get(ing[0], ""))))
            ctk.CTkEntry(row, textvariable=var, width=60).pack(side="right")
            entries.append({"id": ing[0], "var": var})

        def save():
            custom = {str(e["id"]): float(e["var"].get()) for e in entries if e["var"].get().strip()}
            self.controller.save_custom_recipe(item_id, custom)
            popup.destroy()
            
        ctk.CTkButton(popup, text="Lưu", command=save).pack(pady=10)