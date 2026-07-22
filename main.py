import customtkinter as ctk
from PIL import Image
import os
import sys

# Khởi tạo giao diện ứng dụng chính
from src.views.main_window import MainWindow
from src.views.login_window import LoginWindow

class SplashScreen(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Ẩn viền và thanh tiêu đề của Windows
        self.overrideredirect(True)
        
        # Kích thước màn hình load
        width = 600
        height = 350
        
        # Tính toán để căn giữa màn hình
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.geometry(f'{width}x{height}+{int(x)}+{int(y)}')
        
        self.configure(fg_color="#121212")

        # --- NỘI DUNG MÀN HÌNH CHỜ ---
        # 1. Khung chứa Logo (Anh có thể thay đường dẫn ảnh logo của anh vào đây)
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
        if os.path.exists(logo_path):
            img = ctk.CTkImage(light_image=Image.open(logo_path), size=(100, 100))
            ctk.CTkLabel(self, image=img, text="").pack(pady=(40, 10))
        else:
            # Nếu chưa có ảnh, dùng icon mặc định
            ctk.CTkLabel(self, text="☕", font=ctk.CTkFont(size=60)).pack(pady=(40, 10))

        # 2. Tiêu đề phần mềm
        ctk.CTkLabel(self, text="COFFEE SHOP POS", font=ctk.CTkFont(size=24, weight="bold"), text_color="#E67E22").pack()
        ctk.CTkLabel(self, text="Phiên bản Offline v1.0", font=ctk.CTkFont(size=12), text_color="#AAAAAA").pack(pady=(0, 20))

        # 3. Thanh tiến trình (Progress Bar)
        self.progress = ctk.CTkProgressBar(self, width=400, height=8, progress_color="#E67E22", fg_color="#333333", corner_radius=4)
        self.progress.pack(pady=10)
        self.progress.set(0)
        
        self.lbl_loading = ctk.CTkLabel(self, text="Đang khởi tạo hệ thống...", font=ctk.CTkFont(size=11), text_color="#AAAAAA")
        self.lbl_loading.pack()

        # 4. Bản quyền tác giả (Chuyên nghiệp)
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", pady=20)
        ctk.CTkLabel(bottom_frame, text="Được thiết kế và phát triển độc quyền bởi", font=ctk.CTkFont(size=10), text_color="#7F8C8D").pack()
        ctk.CTkLabel(bottom_frame, text="NGÔ VĂN CHƯƠNG", font=ctk.CTkFont(size=12, weight="bold"), text_color="#BDC3C7").pack()

        # Bắt đầu vòng lặp load
        self.progress_val = 0
        self.update_progress()

    def update_progress(self):
        self.progress_val += 0.05
        self.progress.set(self.progress_val)
        
        # Cập nhật text sinh động
        if self.progress_val > 0.3: self.lbl_loading.configure(text="Đang kết nối cơ sở dữ liệu...")
        if self.progress_val > 0.6: self.lbl_loading.configure(text="Đang tải cấu hình giao diện...")
        if self.progress_val > 0.9: self.lbl_loading.configure(text="Hoàn tất. Đang mở hệ thống...")

        if self.progress_val < 1.0:
            self.after(50, self.update_progress) # Tốc độ load (50ms)
        else:
            self.destroy() # Đóng màn hình load
            launch_login_app() # ĐỔI: Gọi màn hình đăng nhập

# Hàm mở màn hình chính (Sau khi đăng nhập thành công)
def launch_main_app():
    app = MainWindow()
    app.mainloop()

# Hàm mở màn hình đăng nhập
def launch_login_app():
    # Khởi tạo form đăng nhập, truyền hàm launch_main_app vào làm callback
    login_app = LoginWindow(on_login_success=launch_main_app)
    login_app.mainloop()

if __name__ == "__main__":
    splash = SplashScreen()
    splash.mainloop()