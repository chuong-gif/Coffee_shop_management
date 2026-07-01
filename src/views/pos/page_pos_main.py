import tkinter as tk
import customtkinter as ctk
import tkinter.messagebox as messagebox
from src.controllers.order_controller import OrderController
from src.views.pos.left_pane import LeftPane
from src.views.pos.right_pane import RightPane
 
class PagePOS(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="#121212")
        self.controller = OrderController()
 
        # [FIX #4/#5]: Dùng PanedWindow thay vì grid tỉ lệ cố định 6:4
        # -> Kéo được thanh chia để thu hẹp/mở rộng khung hóa đơn bên phải.
        self.paned = tk.PanedWindow(
            self, orient="horizontal", sashwidth=6, sashrelief="flat",
            bg="#121212", bd=0, opaqueresize=True
        )
        self.paned.pack(fill="both", expand=True, padx=20, pady=20)
 
        # Khởi tạo 2 Component Trái Phải và nhúng Callback
        self.left_pane = LeftPane(self.paned, self.controller,
                                  on_table_select=self.handle_table_selected,
                                  on_item_add=self.handle_item_added)
 
        self.right_pane = RightPane(self.paned, self.controller,
                                    on_bill_cleared=self.handle_bill_cleared)
 
        # minsize để 2 bên không bị kéo mất hẳn.
        # [FIX]: stretch="always" -> khi cửa sổ được resize/phóng to, phần không gian dư
        # được CHIA TỈ LỆ cho cả 2 khung, thay vì mặc định Tk dồn hết cho khung cuối (bên phải)
        # khiến khung hóa đơn "nở" bất thường khi full màn hình.
        self.paned.add(self.left_pane, minsize=460, stretch="always")
        self.paned.add(self.right_pane, minsize=320, stretch="always")
 
        # [FIX]: Đặt vị trí thanh chia ban đầu dựa trên sự kiện <Configure> đầu tiên có kích
        # thước thật (thay vì đoán bằng timer cố định 60ms, dễ chạy trước khi cửa sổ có kích
        # thước thật khi mở full màn hình ngay từ đầu).
        self._sash_initialized = False
        self.paned.bind("<Configure>", self._on_paned_configure)
 
        # Khởi động tải dữ liệu lần đầu
        self.left_pane.refresh_tables()
        self.left_pane.refresh_menu()
 
    def _on_paned_configure(self, event):
        if not self._sash_initialized and event.width > 300:
            self._sash_initialized = True
            self.after(10, lambda w=event.width: self._set_initial_sash(w))
 
    def _set_initial_sash(self, width=None):
        try:
            w = width or self.paned.winfo_width()
            if w > 100:
                self.paned.sash_place(0, int(w * 0.68), 0)
        except Exception:
            pass
 
    # --- LUỒNG ĐIỀU PHỐI (ORCHESTRATOR) ---
 
    def handle_table_selected(self, table_id, table_name):
        """Khi bấm vào một bàn bên trái -> Tải bill sang bên phải"""
        if table_id is None and table_name == "Đơn Mang Về":
            # [FIX #1]: Chỉ xem thử có đơn Mang Về đang mở không, KHÔNG tạo đơn mới ở đây.
            order_data = self.controller.get_takeaway_pane_data()
            self.right_pane.load_order(order_data["order_id"], None, "Mang Về")
        else:
            order_data = self.controller.handle_table_click(table_id, table_name)
            self.right_pane.load_order(order_data["order_id"], table_id, table_name)
 
    def handle_item_added(self, do_uong_id):
        """Khi bấm [+] món bên trái -> Thêm vào bill bên phải"""
        t_id = self.right_pane.current_table_id
        o_id = self.right_pane.current_order_id
        t_name = self.right_pane.lbl_table_name.cget("text").split("(")[0].strip().replace("📄 ", "")
 
        # Chưa chọn Bàn và cũng chưa chọn Mang Về -> báo lỗi
        if t_id is None and o_id is None and t_name != "Mang Về":
            return messagebox.showwarning("Lỗi", "Hãy chọn Bàn hoặc Đơn Mang Về trước!")
 
        # [FIX #1]: Chỉ tạo đơn (dù là Bàn hay Mang Về) tại thời điểm món ĐẦU TIÊN được thêm
        if not o_id:
            if t_name == "Mang Về":
                order_data = self.controller.create_takeaway_order()
            else:
                order_data = self.controller.open_table_order(t_id, t_name)
                self.left_pane.refresh_tables()  # Bàn đổi sang màu đỏ
            o_id = order_data["order_id"]
 
        # Thêm món vào Database
        self.controller.add_item_to_order(t_id, do_uong_id, order_id=o_id)
 
        # Báo cho bên phải tải lại Bill
        self.right_pane.load_order(o_id, t_id, t_name)
 
    def handle_bill_cleared(self):
        """Khi Thanh toán xong, Hủy đơn, hoặc bill trống hẳn -> Báo bên trái reset bàn về Xanh"""
        self.left_pane.selected_table_id = None
        self.left_pane.refresh_tables()