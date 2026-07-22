import customtkinter as ctk
from src.views.pos.page_pos_main import PagePOS
from src.views.page_menu import PageMenu
from src.views.page_stock import PageStock
from src.views.page_report import PageReport
from src.views.page_data import PageData
from src.views.page_history import PageHistory # Import Trang Lịch Sử
from src.views.page_account import PageAccount # Import Trang Tài Khoản
from src.utils import session

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Phần Mềm Quản Lý Quán Cà Phê - Offline v1.0")
        self.geometry("1200x700")
        self.after(0, lambda: self.state('zoomed'))
        ctk.set_appearance_mode("Dark") 

        # --- BỐ CỤC CHÍNH ---
        # 1. Thanh Menu bên trái (Sidebar)
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#212121")
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)

        # Logo text
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="COFFEE SHOP", font=ctk.CTkFont(size=22, weight="bold"), text_color="#E67E22")
        self.logo_label.pack(padx=20, pady=(20, 10))

        # --- AVATAR & TÊN TÀI KHOẢN ---
        self.user_profile_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.user_profile_frame.pack(pady=(0, 15))

        user_name = session.current_user["ho_ten"]
        first_letter = user_name[0].upper() if user_name else "U"

        # Vòng tròn Avatar (Dùng corner_radius = 1/2 kích thước để thành hình tròn)
        self.avatar_lbl = ctk.CTkLabel(self.user_profile_frame, text=first_letter, font=ctk.CTkFont(size=24, weight="bold"), 
                                       width=50, height=50, corner_radius=25, fg_color="#E67E22", text_color="white")
        self.avatar_lbl.pack(pady=(0, 5))

        # Tên tài khoản hiển thị
        self.name_lbl = ctk.CTkLabel(self.user_profile_frame, text=user_name, font=ctk.CTkFont(size=14, weight="bold"), text_color="#BDC3C7")
        self.name_lbl.pack()

        ctk.CTkFrame(self.sidebar_frame, height=1, fg_color="#333333").pack(fill="x", padx=20, pady=(0, 10))

        # --- NÚT ĐIỀU HƯỚNG ---
        self.nav_buttons = []

        def create_nav_button(text, command):
            btn = ctk.CTkButton(
                self.sidebar_frame, text=text, font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="transparent", text_color="#AAAAAA", hover_color="#333333",
                anchor="w", height=45, command=command
            )
            btn.pack(fill="x", padx=15, pady=2)
            self.nav_buttons.append(btn)
            return btn

        # Kiểm tra quyền
        if session.current_user["quyen_ban_hang"] == 1:
            self.btn_pos = create_nav_button("🏠  Bàn & Gọi Món", lambda: self.handle_nav_click(self.btn_pos, self.show_pos))
            
        if session.current_user["quyen_do_uong"] == 1:
            self.btn_menu = create_nav_button("☕  Quản Lý Đồ Uống", lambda: self.handle_nav_click(self.btn_menu, self.show_menu))
            
        if session.current_user["quyen_kho"] == 1:
            self.btn_stock = create_nav_button("📦  Quản Lý Kho", lambda: self.handle_nav_click(self.btn_stock, self.show_stock))
            
        if session.current_user["quyen_thong_ke"] == 1:
            self.btn_report = create_nav_button("📊  Thống Kê Doanh Thu", lambda: self.handle_nav_click(self.btn_report, self.show_report))

        if session.current_user["quyen_lich_su"] == 1:
            self.btn_history = create_nav_button("📜  Lịch Sử Hóa Đơn", lambda: self.handle_nav_click(self.btn_history, self.show_history))
            
        if session.current_user["quyen_tai_khoan"] == 1:
            self.btn_account = create_nav_button("👥  Quản Lý Tài Khoản", lambda: self.handle_nav_click(self.btn_account, self.show_account))
            
        if session.current_user["quyen_du_lieu"] == 1:
            self.btn_data = create_nav_button("⚙️  Quản Lý Dữ Liệu", lambda: self.handle_nav_click(self.btn_data, self.show_data))

        # --- ĐÁY SIDEBAR (Developer & Nút Đăng Xuất) ---
        # Khung chứa Dev Info nằm sát đáy
        self.dev_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.dev_frame.pack(side="bottom", fill="x", pady=(0, 20))
        
        ctk.CTkFrame(self.dev_frame, height=1, fg_color="#333333").pack(fill="x", padx=20, pady=(0, 15))
        ctk.CTkLabel(self.dev_frame, text="Developer: Ngô Văn Chương", text_color="#7F8C8D", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=20)

        # Nút Đăng xuất màu đỏ xếp trên Dev Info
        self.btn_logout = ctk.CTkButton(
            self.sidebar_frame, text="🚪  Đăng Xuất", font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="transparent", text_color="#E74C3C", hover_color="#C0392B",
            anchor="w", height=45, command=self.logout
        )
        self.btn_logout.pack(side="bottom", fill="x", padx=15, pady=(10, 5))

        # 2. Vùng hiển thị nội dung bên phải
        self.content_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#121212")
        self.content_frame.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        self.page_pos = PagePOS(self.content_frame)
        self.page_history = PageHistory(self.content_frame) # Khởi tạo trang Lịch sử
        self.page_menu = PageMenu(self.content_frame)
        self.page_stock = PageStock(self.content_frame)
        self.page_report = PageReport(self.content_frame)
        self.page_data = PageData(self.content_frame)
        self.page_account = PageAccount(self.content_frame) # Khởi tạo trang Tài khoản

        # Tự động mở trang đầu tiên
        if hasattr(self, 'btn_pos'): self.handle_nav_click(self.btn_pos, self.show_pos)
        elif hasattr(self, 'btn_account'): self.handle_nav_click(self.btn_account, self.show_account)

    # --- HÀM XỬ LÝ (Thêm hàm show cho 2 trang mới) ---
    def handle_nav_click(self, clicked_btn, func_to_call):
        for btn in self.nav_buttons:
            btn.configure(fg_color="transparent", text_color="#AAAAAA")
        clicked_btn.configure(fg_color="#E67E22", text_color="white")
        func_to_call()

