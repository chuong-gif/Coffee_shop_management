import customtkinter as ctk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import datetime
from tkcalendar import DateEntry
from src.controllers.order_controller import OrderController
from src.utils.printer_helper import PrinterHelper

class PageHistory(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.controller = OrderController()
        self.printer = PrinterHelper()
        self.current_selected_order_id = None

        # [TỐI ƯU UI]: Đảo tỷ lệ thành 6:4 (Trái rộng hơn Phải)
        self.grid_columnconfigure(0, weight=6) 
        self.grid_columnconfigure(1, weight=4) 
        self.grid_rowconfigure(0, weight=1)

        self.build_left_pane()
        self.build_right_pane()
        
        self.load_history()

    def build_left_pane(self):
        # Thiết kế dạng Card bo góc
        self.left_frame = ctk.CTkFrame(self, corner_radius=12, fg_color="#1E1E1E", border_width=1, border_color="#333333")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # --- BỘ LỌC THỜI GIAN ---
        filter_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=20)

        header_row = ctk.CTkFrame(filter_frame, fg_color="transparent")
        header_row.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(header_row, text="📊 LỊCH SỬ BÁN HÀNG", font=ctk.CTkFont(size=18, weight="bold"), text_color="#E67E22").pack(side="left")
        
        ctk.CTkButton(header_row, text="Hôm nay", width=80, height=28, font=ctk.CTkFont(weight="bold"), fg_color="#333333", hover_color="#444444", text_color="white", command=self.set_today).pack(side="right")

        date_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        date_frame.pack(fill="x")

        col1 = ctk.CTkFrame(date_frame, fg_color="transparent")
        col1.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(col1, text="Từ ngày:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#AAAAAA").pack(anchor="w", pady=(0, 5))
        self.cal_start = DateEntry(col1, width=15, background='#E67E22', foreground='white', borderwidth=0, date_pattern='yyyy-mm-dd', font=('Arial', 12))
        self.cal_start.pack(fill="x")

        col2 = ctk.CTkFrame(date_frame, fg_color="transparent")
        col2.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(col2, text="Đến ngày:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#AAAAAA").pack(anchor="w", pady=(0, 5))
        self.cal_end = DateEntry(col2, width=15, background='#E67E22', foreground='white', borderwidth=0, date_pattern='yyyy-mm-dd', font=('Arial', 12))
        self.cal_end.pack(fill="x")

        ctk.CTkButton(date_frame, text="🔍 Lọc KQ", width=100, height=35, font=ctk.CTkFont(weight="bold"), fg_color="#3498DB", hover_color="#2980B9", text_color="white", command=self.load_history).pack(side="bottom")

        # --- BẢNG DANH SÁCH ---
        style = ttk.Style()
        style.configure("History.Treeview", background="#212121", foreground="white", rowheight=40, fieldbackground="#212121", borderwidth=0)
        style.map("History.Treeview", background=[('selected', '#E67E22')])
        style.configure("History.Treeview.Heading", background="#333333", foreground="white", font=('Arial', 11, 'bold'), padding=5)

        columns = ("id", "ma_don", "thoi_gian", "tong_tien", "trang_thai")
        self.tree = ttk.Treeview(self.left_frame, columns=columns, show="headings", style="History.Treeview")
        self.tree.heading("id", text="ID"); self.tree.column("id", width=0, stretch=False)
        self.tree.heading("ma_don", text="Mã Đơn"); self.tree.column("ma_don", width=120, anchor="center")
        self.tree.heading("thoi_gian", text="Thời Gian"); self.tree.column("thoi_gian", width=150, anchor="center")
        self.tree.heading("tong_tien", text="Doanh Thu"); self.tree.column("tong_tien", width=120, anchor="e")
        self.tree.heading("trang_thai", text="Trạng Thái"); self.tree.column("trang_thai", width=120, anchor="center")
        
        # Thêm Scrollbar
        scrollbar = ttk.Scrollbar(self.left_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y", pady=(0, 20), padx=(0, 20))
        
        self.tree.pack(fill="both", expand=True, padx=(20, 0), pady=(0, 20))
        self.tree.bind("<ButtonRelease-1>", self.on_order_select)

    def build_right_pane(self):
        # Giao diện Phải mô phỏng tờ Bill thật
        self.right_frame = ctk.CTkFrame(self, corner_radius=12, fg_color="#212121", border_width=1, border_color="#333333")
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        # Header Chi Tiết
        self.header_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(self.header_frame, text="🧾 CHI TIẾT HÓA ĐƠN", font=ctk.CTkFont(size=14, weight="bold"), text_color="#AAAAAA").pack(anchor="w")
        self.lbl_ma_don = ctk.CTkLabel(self.header_frame, text="--", font=ctk.CTkFont(size=22, weight="bold"), text_color="white")
        self.lbl_ma_don.pack(anchor="w", pady=(5, 0))
        self.lbl_thoi_gian = ctk.CTkLabel(self.header_frame, text="--", font=ctk.CTkFont(size=12), text_color="#AAAAAA")
        self.lbl_thoi_gian.pack(anchor="w")

        ctk.CTkFrame(self.right_frame, height=1, fg_color="#333333").pack(fill="x", padx=20)

        # Danh sách món (Scrollable)
        self.item_list = ctk.CTkScrollableFrame(self.right_frame, fg_color="transparent")
        self.item_list.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkFrame(self.right_frame, height=1, fg_color="#333333").pack(fill="x", padx=20)

        # Khung Kế Toán (Bổ sung đầy đủ thông tin Khách đưa, Tiền thừa)
        self.summary_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.summary_frame.pack(fill="x", padx=20, pady=15)

        self.row_giam_gia = ctk.CTkFrame(self.summary_frame, fg_color="transparent")
        self.row_giam_gia.pack(fill="x", pady=2)
        ctk.CTkLabel(self.row_giam_gia, text="Giảm giá:", font=ctk.CTkFont(size=13)).pack(side="left")
        self.lbl_giam_gia = ctk.CTkLabel(self.row_giam_gia, text="0 đ", font=ctk.CTkFont(size=13, weight="bold"), text_color="#2ECC71")
        self.lbl_giam_gia.pack(side="right")
        
        self.row_khach_dua = ctk.CTkFrame(self.summary_frame, fg_color="transparent")
        self.row_khach_dua.pack(fill="x", pady=2)
        ctk.CTkLabel(self.row_khach_dua, text="Khách đưa:", font=ctk.CTkFont(size=13)).pack(side="left")
        self.lbl_khach_dua = ctk.CTkLabel(self.row_khach_dua, text="0 đ", font=ctk.CTkFont(size=13))
        self.lbl_khach_dua.pack(side="right")
        
        self.row_tien_thua = ctk.CTkFrame(self.summary_frame, fg_color="transparent")
        self.row_tien_thua.pack(fill="x", pady=2)
        ctk.CTkLabel(self.row_tien_thua, text="Tiền thừa:", font=ctk.CTkFont(size=13)).pack(side="left")
        self.lbl_tien_thua = ctk.CTkLabel(self.row_tien_thua, text="0 đ", font=ctk.CTkFont(size=13))
        self.lbl_tien_thua.pack(side="right")

        self.row_tong = ctk.CTkFrame(self.summary_frame, fg_color="transparent")
        self.row_tong.pack(fill="x", pady=(10, 5))
        ctk.CTkLabel(self.row_tong, text="TỔNG THU KẾ TOÁN:", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        self.lbl_tong_tien = ctk.CTkLabel(self.row_tong, text="0 đ", font=ctk.CTkFont(size=20, weight="bold"), text_color="#E74C3C")
        self.lbl_tong_tien.pack(side="right")

        # Nút thao tác [TỐI ƯU ĐỘ TƯƠNG PHẢN, CHỮ TO TRẮNG ĐẬM]
        action_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.btn_reprint = ctk.CTkButton(action_frame, text="🖨️ In Lại", height=45, font=ctk.CTkFont(size=13, weight="bold"), text_color="white", fg_color="#2980B9", hover_color="#1A5276", state="disabled", command=self.reprint_bill)
        self.btn_reprint.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btn_edit = ctk.CTkButton(action_frame, text="✏️ Sửa Đơn", height=45, font=ctk.CTkFont(size=13, weight="bold"), text_color="white", fg_color="#D35400", hover_color="#A04000", state="disabled", command=self.edit_order)
        self.btn_edit.pack(side="left", fill="x", expand=True, padx=(5, 5))

        self.btn_void = ctk.CTkButton(action_frame, text="❌ Hủy (Hoàn tiền)", height=45, font=ctk.CTkFont(size=13, weight="bold"), text_color="white", fg_color="#C0392B", hover_color="#922B21", state="disabled", command=self.void_order)
        self.btn_void.pack(side="left", fill="x", expand=True, padx=(5, 0))

    def set_today(self):
        today = datetime.datetime.now().date()
        self.cal_start.set_date(today)
        self.cal_end.set_date(today)
        self.load_history()

    def load_history(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        self.clear_details()

        start_date = self.cal_start.get()
        end_date = self.cal_end.get()

        orders = self.controller.get_history_orders(start_date, end_date)
        for o in orders:
            raw_time = o[5] 
            try:
                dt = datetime.datetime.strptime(raw_time, "%Y-%m-%d %H:%M:%S")
                time_str = dt.strftime("%d/%m %H:%M") 
            except:
                time_str = str(raw_time) if raw_time else "--"
            
            tong_tien_str = f"{o[3]:,.0f} đ".replace(",", ".")
            self.tree.insert("", "end", values=(o[0], o[1], time_str, tong_tien_str, o[4]))

    def on_order_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        
        row = self.tree.item(sel[0], "values")
        self.current_selected_order_id = int(row[0])
        trang_thai = row[4]

        summary = self.controller.get_order_summary(self.current_selected_order_id)
        items = self.controller.get_order_items(self.current_selected_order_id)

        self.lbl_ma_don.configure(text=f"{summary['ma_don']} ({summary['loai_don']})")
        
        time_text = f"Thời gian: {summary.get('local_time', '--')}"
        if trang_thai == 'Đã Hủy':
            time_text += " [ĐÃ HỦY ĐƠN / ĐÃ HOÀN TIỀN]"
            self.lbl_thoi_gian.configure(text=time_text, text_color="#E74C3C")
            self.btn_void.configure(state="disabled") 
            self.btn_edit.configure(state="disabled")
        else:
            self.lbl_thoi_gian.configure(text=time_text, text_color="#AAAAAA")
            self.btn_void.configure(state="normal")
            self.btn_edit.configure(state="normal")
            
        self.btn_reprint.configure(state="normal")

        for widget in self.item_list.winfo_children(): widget.destroy()
        
        for item in items:
            card = ctk.CTkFrame(self.item_list, fg_color="#121212", corner_radius=6)
            card.pack(fill="x", pady=2)
            ctk.CTkLabel(card, text=f"{item[3]}x", font=ctk.CTkFont(weight="bold"), text_color="#3498DB").pack(side="left", padx=(10, 5), pady=10)
            ctk.CTkLabel(card, text=f"{item[2]}", font=ctk.CTkFont(weight="bold")).pack(side="left", pady=10)
            ctk.CTkLabel(card, text=f"{item[6]:,.0f} đ".replace(",", "."), text_color="#E67E22").pack(side="right", padx=10, pady=10)

        # Cập nhật thông số Kế toán
        giam_gia = summary.get('tien_giam_gia', 0)
        khach_dua = summary.get('tien_khach_dua', 0)
        tien_thua = summary.get('tien_thua', 0)
        
        self.lbl_giam_gia.configure(text=f"- {giam_gia:,.0f} đ".replace(",", "."))
        self.lbl_khach_dua.configure(text=f"{khach_dua:,.0f} đ".replace(",", "."))
        self.lbl_tien_thua.configure(text=f"{tien_thua:,.0f} đ".replace(",", "."))
        self.lbl_tong_tien.configure(text=f"{summary['tong_tien']:,.0f} đ".replace(",", "."))

    def edit_order(self):
        if not self.current_selected_order_id: return
        
        # [UX]: Thông báo rõ ràng, giải thích cặn kẽ đường đi nước bước
        msg = (
            "Hóa đơn sẽ được mở lại để chỉnh sửa!\n\n"
            "👉 HƯỚNG DẪN TÌM LẠI ĐƠN:\n"
            "- Nếu Bàn cũ ĐANG TRỐNG: Đơn đã được đặt lại đúng bàn đó.\n"
            "- Nếu Bàn cũ ĐÃ CÓ KHÁCH: Hệ thống tự động chuyển đơn này vào mục [MANG VỀ] để tránh trùng lặp.\n\n"
            "Vui lòng sang tab [Bàn & Gọi Món] để tìm lại đơn này và thanh toán lại."
        )
        
        confirm = messagebox.askyesno("Xác nhận Sửa Hóa Đơn", msg)
        
        if confirm:
            try:
                self.controller.reopen_order(self.current_selected_order_id)
                self.load_history()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")

    def void_order(self):
        if not self.current_selected_order_id: return
        confirm = messagebox.askyesno(
            "Cảnh báo Kế toán", 
            "Việc hủy hóa đơn sẽ đưa doanh thu đơn này về 0 đ và tự động hoàn trả nguyên liệu vào kho.\n\nBạn có chắc chắn muốn thực hiện?"
        )
        if confirm:
            try:
                self.controller.void_paid_order(self.current_selected_order_id)
                messagebox.showinfo("Thành công", "Đã hủy hóa đơn và hoàn trả kho thành công!")
                self.load_history()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")

    def reprint_bill(self):
        if not self.current_selected_order_id: return
        summary = self.controller.get_order_summary(self.current_selected_order_id)
        items = self.controller.get_order_items(self.current_selected_order_id)
        try:
            self.printer.print_receipt(
                order_id=self.current_selected_order_id,
                table_name=f"In lại ({summary['loai_don']})",
                items=items,
                total=summary['tong_tien'],
                tien_khach_dua=summary['tien_khach_dua'],
                tien_thua=summary['tien_thua']
            )
            messagebox.showinfo("Thành công", "Đã gửi lệnh in!")
        except Exception as e:
            messagebox.showerror("Lỗi Máy In", str(e))

    def clear_details(self):
        self.current_selected_order_id = None
        self.lbl_ma_don.configure(text="--")
        self.lbl_thoi_gian.configure(text="--", text_color="#AAAAAA")
        for widget in self.item_list.winfo_children(): widget.destroy()
        self.lbl_giam_gia.configure(text="0 đ")
        self.lbl_khach_dua.configure(text="0 đ")
        self.lbl_tien_thua.configure(text="0 đ")
        self.lbl_tong_tien.configure(text="0 đ")
        self.btn_reprint.configure(state="disabled")
        self.btn_edit.configure(state="disabled")
        self.btn_void.configure(state="disabled")