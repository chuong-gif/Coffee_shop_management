# File khởi chạy chính của toàn bộ phần mềm
import sys
from src.views.main_window import MainWindow
from src.models.db_manager import DatabaseManager

def main():
    
    # Khởi tạo database trước khi mở giao diện
    db = DatabaseManager()
    db.init_database()
    # Khởi tạo ứng dụng
    app = MainWindow()
    # Giữ ứng dụng luôn chạy cho đến khi người dùng bấm tắt
    app.mainloop()

if __name__ == "__main__":
    main()