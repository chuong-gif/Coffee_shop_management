# Khung giao diện chính (Gồm Sidebar menu bên trái + Vùng hiển thị nội dung)
import customtkinter as ctk
from src.views.pos.page_pos_main import PagePOS
from src.views.page_menu import PageMenu
from src.views.page_stock import PageStock
from src.views.page_report import PageReport
from src.views.page_data import PageData

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

        # Khởi tạo các trang giao diện (hiện tại mới có trang POS)
        self.page_pos = PagePOS(self.content_frame)
        self.page_menu = PageMenu(self.content_frame)
        self.page_stock = PageStock(self.content_frame)
        self.page_report = PageReport(self.content_frame)
        self.page_data = PageData(self.content_frame)

        # Mặc định khi mở app sẽ hiển thị trang Bán hàng (POS)
        self.show_pos()

    # --- HÀM XỬ LÝ CHUYỂN TRANG ---
    def clear_content(self):
        """Hàm dùng để xóa giao diện trang cũ trước khi tải trang mới lên"""
        for widget in self.content_frame.winfo_children():
            widget.pack_forget()

    def show_pos(self): # trang 1: Trang đặt bàn
        self.clear_content() # Xóa trang cũ đi
        self.page_pos.pack(fill="both", expand=True) # Hiện trang POS lên
        
    def show_menu(self): # trang 2: menu
        self.clear_content()
        self.page_menu.refresh_menu_list() # Lấy dữ liệu mới nhất từ DB
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
