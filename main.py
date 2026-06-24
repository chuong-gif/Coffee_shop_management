# File khởi chạy chính của toàn bộ phần mềm
import sys
from src.views.main_window import MainWindow

def main():
    # Khởi tạo ứng dụng
    app = MainWindow()
    # Giữ ứng dụng luôn chạy cho đến khi người dùng bấm tắt
    app.mainloop()

if __name__ == "__main__":
    main()