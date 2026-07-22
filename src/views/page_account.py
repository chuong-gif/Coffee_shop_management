import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
from src.config import DB_PATH
from src.utils import session

class PageAccount(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        # Cấu hình grid co giãn tỷ lệ 1:2
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # --- TRÁI: FORM NHẬP LIỆU (Có thanh cuộn để chống tràn UI) ---
        self.form_frame = ctk.CTkScrollableFrame(self, corner_radius=10, fg_color="#1E1E1E")
        self.form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

        # --- PHẢI: BẢNG DỮ LIỆU ---
        self.table_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#1E1E1E")
        self.table_frame.grid(row=0, column=1, sticky="nsew")

        self.setup_form()
        self.setup_table()
        self.load_data()

    def setup_form(self):
        # Tiêu đề
        ctk.CTkLabel(self.form_frame, text="THÔNG TIN TÀI KHOẢN", font=ctk.CTkFont(size=18, weight="bold"), text_color="#E67E22").pack(pady=(15, 20))

        # Nhập liệu cơ bản
        self.txt_username = ctk.CTkEntry(self.form_frame, placeholder_text="Tên đăng nhập", height=35)
        self.txt_username.pack(fill="x", padx=20, pady=10)

        self.txt_name = ctk.CTkEntry(self.form_frame, placeholder_text="Họ và tên nhân viên", height=35)
        self.txt_name.pack(fill="x", padx=20, pady=10)

        self.txt_password = ctk.CTkEntry(self.form_frame, placeholder_text="Mật khẩu (Bỏ trống nếu không đổi)", show="*", height=35)
        self.txt_password.pack(fill="x", padx=20, pady=10)

        # Khung Phân Quyền (Chia 2 cột)
        ctk.CTkLabel(self.form_frame, text="Phân quyền truy cập:", font=ctk.CTkFont(weight="bold", size=14)).pack(anchor="w", padx=20, pady=(20, 10))
        
        perm_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        perm_frame.pack(fill="x", padx=15)
        perm_frame.grid_columnconfigure((0, 1), weight=1) # Chia 2 cột đều nhau

        self.chk_ban_hang = ctk.CTkCheckBox(perm_frame, text="Bàn & Gọi món")
        self.chk_do_uong = ctk.CTkCheckBox(perm_frame, text="Quản lý đồ uống")
        self.chk_kho = ctk.CTkCheckBox(perm_frame, text="Quản lý kho")
        self.chk_thong_ke = ctk.CTkCheckBox(perm_frame, text="Thống kê doanh thu")
        self.chk_lich_su = ctk.CTkCheckBox(perm_frame, text="Lịch sử hóa đơn")
        self.chk_tai_khoan = ctk.CTkCheckBox(perm_frame, text="Quản lý tài khoản")
        self.chk_du_lieu = ctk.CTkCheckBox(perm_frame, text="Quản lý dữ liệu")
        self.chk_ma_giam_gia = ctk.CTkCheckBox(perm_frame, text="Mã giảm giá")

        # Xếp các checkbox vào lưới (Row, Column)
        self.chk_ban_hang.grid(row=0, column=0, pady=8, sticky="w")
        self.chk_do_uong.grid(row=0, column=1, pady=8, sticky="w")
        self.chk_kho.grid(row=1, column=0, pady=8, sticky="w")
        self.chk_thong_ke.grid(row=1, column=1, pady=8, sticky="w")
        self.chk_lich_su.grid(row=2, column=0, pady=8, sticky="w")
        self.chk_tai_khoan.grid(row=2, column=1, pady=8, sticky="w")
        self.chk_du_lieu.grid(row=3, column=0, pady=8, sticky="w")
        self.chk_ma_giam_gia.grid(row=3, column=1, pady=8, sticky="w")

        # Nút Hành động
        btn_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=30)
        btn_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.btn_add = ctk.CTkButton(btn_frame, text="Thêm", height=35, fg_color="#2ECC71", hover_color="#27AE60", command=self.add_account)
        self.btn_add.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.btn_update = ctk.CTkButton(btn_frame, text="Cập nhật", height=35, fg_color="#3498DB", hover_color="#2980B9", command=self.update_account)
        self.btn_update.grid(row=0, column=1, padx=5, sticky="ew")
        
        self.btn_clear = ctk.CTkButton(btn_frame, text="Làm mới", height=35, fg_color="#95A5A6", hover_color="#7F8C8D", command=self.clear_form)
        self.btn_clear.grid(row=0, column=2, padx=5, sticky="ew")

        self.btn_delete = ctk.CTkButton(self.form_frame, text="Xóa tài khoản đã chọn", height=35, fg_color="#E74C3C", hover_color="#C0392B", command=self.delete_account)
        self.btn_delete.pack(fill="x", padx=25, pady=(0, 20))

        self.selected_account_id = None

    def setup_table(self):
        # Header cho bảng
        lbl_table = ctk.CTkLabel(self.table_frame, text="DANH SÁCH NHÂN VIÊN", font=ctk.CTkFont(size=16, weight="bold"), text_color="#AAAAAA")
        lbl_table.pack(anchor="w", padx=20, pady=(15, 10))

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2B2B2B", foreground="white", rowheight=35, fieldbackground="#2B2B2B", borderwidth=0)
        style.map("Treeview", background=[('selected', '#E67E22')])
        style.configure("Treeview.Heading", background="#333333", foreground="white", font=('Arial', 10, 'bold'), borderwidth=1)

        columns = ("id", "username", "name", "roles")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("username", text="Tên đăng nhập")
        self.tree.heading("name", text="Họ và tên")
        self.tree.heading("roles", text="Quyền hạn")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("username", width=120)
        self.tree.column("name", width=180)
        self.tree.column("roles", width=350)

        # Thêm Scrollbar cho bảng
        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y", pady=(0, 15), padx=(0, 10))
        self.tree.pack(fill="both", expand=True, padx=(15, 0), pady=(0, 15))
        
        self.tree.bind("<Double-1>", self.on_row_double_click)

    def load_data(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row # Dùng Row dict để lấy đúng tên cột
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tai_khoan")
            rows = cursor.fetchall()
            
            for row in rows:
                d = dict(row)
                roles = []
                if d['quyen_ban_hang']: roles.append("POS")
                if d['quyen_do_uong']: roles.append("Đồ uống")
                if d['quyen_kho']: roles.append("Kho")
                if d['quyen_thong_ke']: roles.append("Thống kê")
                if d['quyen_lich_su']: roles.append("Lịch sử")
                if d['quyen_tai_khoan']: roles.append("TK")
                if d['quyen_du_lieu']: roles.append("Dữ liệu")
                if d['quyen_ma_giam_gia']: roles.append("Mã giảm giá")
                
                role_text = ", ".join(roles) if roles else "Không có quyền"
                self.tree.insert("", "end", values=(d['id'], d['ten_dang_nhap'], d['ho_ten'], role_text))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu: {e}")
        finally:
            if 'conn' in locals(): conn.close()

    def on_row_double_click(self, event):
        item = self.tree.selection()
        if not item: return
        account_id = self.tree.item(item, "values")[0]
        
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tai_khoan WHERE id=?", (account_id,))
            row = dict(cursor.fetchone())
            
            self.clear_form()
            self.selected_account_id = row['id']
            self.txt_username.insert(0, row['ten_dang_nhap'])
            self.txt_name.insert(0, row['ho_ten'])
            
            if row['quyen_ban_hang']: self.chk_ban_hang.select()
            if row['quyen_do_uong']: self.chk_do_uong.select()
            if row['quyen_kho']: self.chk_kho.select()
            if row['quyen_thong_ke']: self.chk_thong_ke.select()
            if row['quyen_lich_su']: self.chk_lich_su.select()
            if row['quyen_tai_khoan']: self.chk_tai_khoan.select()
            if row['quyen_du_lieu']: self.chk_du_lieu.select()
            if row['quyen_ma_giam_gia']: self.chk_ma_giam_gia.select()
            
            self.txt_username.configure(state="disabled") 
        except Exception as e:
            pass
        finally:
            if 'conn' in locals(): conn.close()

    def get_checkbox_values(self):
        return (
            self.chk_ban_hang.get(), self.chk_do_uong.get(), self.chk_kho.get(),
            self.chk_thong_ke.get(), self.chk_lich_su.get(), self.chk_tai_khoan.get(),
            self.chk_du_lieu.get(), self.chk_ma_giam_gia.get()
        )

    def add_account(self):
        username = self.txt_username.get().strip()
        name = self.txt_name.get().strip()
        password = self.txt_password.get().strip()
        
        if not username or not name or not password:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đủ thông tin!")
            return
            
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        perms = self.get_checkbox_values()
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO tai_khoan 
                              (ten_dang_nhap, mat_khau, ho_ten, quyen_ban_hang, quyen_do_uong, quyen_kho, 
                               quyen_thong_ke, quyen_lich_su, quyen_tai_khoan, quyen_du_lieu, quyen_ma_giam_gia) 
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (username, hashed_pw, name, *perms))
            conn.commit()
            self.clear_form(); self.load_data()
            messagebox.showinfo("Thành công", "Thêm tài khoản thành công!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Lỗi", "Tên đăng nhập đã tồn tại!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi hệ thống: {e}")
        finally:
            if 'conn' in locals(): conn.close()

    def update_account(self):
        if not self.selected_account_id: return
        
        name = self.txt_name.get().strip()
        password = self.txt_password.get().strip()
        perms = self.get_checkbox_values()
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            if password:
                hashed_pw = hashlib.sha256(password.encode()).hexdigest()
                cursor.execute('''UPDATE tai_khoan SET ho_ten=?, mat_khau=?, quyen_ban_hang=?, quyen_do_uong=?, 
                                  quyen_kho=?, quyen_thong_ke=?, quyen_lich_su=?, quyen_tai_khoan=?, quyen_du_lieu=?, quyen_ma_giam_gia=? WHERE id=?''',
                               (name, hashed_pw, *perms, self.selected_account_id))
            else:
                cursor.execute('''UPDATE tai_khoan SET ho_ten=?, quyen_ban_hang=?, quyen_do_uong=?, 
                                  quyen_kho=?, quyen_thong_ke=?, quyen_lich_su=?, quyen_tai_khoan=?, quyen_du_lieu=?, quyen_ma_giam_gia=? WHERE id=?''',
                               (name, *perms, self.selected_account_id))
            conn.commit()
            self.clear_form(); self.load_data()
            messagebox.showinfo("Thành công", "Cập nhật thành công!")
            
            if self.selected_account_id == session.current_user['id']:
                messagebox.showinfo("Thông báo", "Vui lòng đăng xuất và đăng nhập lại để áp dụng quyền mới.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi hệ thống: {e}")
        finally:
            if 'conn' in locals(): conn.close()

    # FIX LỖI XÓA TẠI ĐÂY: Lấy thẳng ID từ Treeview đang chọn
    def delete_account(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Cảnh báo", "Vui lòng click chọn 1 dòng tài khoản bên bảng để xóa!")
            return
            
        account_id = int(self.tree.item(selected_items[0], "values")[0])
        
        if account_id == session.current_user['id']:
            messagebox.showerror("Lỗi", "Bạn không thể tự xóa tài khoản đang đăng nhập!")
            return
            
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa tài khoản này?"):
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tai_khoan WHERE id=?", (account_id,))
                conn.commit()
                self.clear_form(); self.load_data()
                messagebox.showinfo("Thành công", "Đã xóa tài khoản.")
            finally:
                if 'conn' in locals(): conn.close()

    def clear_form(self):
        self.selected_account_id = None
        self.txt_username.configure(state="normal")
        self.txt_username.delete(0, 'end')
        self.txt_name.delete(0, 'end')
        self.txt_password.delete(0, 'end')
        self.chk_ban_hang.deselect(); self.chk_do_uong.deselect(); self.chk_kho.deselect()
        self.chk_thong_ke.deselect(); self.chk_lich_su.deselect(); self.chk_tai_khoan.deselect()
        self.chk_du_lieu.deselect(); self.chk_ma_giam_gia.deselect()