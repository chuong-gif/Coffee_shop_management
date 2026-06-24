import customtkinter as ctk
import tkinter.messagebox as messagebox
from src.controllers.order_controller import OrderController

class PagePOS(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        
        # Khởi tạo Controller chứa logic
        self.controller = OrderController()

        self.grid_columnconfigure(0, weight=6)
        self.grid_columnconfigure(1, weight=4)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # KHU VỰC BÊN TRÁI: SƠ ĐỒ BÀN & CÔNG CỤ
        # ==========================================
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")

        # --- Thanh công cụ Quản lý bàn ---
        self.toolbar_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.toolbar_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        self.lbl_title_left = ctk.CTkLabel(self.toolbar_frame, text="SƠ ĐỒ BÀN", font=ctk.CTkFont(size=18, weight="bold"))
        self.lbl_title_left.pack(side="left", padx=10)

        # Nút Thêm Bàn
        self.btn_add_table = ctk.CTkButton(self.toolbar_frame, text="+ Thêm Bàn", width=80, command=self.ui_add_table)
        self.btn_add_table.pack(side="right", padx=5)

        # Nút Gộp/Tách bàn (Sẽ nối logic sau)
        self.btn_merge_table = ctk.CTkButton(self.toolbar_frame, text="Gộp/Tách", width=80, fg_color="#8E44AD", hover_color="#9B59B6", command=self.ui_move_or_merge_table)
        self.btn_merge_table.pack(side="right", padx=5)

        self.btn_open_table = ctk.CTkButton(self.toolbar_frame, text="Mở Bàn", width=90, fg_color="#2980B9", hover_color="#21618C", command=self.ui_open_table)
        self.btn_open_table.pack(side="right", padx=5)

        # Nút Đơn Mang Về
        self.btn_takeaway = ctk.CTkButton(self.left_frame, text="🛒 Đơn Mang Về", height=40, fg_color="#E67E22", hover_color="#D35400", command=self.ui_takeaway)
        self.btn_takeaway.pack(padx=20, pady=(10, 15), fill="x")

        # Lưới chứa các bàn (Dynamic Grid)
        self.table_grid = ctk.CTkScrollableFrame(self.left_frame, fg_color="transparent")
        self.table_grid.pack(padx=10, pady=0, fill="both", expand=True)
        self.table_grid.grid_columnconfigure((0, 1, 2), weight=1)

        # ==========================================
        # KHU VỰC BÊN PHẢI: CHI TIẾT HÓA ĐƠN
        # ==========================================
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, padx=0, pady=0, sticky="nsew")

        self.lbl_title_right = ctk.CTkLabel(self.right_frame, text="CHI TIẾT ĐƠN HÀNG", font=ctk.CTkFont(size=18, weight="bold"))
        self.lbl_title_right.pack(pady=(10, 15))

        self.order_info_label = ctk.CTkLabel(self.right_frame, text="Vui lòng chọn bàn để gọi món hoặc chọn Đơn Mang Về", font=ctk.CTkFont(size=16, weight="bold"), anchor="w")
        self.order_info_label.pack(fill="x", padx=10, pady=(0, 10))

        self.note_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.note_frame.pack(fill="x", padx=10, pady=(0, 10))
        self.order_note_var = ctk.StringVar()
        self.order_note_entry = ctk.CTkEntry(self.note_frame, textvariable=self.order_note_var, placeholder_text="Ghi chú đơn (pha chế, phục vụ, vv.)")
        self.order_note_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.btn_save_note = ctk.CTkButton(self.note_frame, text="Lưu ghi chú", width=120, command=self.ui_save_order_note)
        self.btn_save_note.pack(side="right")

        self.order_list_frame = ctk.CTkScrollableFrame(self.right_frame, fg_color=("#EBEBEB", "#2B2B2B"), height=220)
        self.order_list_frame.pack(padx=10, pady=(0, 10), fill="x", expand=False)
        self.lbl_empty = ctk.CTkLabel(self.order_list_frame, text="Danh sách món sẽ hiện ở đây")
        self.lbl_empty.pack(pady=50)

        self.menu_title = ctk.CTkLabel(self.right_frame, text="Menu gọi món", font=ctk.CTkFont(size=16, weight="bold"), anchor="w")
        self.menu_title.pack(fill="x", padx=10, pady=(10, 5))

        self.menu_list_frame = ctk.CTkScrollableFrame(self.right_frame, fg_color=("#EBEBEB", "#2B2B2B"))
        self.menu_list_frame.pack(padx=10, pady=(0, 10), fill="both", expand=True)

        self.checkout_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.checkout_frame.pack(padx=10, pady=15, fill="x")

        self.lbl_total = ctk.CTkLabel(self.checkout_frame, text="Tổng tiền: 0 đ", font=ctk.CTkFont(size=18, weight="bold"), text_color="#E74C3C")
        self.lbl_total.pack(side="left", padx=10)

        buttons_frame = ctk.CTkFrame(self.checkout_frame, fg_color="transparent")
        buttons_frame.pack(side="right")

        self.btn_open_table_right = ctk.CTkButton(buttons_frame, text="Mở Bàn", height=40, fg_color="#2980B9", hover_color="#21618C", command=self.ui_open_table)
        self.btn_open_table_right.pack(side="right", padx=(0, 5))

        self.btn_print = ctk.CTkButton(buttons_frame, text="In Hóa Đơn", height=40, fg_color="#3498DB", hover_color="#2980B9", command=self.ui_print_invoice)
        self.btn_print.pack(side="right", padx=(0, 5))

        self.btn_checkout = ctk.CTkButton(buttons_frame, text="Thanh Toán", height=45, fg_color="#E74C3C", hover_color="#C0392B", font=ctk.CTkFont(size=14, weight="bold"), command=self.ui_checkout)
        self.btn_checkout.pack(side="right", padx=5)

        self.selected_table_id = None
        self.selected_table_name = None
        self.selected_order_id = None

        # Kích hoạt tải dữ liệu bàn từ Database lên UI
        self.refresh_table_grid()

    # ==========================================
    # CÁC HÀM XỬ LÝ GIAO DIỆN VÀ TƯƠNG TÁC
    # ==========================================
    def refresh_table_grid(self):
        """Xóa lưới bàn cũ và vẽ lại lưới bàn mới từ Database"""
        # Xóa các widget bàn cũ đang hiển thị
        for widget in self.table_grid.winfo_children():
            widget.destroy()

        # Lấy dữ liệu thật từ Controller
        tables = self.controller.get_tables_data()

        # Render danh sách bàn
        for i, table in enumerate(tables):
            table_id = table[0]
            ten_ban = table[1]
            trang_thai = table[2]

            row_index = i // 3
            col_index = i % 3

            # Chọn màu theo trạng thái
            bg_color = "#2ECC71" if trang_thai == "Trống" else "#E74C3C"
            hover_bg = "#27AE60" if trang_thai == "Trống" else "#C0392B"

            # Frame nhỏ chứa nút Bàn và nút Xóa mini
            frame_ban = ctk.CTkFrame(self.table_grid, fg_color="transparent")
            frame_ban.grid(row=row_index, column=col_index, padx=10, pady=10, sticky="nsew")

            btn_table = ctk.CTkButton(frame_ban, text=f"{ten_ban}\n({trang_thai})", 
                                      height=70, 
                                      fg_color=bg_color, hover_color=hover_bg,
                                      font=ctk.CTkFont(size=14, weight="bold"),
                                      # Dùng lambda để truyền ID bàn khi click
                                      command=lambda t_id=table_id, t_name=ten_ban: self.on_table_click(t_id, t_name))
            btn_table.pack(fill="both", expand=True)

            # Nút xóa bàn (nhỏ xíu ở dưới)
            btn_delete = ctk.CTkButton(frame_ban, text="Xóa", width=40, height=20, fg_color="#7F8C8D", hover_color="#95A5A6",
                                       command=lambda t_id=table_id: self.ui_delete_table(t_id))
            btn_delete.pack(pady=(2, 0))

    def on_table_click(self, table_id, ten_ban):
        order_data = self.controller.handle_table_click(table_id, ten_ban)
        self.selected_table_id = order_data["table_id"]
        self.selected_table_name = ten_ban
        self.selected_order_id = order_data["order_id"]
        self.order_note_var.set(order_data.get("order_note") or "")
        if self.selected_order_id:
            self.order_info_label.configure(text=f"Bàn: {ten_ban} | Đơn #{self.selected_order_id}")
        else:
            self.order_info_label.configure(text=f"Bàn: {ten_ban} | Chưa có đơn")
        self.refresh_order_items(order_data["order_items"])
        self.refresh_menu_items(order_data["menu"])
        self.lbl_total.configure(text=f"Tổng tiền: {order_data['order_total']:,} đ".replace(",", "."))

    def ui_add_table(self):
        """Hiển thị hộp thoại nhập tên bàn mới"""
        dialog = ctk.CTkInputDialog(text="Nhập tên bàn mới (VD: Bàn 1):", title="Thêm Bàn")
        ten_ban = dialog.get_input()
        if ten_ban:
            success = self.controller.add_new_table(ten_ban)
            if success:
                self.refresh_table_grid() # Tải lại lưới bàn

    def ui_delete_table(self, table_id):
        """Xác nhận và xóa bàn"""
        confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa bàn này không?")
        if confirm:
            self.controller.delete_table(table_id)
            self.refresh_table_grid()
            self.order_info_label.configure(text="Vui lòng chọn bàn để gọi món hoặc chọn Đơn Mang Về")
            self.selected_table_id = None
            self.selected_table_name = None
            self.selected_order_id = None
            self.order_note_var.set("")
            self.refresh_order_items([])
            self.refresh_menu_items([])

    def ui_open_table(self):
        if self.selected_table_id is None:
            return messagebox.showwarning("Lỗi", "Vui lòng chọn bàn trước khi mở bàn.")
        if self.selected_order_id:
            return messagebox.showinfo("Thông báo", "Bàn này đã có đơn hàng mở.")
        order_data = self.controller.open_table_order(self.selected_table_id, self.selected_table_name)
        self.selected_order_id = order_data["order_id"]
        self.order_note_var.set(order_data.get("order_note") or "")
        self.order_info_label.configure(text=f"Bàn: {self.selected_table_name} | Đơn #{self.selected_order_id}")
        self.refresh_order_items(order_data["order_items"])
        self.refresh_menu_items(order_data["menu"])
        self.lbl_total.configure(text=f"Tổng tiền: {order_data['order_total']:,} đ".replace(",", "."))

    def ui_move_or_merge_table(self):
        if not self.selected_order_id or self.selected_table_id is None:
            return messagebox.showwarning("Lỗi", "Vui lòng chọn bàn có đơn hàng trước khi chuyển/gộp.")

        dialog = ctk.CTkInputDialog(text="Nhập tên bàn đích để chuyển/gộp đơn:", title="Di chuyển/Gộp Bàn")
        target_name = dialog.get_input()
        if not target_name:
            return

        success, msg, target_table_id = self.controller.move_order_to_table(self.selected_table_id, target_name)
        if success:
            self.selected_table_id = target_table_id
            self.order_info_label.configure(text=f"Bàn: {target_name} | Đơn #{self.selected_order_id}")
            self.refresh_table_grid()
            messagebox.showinfo("Thành công", msg)
        else:
            messagebox.showerror("Lỗi", msg)

    def ui_save_order_note(self):
        if not self.selected_order_id:
            return messagebox.showwarning("Lỗi", "Chưa có đơn hàng để lưu ghi chú.")

        self.controller.save_order_note(self.selected_order_id, self.order_note_var.get())
        messagebox.showinfo("Thông báo", "Ghi chú đơn đã được lưu.")

    def refresh_order_items(self, order_items):
        for widget in self.order_list_frame.winfo_children():
            widget.destroy()

        if not order_items:
            ctk.CTkLabel(self.order_list_frame, text="Chưa có món nào trong đơn.").pack(pady=30)
            return

        for item in order_items:
            _, do_uong_id, ten_mon, so_luong, don_gia, ghi_chu, thanh_tien = item
            label = ctk.CTkLabel(
                self.order_list_frame,
                text=f"{ten_mon} x{so_luong} - {don_gia:,} đ = {thanh_tien:,} đ".replace(",", "."),
                anchor="w",
            )
            label.pack(fill="x", padx=10, pady=5)
            if ghi_chu:
                ctk.CTkLabel(self.order_list_frame, text=f"Ghi chú: {ghi_chu}", anchor="w", font=ctk.CTkFont(size=12)).pack(fill="x", padx=20, pady=(0, 5))

    def refresh_menu_items(self, available_menu):
        for widget in self.menu_list_frame.winfo_children():
            widget.destroy()

        if not available_menu:
            ctk.CTkLabel(self.menu_list_frame, text="Không có món nào còn hàng.").pack(pady=40)
            return

        for item in available_menu:
            d_id, ma_mon, ten_mon, phan_loai, gia_ban, con_hang, hinh_anh = item
            row = ctk.CTkFrame(self.menu_list_frame)
            row.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(row, text=f"{ten_mon} ({phan_loai})", anchor="w").pack(side="left", padx=5, expand=True)
            ctk.CTkLabel(row, text=f"{gia_ban:,} đ".replace(",", "."), width=110, anchor="e").pack(side="left", padx=5)
            ctk.CTkButton(row, text="+ Thêm", width=80, command=lambda id=d_id: self.ui_add_menu_item(id)).pack(side="right", padx=5)

    def ui_add_menu_item(self, do_uong_id):
        if not self.selected_order_id and self.selected_table_id is None:
            return messagebox.showwarning("Lỗi", "Vui lòng chọn bàn hoặc đơn mang về trước khi gọi món.")
        result = self.controller.add_item_to_order(
            self.selected_table_id,
            do_uong_id,
            order_id=self.selected_order_id,
            quantity=1,
        )
        self.selected_order_id = result["order_id"]
        if self.selected_table_name == "Đơn Mang Về":
            self.order_info_label.configure(text=f"Đơn Mang Về | Đơn #{self.selected_order_id}")
        else:
            self.order_info_label.configure(text=f"Bàn: {self.selected_table_name} | Đơn #{self.selected_order_id}")
        self.refresh_order_items(result["order_items"])
        self.lbl_total.configure(text=f"Tổng tiền: {result['order_total']:,} đ".replace(",", "."))

    def ui_takeaway(self):
        order_data = self.controller.create_takeaway_order()
        self.selected_table_id = order_data["table_id"]
        self.selected_table_name = order_data["ten_ban"]
        self.selected_order_id = order_data["order_id"]
        self.order_note_var.set(order_data.get("order_note") or "")
        self.order_info_label.configure(text="Đơn Mang Về | Đang xử lý")
        self.refresh_order_items(order_data["order_items"])
        self.refresh_menu_items(order_data["menu"])
        self.lbl_total.configure(text=f"Tổng tiền: {order_data['order_total']:,} đ".replace(",", "."))

    def ui_checkout(self):
        if not self.selected_order_id:
            return messagebox.showwarning("Lỗi", "Chưa có đơn hàng để thanh toán.")

        total_amount = self.controller.get_order_total(self.selected_order_id)
        if total_amount == 0:
            return messagebox.showwarning("Lỗi", "Đơn hàng chưa có món nào.")

        payment_dialog = ctk.CTkInputDialog(text="Nhập số tiền khách đưa:", title="Thanh toán")
        payment_value = payment_dialog.get_input()
        if not payment_value or not payment_value.replace('.', '', 1).isdigit():
            return messagebox.showerror("Lỗi", "Số tiền không hợp lệ.")

        total, change = self.controller.close_order(self.selected_order_id, int(float(payment_value)))
        if change is None:
            return messagebox.showerror("Lỗi", "Số tiền khách đưa phải lớn hơn hoặc bằng tổng tiền.")

        messagebox.showinfo("Thanh toán", f"Đã thanh toán {total:,} đ. Tiền thừa: {change:,} đ".replace(",", "."))
        self.refresh_table_grid()
        self.selected_table_id = None
        self.selected_order_id = None
        self.order_note_var.set("")
        self.order_info_label.configure(text="Vui lòng chọn bàn để gọi món hoặc chọn Đơn Mang Về")
        self.refresh_order_items([])
        self.refresh_menu_items([])
        self.lbl_total.configure(text="Tổng tiền: 0 đ")

    def ui_print_invoice(self):
        if not self.selected_order_id:
            return messagebox.showwarning("Lỗi", "Chưa có đơn hàng để in hóa đơn.")

        order_items = self.controller.get_order_items(self.selected_order_id)
        order_total = self.controller.get_order_total(self.selected_order_id)
        if not order_items:
            return messagebox.showwarning("Lỗi", "Đơn hàng chưa có món nào.")

        invoice_text = [f"HÓA ĐƠN BÁN HÀNG\nĐơn #{self.selected_order_id}"]
        for item in order_items:
            _, do_uong_id, ten_mon, so_luong, don_gia, ghi_chu, thanh_tien = item
            invoice_text.append(f"{ten_mon} x{so_luong} = {thanh_tien:,} đ")
            if ghi_chu:
                invoice_text.append(f"  Ghi chú: {ghi_chu}")
        invoice_text.append(f"Tổng: {order_total:,} đ")

        invoice_data = "\n".join(invoice_text).replace(",", ".")
        messagebox.showinfo("Hóa đơn", invoice_data)
