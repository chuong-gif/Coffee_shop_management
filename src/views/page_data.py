import customtkinter as ctk
import tkinter.messagebox as messagebox
from tkinter import filedialog
import datetime
import os
from src.controllers.backup_controller import BackupController

class PageData(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="#121212")

        self.controller = BackupController()

        # Bảng màu Dark Theme
        self.card_bg = "#212121"
        self.border_color = "#333333"
        self.text_main = "white"
        self.text_sub = "#AAAAAA"
        self.color_accent = "#E67E22"

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) 
        self.grid_rowconfigure(1, weight=0) 
        self.grid_rowconfigure(2, weight=1) 

        self.build_ui()
        self.load_config()
        self.load_real_logs()

    def build_ui(self):
        # ==========================================
        # 1. HEADER TIÊU ĐỀ
        # ==========================================
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(self.header_frame, text="HỆ THỐNG QUẢN TRỊ & AN TOÀN DỮ LIỆU", font=ctk.CTkFont(size=20, weight="bold"), text_color=self.text_main).pack(anchor="w")
        ctk.CTkLabel(self.header_frame, text="Tự động sao lưu, nén dữ liệu an toàn và lưu trữ 7 bản sao gần nhất.", text_color=self.text_sub, font=ctk.CTkFont(size=12)).pack(anchor="w")
        
        ctk.CTkFrame(self, height=1, fg_color=self.border_color).grid(row=0, column=0, sticky="ew", padx=20, pady=(55, 0))

        # ==========================================
        # 2. VÙNG ĐỒNG BỘ HÓA 1 CHẠM (EXPORT / IMPORT)
        # ==========================================
        self.sync_card = ctk.CTkFrame(self, fg_color=self.card_bg, corner_radius=8, border_width=1, border_color=self.border_color)
        self.sync_card.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        self.sync_card.grid_columnconfigure((0, 1), weight=1)

        # Khung bên trái: Xuất
        export_zone = ctk.CTkFrame(self.sync_card, fg_color="transparent")
        export_zone.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        ctk.CTkLabel(export_zone, text="📦 ĐÓNG GÓI DỮ LIỆU (EXPORT)", font=ctk.CTkFont(size=14, weight="bold"), text_color=self.text_main).pack(anchor="w")
        ctk.CTkLabel(export_zone, text="Nén toàn bộ cấu hình quán, thực đơn, hình ảnh món và hóa đơn\nthành một file an toàn mã hóa mã băm để mang sang máy khác.", text_color=self.text_sub, font=ctk.CTkFont(size=11), justify="left").pack(anchor="w", pady=5)
        
        ctk.CTkButton(export_zone, text="Xuất File Đồng Bộ 1 Chạm (.coffee)", fg_color=self.color_accent, hover_color="#D35400", font=ctk.CTkFont(weight="bold"), height=40, command=self.ui_export_action).pack(fill="x", pady=(10, 0))

        ctk.CTkFrame(self.sync_card, width=1, fg_color=self.border_color).grid(row=0, column=0, sticky="nse", padx=(0,0), pady=15)

        # Khung bên phải: Nhập
        import_zone = ctk.CTkFrame(self.sync_card, fg_color="transparent")
        import_zone.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        ctk.CTkLabel(import_zone, text="📥 NẠP DỮ LIỆU ĐỒNG BỘ (IMPORT)", font=ctk.CTkFont(size=14, weight="bold"), text_color=self.text_main).pack(anchor="w")
        ctk.CTkLabel(import_zone, text="Giải nén chứng từ từ thiết bị khác nạp vào hệ thống hiện tại.\nPhần mềm tự động phát hiện mã độc bằng cơ chế băm SHA-256.", text_color=self.text_sub, font=ctk.CTkFont(size=11), justify="left").pack(anchor="w", pady=5)
        
        ctk.CTkButton(import_zone, text="Chọn File Dữ Liệu Nạp Vào Hệ Thống", fg_color="#2980B9", hover_color="#1F618D", font=ctk.CTkFont(weight="bold"), height=40, command=self.ui_import_action).pack(fill="x", pady=(10, 0))

        # ==========================================
        # 3. KHU VỰC THIẾT LẬP TỰ ĐỘNG & NHẬT KÝ
        # ==========================================
        self.bottom_grid = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_grid.grid(row=2, column=0, sticky="nsew", padx=20, pady=(5, 20))
        self.bottom_grid.grid_columnconfigure(0, weight=4) 
        self.bottom_grid.grid_columnconfigure(1, weight=6) 
        self.bottom_grid.grid_rowconfigure(0, weight=1)

        # --- KHUNG TRÁI: CẤU HÌNH SAO LƯU TỰ ĐỘNG ---
        config_card = ctk.CTkFrame(self.bottom_grid, fg_color=self.card_bg, corner_radius=8, border_width=1, border_color=self.border_color)
        config_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(config_card, text="⚙️ CẤU HÌNH SAO LƯU TỰ ĐỘNG", font=ctk.CTkFont(size=13, weight="bold"), text_color=self.text_main).pack(anchor="w", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(config_card, text="THƯ MỤC GỐC LƯU TRỮ:", font=ctk.CTkFont(size=11, weight="bold"), text_color=self.text_sub).pack(anchor="w", padx=20, pady=(5, 2))
        path_frame = ctk.CTkFrame(config_card, fg_color="transparent")
        path_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.entry_path = ctk.CTkEntry(path_frame, fg_color="#121212", border_color=self.border_color, text_color=self.text_main)
        self.entry_path.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(path_frame, text="Thay đổi", width=60, fg_color="#333333", text_color="white", hover_color="#555555", command=self.ui_browse_folder).pack(side="right")

        ctk.CTkLabel(config_card, text="CHU KỲ TỰ ĐỘNG CHẠY NGẦM:", font=ctk.CTkFont(size=11, weight="bold"), text_color=self.text_sub).pack(anchor="w", padx=20, pady=(5, 2))
        
        interval_frame = ctk.CTkFrame(config_card, fg_color="transparent")
        interval_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(interval_frame, text="Sao lưu sau mỗi:", text_color=self.text_main).pack(side="left", padx=(0, 10))
        
        self.var_interval_num = ctk.StringVar(value="1")
        self.entry_interval = ctk.CTkEntry(interval_frame, textvariable=self.var_interval_num, width=50, justify="center", fg_color="#121212", border_color=self.border_color)
        self.entry_interval.pack(side="left", padx=(0, 5))
        
        self.cb_unit = ctk.CTkComboBox(interval_frame, values=["Giây", "Phút", "Giờ"], width=80, fg_color="#121212", border_color=self.border_color, command=self.save_config)
        self.cb_unit.pack(side="left", padx=(0, 10))

        self.switch_auto_var = ctk.BooleanVar(value=True)
        self.switch_auto = ctk.CTkSwitch(config_card, text="Kích hoạt tự động sao lưu", variable=self.switch_auto_var, progress_color="#196F3D", button_color="#2ECC71", command=self.save_config)
        self.switch_auto.pack(anchor="w", padx=20, pady=5)
        
        self.entry_interval.bind("<FocusOut>", self.save_config)

        ctk.CTkButton(config_card, text="Chạy Lưu Trữ Ngay Bấy Giờ", fg_color="transparent", border_width=1, border_color="#2ECC71", text_color="#2ECC71", hover_color="#196F3D", command=self.ui_run_auto_backup).pack(fill="x", padx=20, pady=(15, 10))

        # [FIX]: Loại bỏ ép side="bottom" để khung cảnh báo tự co dãn vừa vặn chữ
        info_alert = ctk.CTkFrame(
            config_card,
            fg_color="#3E2723",
            border_width=1,
            border_color=self.color_accent,
            corner_radius=6
        )
        info_alert.pack(fill="x", padx=20, pady=(15, 20))

        alert_text = (
            "🛡 BẢO VỆ TOÀN VẸN:\n"
            "File Export (.coffee) được gán mã băm bảo mật SHA-256.\n"
            "Mọi hành vi dùng phần mềm ngoài can thiệp Data sẽ bị App phát hiện và từ chối Import lập tức."
        )

        ctk.CTkLabel(
            info_alert,
            text=alert_text,
            text_color=self.color_accent,
            font=ctk.CTkFont(size=11),
            justify="center",
            wraplength=700
        ).pack(
            padx=10,
            pady=4,
            fill="x"
        )

        # --- KHUNG PHẢI: NHẬT KÝ HỆ THỐNG ---
        log_card = ctk.CTkFrame(self.bottom_grid, fg_color=self.card_bg, corner_radius=8, border_width=1, border_color=self.border_color)
        log_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        ctk.CTkLabel(log_card, text="📋 NHẬT KÝ BIẾN ĐỘNG DỮ LIỆU HỆ THỐNG", font=ctk.CTkFont(size=13, weight="bold"), text_color=self.text_main).pack(anchor="w", padx=20, pady=(20, 10))

        self.log_header = ctk.CTkFrame(log_card, fg_color="transparent")
        self.log_header.pack(fill="x", padx=(20, 36), pady=(5, 2))
        self.log_header.grid_columnconfigure(0, weight=2)
        self.log_header.grid_columnconfigure(1, weight=2)
        self.log_header.grid_columnconfigure(2, weight=5)

        ctk.CTkLabel(self.log_header, text="THỜI GIAN", text_color=self.text_sub, font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(self.log_header, text="HÀNH ĐỘNG", text_color=self.text_sub, font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(self.log_header, text="CHI TIẾT LOG", text_color=self.text_sub, font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=2, sticky="w")

        ctk.CTkFrame(log_card, height=1, fg_color=self.border_color).pack(fill="x", padx=15)

        self.log_scroll = ctk.CTkScrollableFrame(log_card, fg_color="transparent")
        self.log_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.log_scroll.grid_columnconfigure(0, weight=2)
        self.log_scroll.grid_columnconfigure(1, weight=2)
        self.log_scroll.grid_columnconfigure(2, weight=5)

    # ==========================================
    # LOGIC XỬ LÝ SỰ KIỆN
    # ==========================================
    def load_config(self):
        config = self.controller.load_auto_backup_config()
        self.entry_path.delete(0, "end")
        self.entry_path.insert(0, config.get("path", ""))
        self.switch_auto_var.set(config.get("enabled", True))
        self.var_interval_num.set(str(config.get("interval_num", 1)))
        self.cb_unit.set(config.get("interval_unit", "Giờ"))

    def save_config(self, *args):
        try:
            num = int(self.var_interval_num.get())
        except:
            num = 1
        self.controller.save_auto_backup_config(
            self.entry_path.get(), 
            self.switch_auto_var.get(),
            num,
            self.cb_unit.get()
        )

    def ui_browse_folder(self):
        folder = filedialog.askdirectory(parent=self.winfo_toplevel())
        if folder:
            self.entry_path.delete(0, "end")
            self.entry_path.insert(0, os.path.abspath(folder))
            self.save_config()

    def load_real_logs(self):
        for widget in self.log_scroll.winfo_children(): widget.destroy()
        
        logs = self.controller.get_system_logs(limit=30)
        if not logs:
            ctk.CTkLabel(self.log_scroll, text="Chưa có bản ghi nhật ký nào.", text_color=self.text_sub).grid(row=0, column=0, columnspan=3, pady=20)
            return

        for idx, log in enumerate(logs):
            time_str, action, detail = log
            r = idx * 2
            
            ctk.CTkLabel(self.log_scroll, text=time_str, text_color=self.text_sub, font=ctk.CTkFont(size=12)).grid(row=r, column=0, sticky="w", pady=6)
            
            if "EXPORT" in action: color_act = self.color_accent
            elif "IMPORT" in action: color_act = "#3498DB"
            elif "ALERT" in action or "LỖI" in action: color_act = "#E74C3C"
            else: color_act = "#2ECC71"
                
            ctk.CTkLabel(self.log_scroll, text=action, text_color=color_act, font=ctk.CTkFont(size=11, weight="bold")).grid(row=r, column=1, sticky="w", pady=6)
            ctk.CTkLabel(self.log_scroll, text=detail, text_color=self.text_main, font=ctk.CTkFont(size=12), anchor="w", wraplength=350, justify="left").grid(row=r, column=2, sticky="w", pady=6)
            ctk.CTkFrame(self.log_scroll, height=1, fg_color="#2A2A2A").grid(row=r+1, column=0, columnspan=3, sticky="ew")

    def ui_run_auto_backup(self):
        success, msg = self.controller.trigger_auto_backup()
        if success:
            messagebox.showinfo("Sao lưu cục bộ", f"Thành công!\n\nĐã lưu tại:\n{msg}", parent=self.winfo_toplevel())
        else:
            messagebox.showwarning("Thông báo", msg, parent=self.winfo_toplevel())
        self.load_real_logs()

    def ui_export_action(self):
        save_path = filedialog.asksaveasfilename(
            parent=self.winfo_toplevel(),
            defaultextension=".coffee", 
            filetypes=[("Gói Dữ Liệu Quán Cà Phê", "*.coffee")], 
            initialfile=f"Data_Sync_{datetime.datetime.now().strftime('%Y%m%d')}.coffee"
        )
        if save_path:
            try:
                self.controller.export_1_touch(save_path)
                messagebox.showinfo("Đóng gói thành công", f"Hệ thống đã mã hóa bảo mật toàn vẹn thành công!\n\nToàn bộ Master Data và Dữ liệu giao dịch đã lưu tại:\n{os.path.basename(save_path)}", parent=self.winfo_toplevel())
            except Exception as e:
                messagebox.showerror("Lỗi Export", f"Đã xảy ra lỗi trong quá trình đóng gói:\n{str(e)}", parent=self.winfo_toplevel())
            self.load_real_logs()

    def ui_import_action(self):
        file_path = filedialog.askopenfilename(
            parent=self.winfo_toplevel(),
            filetypes=[("Gói Dữ Liệu Quán Cà Phê", "*.coffee")]
        )
        if file_path:
            confirm = messagebox.askyesno("Cảnh báo Ghi Đè", "QUAN TRỌNG: Quá trình nạp dữ liệu (.coffee) sẽ GHI ĐÈ toàn bộ Menu, Kho, và các Hóa đơn hiện tại.\n\nAnh có chắc chắn muốn thực hiện thao tác NẠP DỮ LIỆU không?", parent=self.winfo_toplevel())
            if not confirm:
                return

            try:
                self.controller.import_1_touch(file_path)
                messagebox.showinfo("Đồng bộ hoàn tất", "Hệ thống đã nạp và hợp nhất dữ liệu thành công! Chuỗi Hash SHA-256 hoàn toàn trùng khớp.\n\nVui lòng Khởi Động Lại phần mềm để áp dụng dữ liệu mới.", parent=self.winfo_toplevel())
            except PermissionError as pe:
                messagebox.showerror("TỪ CHỐI TRUY CẬP (SECURITY ALERT)", str(pe), parent=self.winfo_toplevel())
            except Exception as e:
                messagebox.showerror("Lỗi Import", f"Dữ liệu không hợp lệ hoặc đã bị lỗi:\n{str(e)}", parent=self.winfo_toplevel())
            
            self.load_real_logs()