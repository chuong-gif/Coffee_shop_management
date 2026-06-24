import customtkinter as ctk
import tkinter.messagebox as messagebox
from src.controllers.backup_controller import BackupController

class PageData(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.controller = BackupController()

        self.title = ctk.CTkLabel(self, text="SAO LƯU & PHỤC HỒI DỮ LIỆU", font=ctk.CTkFont(size=20, weight="bold"))
        self.title.pack(pady=(10, 10))

        self.description = ctk.CTkLabel(
            self,
            text="Nhấn nút sao lưu để tạo file backup cục bộ hoặc tải lên Google Drive.",
            wraplength=760,
            anchor="w",
        )
        self.description.pack(fill="x", padx=20, pady=(0, 10))

        self.btn_local_backup = ctk.CTkButton(self, text="Sao lưu cục bộ", command=self.ui_local_backup)
        self.btn_local_backup.pack(padx=20, pady=(0, 10), fill="x")

        self.btn_drive_backup = ctk.CTkButton(self, text="Sao lưu lên Google Drive", command=self.ui_drive_backup)
        self.btn_drive_backup.pack(padx=20, pady=(0, 10), fill="x")

        self.lbl_status = ctk.CTkLabel(self, text="Trạng thái: Chưa thực hiện sao lưu.", anchor="w")
        self.lbl_status.pack(fill="x", padx=20, pady=(10, 0))

    def ui_local_backup(self):
        try:
            backup_path = self.controller.create_local_backup()
            self.lbl_status.configure(text=f"Đã tạo backup tại: {backup_path}")
            messagebox.showinfo("Sao lưu thành công", f"Backup cục bộ đã tạo: {backup_path}")
        except Exception as ex:
            messagebox.showerror("Lỗi sao lưu", str(ex))

    def ui_drive_backup(self):
        try:
            uploaded = self.controller.backup_to_google_drive()
            self.lbl_status.configure(text=f"Đã sao lưu lên Drive: {uploaded.get('name')}")
            messagebox.showinfo("Sao lưu Drive", f"Backup đã được tải lên Drive: {uploaded.get('name')}")
        except Exception as ex:
            messagebox.showerror("Lỗi sao lưu Drive", str(ex))
