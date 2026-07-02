import customtkinter as ctk
from src.views.pos.page_pos_main import PagePOS
from src.views.page_menu import PageMenu
from src.views.page_stock import PageStock
from src.views.page_report import PageReport
from src.views.page_data import PageData

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Phần Mềm Quản Lý Quán Cà Phê - Offline v1.0")
        self.geometry("1200x700")
        
        # Lệnh ép ứng dụng mở Toàn Màn Hình (Maximize) ngay từ đầu
        self.after(0, lambda: self.state('zoomed'))
        
        ctk.set_appearance_mode("Dark") 

        # --- BỐ CỤC CHÍNH ---
        # 1. Thanh Menu bên trái (Sidebar) - Đổi sang màu trùng với các Card
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#212121")
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False) # Giữ cứng width

        # Logo text
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="COFFEE SHOP", font=ctk.CTkFont(size=22, weight="bold"), text_color="#E67E22")
        self.logo_label.pack(padx=20, pady=(30, 30))

        # Danh sách chứa các nút để xử lý hiệu ứng đổi màu
        self.nav_buttons = []

        def create_nav_button(text, command):
            btn = ctk.CTkButton(
                self.sidebar_frame, 
                text=text, 
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="transparent", 
                text_color="#AAAAAA", 
                hover_color="#333333",
                anchor="w", 
                height=45,
                command=command
            )
            btn.pack(fill="x", padx=15, pady=5)
            self.nav_buttons.append(btn)
            return btn

        # Thêm Icon (Emoji chuẩn) vào các nút
        self.btn_pos = create_nav_button("🏠  Bàn & Gọi Món", lambda: self.handle_nav_click(self.btn_pos, self.show_pos))
        self.btn_menu = create_nav_button("☕  Quản Lý Đồ Uống", lambda: self.handle_nav_click(self.btn_menu, self.show_menu))
        self.btn_stock = create_nav_button("📦  Quản Lý Kho", lambda: self.handle_nav_click(self.btn_stock, self.show_stock))
        self.btn_report = create_nav_button("📊  Thống Kê Doanh Thu", lambda: self.handle_nav_click(self.btn_report, self.show_report))
        self.btn_data = create_nav_button("⚙️  Quản Lý Dữ Liệu", lambda: self.handle_nav_click(self.btn_data, self.show_data))

        # Khung thông tin Developer ở dưới cùng
        self.dev_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.dev_frame.pack(side="bottom", fill="x", pady=20)
        
        ctk.CTkFrame(self.dev_frame, height=1, fg_color="#333333").pack(fill="x", padx=20, pady=(0, 15))
        ctk.CTkLabel(self.dev_frame, text="Developer:", text_color="#7F8C8D", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=20)
        ctk.CTkLabel(self.dev_frame, text="Ngô Văn Chương", text_color="#BDC3C7", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=20, pady=(0, 5))
        ctk.CTkLabel(self.dev_frame, text="Email:", text_color="#7F8C8D", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=20)
        ctk.CTkLabel(self.dev_frame, text="chuongngo171005@gmail.com", text_color="#3498DB", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=20)

        # 2. Vùng hiển thị nội dung bên phải
        self.content_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#121212")
        self.content_frame.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        self.page_pos = PagePOS(self.content_frame)
        self.page_menu = PageMenu(self.content_frame)
        self.page_stock = PageStock(self.content_frame)
        self.page_report = PageReport(self.content_frame)
        self.page_data = PageData(self.content_frame)

        # Mặc định khởi động vào trang POS
        self.handle_nav_click(self.btn_pos, self.show_pos)

    # --- HÀM XỬ LÝ GIAO DIỆN NÚT BẤM (ACTIVE STATE) ---
    def handle_nav_click(self, clicked_btn, func_to_call):
        """Đổi màu nút đang được chọn để người dùng biết mình đang ở trang nào"""
        for btn in self.nav_buttons:
            btn.configure(fg_color="transparent", text_color="#AAAAAA")
        
        # Highlight nút đang chọn
        clicked_btn.configure(fg_color="#E67E22", text_color="white")
        
        # Gọi hàm chuyển trang
        func_to_call()

    # --- HÀM XỬ LÝ CHUYỂN TRANG ---
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.pack_forget()

    def show_pos(self):
        self.clear_content()
        self.page_pos.pack(fill="both", expand=True)
        
    def show_menu(self):
        self.clear_content()
        self.page_menu.refresh_menu_list() 
        self.page_menu.pack(fill="both", expand=True)

    def show_stock(self):
        self.clear_content()
        self.page_stock.refresh_stock_list()
        self.page_stock.pack(fill="both", expand=True)

    def show_report(self):
        self.clear_content()
        self.page_report.pack(fill="both", expand=True)

    def show_data(self):
        self.clear_content()
        self.page_data.pack(fill="both", expand=True)