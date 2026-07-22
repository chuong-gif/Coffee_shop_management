import customtkinter as ctk
import sqlite3
import hashlib
from src.config import DB_PATH
from src.utils import session

class LoginWindow(ctk.CTk):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success 
        
        self.title("Đăng nhập hệ thống")
        self.geometry("400x500")
        self.resizable(False, False)
        self.configure(fg_color="#121212")
        
        self.lbl_title = ctk.CTkLabel(self, text="ĐĂNG NHẬP", font=ctk.CTkFont(size=24, weight="bold"), text_color="#E67E22")
        self.lbl_title.pack(pady=(60, 30))
        
        self.txt_username = ctk.CTkEntry(self, placeholder_text="Tên đăng nhập", width=250, height=40)
        self.txt_username.pack(pady=10)
        
        self.txt_password = ctk.CTkEntry(self, placeholder_text="Mật khẩu", show="*", width=250, height=40)
        self.txt_password.pack(pady=10)
        
        self.lbl_error = ctk.CTkLabel(self, text="", text_color="red")
        self.lbl_error.pack(pady=5)
        
        self.btn_login = ctk.CTkButton(self, text="Đăng Nhập", width=250, height=40, font=ctk.CTkFont(weight="bold"), fg_color="#E67E22", hover_color="#D35400", command=self.handle_login)
        self.btn_login.pack(pady=20)

    def handle_login(self):
        username = self.txt_username.get().strip()
        password = self.txt_password.get().strip()
        
        if not username or not password:
            self.lbl_error.configure(text="Vui lòng nhập đầy đủ thông tin!")
            return
            
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row 
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM tai_khoan WHERE ten_dang_nhap = ? AND mat_khau = ?", (username, hashed_pw))
            user = cursor.fetchone()
            
            if user:
                session.login(dict(user))
                self.destroy() 
                self.on_login_success() 
            else:
                self.lbl_error.configure(text="Sai tên đăng nhập hoặc mật khẩu!")
                
        except Exception as e:
            self.lbl_error.configure(text=f"Lỗi: {e}")
        finally:
            if 'conn' in locals():
                conn.close()