# --- HÀM XỬ LÝ CHUYỂN TRANG (ĐÃ TÍCH HỢP TỰ ĐỘNG LÀM MỚI DỮ LIỆU) ---
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.pack_forget()

    def show_pos(self):
        self.clear_content()
        # Tự động làm mới sơ đồ bàn và danh sách món ăn bên trang POS
        if hasattr(self.page_pos, 'left_pane'):
            self.page_pos.left_pane.refresh_tables()
            self.page_pos.left_pane.refresh_menu()
        self.page_pos.pack(fill="both", expand=True)
        
    def show_history(self):
        self.clear_content()
        # Tự động nạp lại lịch sử hóa đơn khi bấm sang trang này
        if hasattr(self.page_history, 'load_history'):
            self.page_history.load_history()
        self.page_history.pack(fill="both", expand=True)

    def show_menu(self):
        self.clear_content()
        # Đã có sẵn hàm refresh đồ uống
        if hasattr(self.page_menu, 'refresh_menu_list'):
            self.page_menu.refresh_menu_list() 
        self.page_menu.pack(fill="both", expand=True)

    def show_stock(self):
        self.clear_content()
        # Đã có sẵn hàm refresh kho
        if hasattr(self.page_stock, 'refresh_stock_list'):
            self.page_stock.refresh_stock_list()
        self.page_stock.pack(fill="both", expand=True)

    def show_report(self):
        self.clear_content()
        # Nếu trang thống kê có hàm load dữ liệu, tự động gọi
        if hasattr(self.page_report, 'load_report'):
            self.page_report.load_report()
        self.page_report.pack(fill="both", expand=True)

    def show_data(self):
        self.clear_content()
        if hasattr(self.page_data, 'load_data'):
            self.page_data.load_data()
        self.page_data.pack(fill="both", expand=True)

    def show_account(self):
        self.clear_content()
        # Tự động load lại danh sách tài khoản nhân viên
        if hasattr(self.page_account, 'load_data'):
            self.page_account.load_data()
        self.page_account.pack(fill="both", expand=True)
        
    def logout(self):
        self.destroy() 
        session.logout() 
        from main import launch_login_app
        launch_login_app()