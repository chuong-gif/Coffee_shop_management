# Khung giao diện chính (Gồm Sidebar menu bên trái + Vùng hiển thị nội dung)
import customtkinter as ctk

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Cấu hình cửa sổ chính
        self.title("Phần Mềm Quản Lý Quán Cà Phê - Offline v1.0")
        self.geometry("1100x650")
        
        # Đặt chế độ giao diện (Hệ thống tự nhận Dark/Light mode của Windows)
        ctk.set_appearance_mode("System") 
        ctk.set_default_color_theme("blue")

        # --- BỐ CỤC CHÍNH (Layout) ---
        # 1. Thanh Menu bên trái (Sidebar)
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.pack(side="left", fill="y", padx=0, pady=0)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="COFFEE SHOP", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(padx=20, pady=20)

        # Các nút bấm chuyển trang trên Sidebar
        self.btn_pos = ctk.CTkButton(self.sidebar_frame, text="Trang Bàn & Gọi Món", command=self.show_pos)
        self.btn_pos.pack(padx=20, pady=10, fill="x")

        self.btn_menu = ctk.CTkButton(self.sidebar_frame, text="Quản Lý Đồ Uống", command=self.show_menu)
        self.btn_menu.pack(padx=20, pady=10, fill="x")

        self.btn_stock = ctk.CTkButton(self.sidebar_frame, text="Quản Lý Kho", command=self.show_stock)
        self.btn_stock.pack(padx=20, pady=10, fill="x")

        self.btn_report = ctk.CTkButton(self.sidebar_frame, text="Thống Kê Doanh Thu", command=self.show_report)
        self.btn_report.pack(padx=20, pady=10, fill="x")

        self.btn_data = ctk.CTkButton(self.sidebar_frame, text="Quản Lý Dữ Liệu", command=self.show_data)
        self.btn_data.pack(padx=20, pady=10, fill="x")

        # 2. Vùng hiển thị nội dung bên phải (Content Area)
        self.content_frame = ctk.CTkFrame(self, corner_radius=10)
        self.content_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.status_label = ctk.CTkLabel(self.content_frame, text="Chào mừng bạn đến với hệ thống quản lý!", font=ctk.CTkFont(size=16))
        self.status_label.pack(expand=True)

    # --- CÁC HÀM XỬ LÝ CHUYỂN TRANG (Tạm thời thay đổi chữ hiển thị) ---
    def show_pos(self):
        self.status_label.configure(text="Đây là không gian hiển thị Sơ đồ bàn & Bán hàng (Trang 1)")

    def show_menu(self):
        self.status_label.configure(text="Đây là không gian quản lý Menu đồ uống (Trang 2)")

    def show_stock(self):
        self.status_label.configure(text="Đây là không gian Quản lý Kho & Kiểm kho hao hụt (Trang 3)")

    def show_report(self):
        self.status_label.configure(text="Đây là không gian xem Biểu đồ & Doanh thu lãi lỗ (Trang 4)")

    def show_data(self):
        self.status_label.configure(text="Đây là cấu hình dán link Google Drive Auto-Backup (Trang 5)")