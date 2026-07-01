import os
import customtkinter as ctk
import tkinter.messagebox as messagebox
from tkinter import filedialog
from PIL import Image
from src.controllers.menu_controller import MenuController

class PageMenu(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="#121212") 
        self.controller = MenuController()

        self.bg_color = "#121212"
        self.card_color = "#212121"
        self.border_color = "#333333"
        self.text_main = "white"
        self.text_sub = "#AAAAAA"
        self.color_accent = "#E67E22"

        # ==========================================
        # 1. HEADER & BỘ LỌC
        # ==========================================
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=(20, 10))

        title_group = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        title_group.pack(side="left")
        ctk.CTkLabel(title_group, text="QUẢN LÝ THỰC ĐƠN ĐỒ UỐNG", font=ctk.CTkFont(size=20, weight="bold"), text_color=self.text_main).pack(anchor="w")
        ctk.CTkLabel(title_group, text="Quản lý giá cả, danh mục sản phẩm và trạng thái kho.", text_color=self.text_sub, font=ctk.CTkFont(size=12)).pack(anchor="w")

        btn_group = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        btn_group.pack(side="right", pady=10)

        # [TÍNH NĂNG MỚI]: Bộ lọc danh mục
        ctk.CTkLabel(btn_group, text="Lọc theo:", font=ctk.CTkFont(size=12), text_color=self.text_sub).pack(side="left", padx=5)
        self.filter_var = ctk.StringVar(value="Tất cả")
        self.cb_filter = ctk.CTkComboBox(btn_group, variable=self.filter_var, values=["Tất cả"], fg_color=self.card_color, border_color=self.border_color, text_color=self.text_main, command=self.on_filter_change)
        self.cb_filter.pack(side="left", padx=(0, 15))

        ctk.CTkButton(btn_group, text="📁 Thiết lập danh mục", fg_color="transparent", border_width=1, border_color=self.color_accent, text_color=self.color_accent, hover_color="#3E2723", command=self.ui_category_popup).pack(side="left", padx=10)
        ctk.CTkButton(btn_group, text="+ Thêm đồ uống mới", fg_color=self.color_accent, hover_color="#D35400", text_color="white", font=ctk.CTkFont(weight="bold"), command=lambda: self.ui_drink_popup()).pack(side="left")

        ctk.CTkFrame(self, height=1, fg_color=self.border_color).pack(fill="x", padx=20, pady=5)

        # ==========================================
        # 2. KHU VỰC DỮ LIỆU CỐ ĐỊNH TIÊU ĐỀ (STICKY HEADER)
        # ==========================================
        self.list_container = ctk.CTkFrame(self, fg_color=self.card_color, corner_radius=8, border_width=1, border_color=self.border_color)
        self.list_container.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        # Khung Tiêu Đề Cố Định (Nằm ngoài Scroll)
        self.sticky_header = ctk.CTkFrame(self.list_container, fg_color="transparent")
        # Padding phải 26px để bù trừ cho khoảng trống thanh cuộn (Scrollbar) ở bên dưới
        self.sticky_header.pack(fill="x", padx=(10, 26), pady=(10, 5))
        
        self.sticky_header.grid_columnconfigure(0, weight=1) 
        self.sticky_header.grid_columnconfigure(1, weight=4) 
        self.sticky_header.grid_columnconfigure(2, weight=2) 
        self.sticky_header.grid_columnconfigure(3, weight=4) 
        self.sticky_header.grid_columnconfigure(4, weight=2) 
        self.sticky_header.grid_columnconfigure(5, weight=2) 

        headers = ["MÃ MÓN", "CHI TIẾT ĐỒ UỐNG", "GIÁ BÁN ĐỀ XUẤT", "ĐỊNH LƯỢNG TIÊU HAO KHO", "TRẠNG THÁI TẠI QUẦY", "HÀNH ĐỘNG"]
        for col_idx, col_name in enumerate(headers):
            ctk.CTkLabel(self.sticky_header, text=col_name, anchor="w", font=ctk.CTkFont(size=12, weight="bold"), text_color=self.text_sub).grid(row=0, column=col_idx, sticky="w", padx=10)

        ctk.CTkFrame(self.list_container, height=1, fg_color="#333333").pack(fill="x", padx=10)

        # Khung Cuộn Danh Sách
        self.list_scroll = ctk.CTkScrollableFrame(self.list_container, fg_color="transparent")
        self.list_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Grid của Scroll phải Y HỆT Sticky Header để không bị lệch chéo
        self.list_scroll.grid_columnconfigure(0, weight=1) 
        self.list_scroll.grid_columnconfigure(1, weight=4) 
        self.list_scroll.grid_columnconfigure(2, weight=2) 
        self.list_scroll.grid_columnconfigure(3, weight=4) 
        self.list_scroll.grid_columnconfigure(4, weight=2) 
        self.list_scroll.grid_columnconfigure(5, weight=2) 

        self.refresh_menu_list()

    # ==========================================
    # CÁC HÀM RENDER GIAO DIỆN
    # ==========================================
    def get_image(self, path, size=(45, 45)):
        if path and os.path.exists(path):
            try: return ctk.CTkImage(light_image=Image.open(path), size=size)
            except Exception: pass
        return None

    def on_filter_change(self, choice):
        self.refresh_menu_list()

    def refresh_menu_list(self):
        # 1. Cập nhật lại danh sách danh mục cho Combobox Bộ Lọc
        all_cats = self.controller.get_categories()
        current_val = self.filter_var.get()
        self.cb_filter.configure(values=["Tất cả"] + all_cats)
        if current_val not in ["Tất cả"] + all_cats:
            self.filter_var.set("Tất cả")
            current_val = "Tất cả"

        self.ingredient_data = self.controller.get_ingredients()
        self.ing_map = {ing[0]: {"name": ing[1], "unit": ing[2]} for ing in self.ingredient_data}

        # 2. Xóa lưới cũ
        for widget in self.list_scroll.winfo_children():
            widget.destroy()

        # 3. Lọc dữ liệu
        all_drinks = self.controller.get_menu()
        if current_val != "Tất cả":
            drinks = [d for d in all_drinks if d[3] == current_val]
        else:
            drinks = all_drinks

        if not drinks:
            ctk.CTkLabel(self.list_scroll, text="Chưa có đồ uống nào phù hợp.", text_color=self.text_sub).grid(row=0, column=0, columnspan=6, pady=40)
            return

        for i, item in enumerate(drinks):
            d_id, d_code, d_name, d_cat, d_price, d_status, d_image = item
            r = i * 2 # Tính dòng cho dữ liệu

            # 1. Mã món
            ctk.CTkLabel(self.list_scroll, text=d_code, anchor="w", text_color=self.text_sub, font=ctk.CTkFont(family="Courier")).grid(row=r, column=0, sticky="w", padx=10, pady=10)

            # 2. Chi tiết
            detail_frame = ctk.CTkFrame(self.list_scroll, fg_color="transparent")
            detail_frame.grid(row=r, column=1, sticky="w", padx=10, pady=5)

            img_obj = self.get_image(d_image)
            if img_obj:
                ctk.CTkLabel(detail_frame, image=img_obj, text="").pack(side="left", padx=(0, 15))
            else:
                bg_color = f"#{abs(hash(d_cat or 'Khác')) % 0xFFFFFF:06x}"
                img_lbl = ctk.CTkFrame(detail_frame, width=45, height=45, corner_radius=8, fg_color=bg_color)
                img_lbl.pack(side="left", padx=(0, 15))
                img_lbl.pack_propagate(False) 
                ctk.CTkLabel(img_lbl, text=d_name[:2].upper(), text_color="white", font=ctk.CTkFont(weight="bold")).pack(expand=True)

            text_col = ctk.CTkFrame(detail_frame, fg_color="transparent")
            text_col.pack(side="left")
            ctk.CTkLabel(text_col, text=d_name, anchor="w", text_color=self.text_main, font=ctk.CTkFont(weight="bold", size=14)).pack(anchor="w")
            
            cat_pill = ctk.CTkFrame(text_col, corner_radius=4, fg_color="#333333", height=20)
            cat_pill.pack(anchor="w", pady=(4, 0))
            ctk.CTkLabel(cat_pill, text=d_cat or "Khác", text_color=self.text_main, font=ctk.CTkFont(size=11)).pack(padx=6)

            # 3. Giá bán
            ctk.CTkLabel(self.list_scroll, text=f"{d_price:,.0f} đ".replace(",", "."), anchor="w", font=ctk.CTkFont(weight="bold"), text_color=self.color_accent).grid(row=r, column=2, sticky="w", padx=10)

            # 4. Định lượng
            recipe_frame = ctk.CTkFrame(self.list_scroll, fg_color="transparent")
            recipe_frame.grid(row=r, column=3, sticky="w", padx=10)
            recipe = self.controller.get_recipe(d_id)
            if recipe:
                for ing_id, qty in recipe.items():
                    if ing_id in self.ing_map:
                        ing_name = self.ing_map[ing_id]['name']
                        ing_unit = self.ing_map[ing_id]['unit']
                        pill = ctk.CTkFrame(recipe_frame, corner_radius=4, fg_color="#3E2723", border_width=1, border_color=self.color_accent)
                        pill.pack(anchor="w", pady=2)
                        ctk.CTkLabel(pill, text=f"{ing_name}: {qty:g} {ing_unit}", font=ctk.CTkFont(size=11), text_color=self.color_accent).pack(padx=8, pady=2)
            else:
                ctk.CTkLabel(recipe_frame, text="-- Không cấu hình --", text_color=self.text_sub, font=ctk.CTkFont(size=11)).pack(anchor="w")

            # 5. Trạng thái
            status_frame = ctk.CTkFrame(self.list_scroll, fg_color="transparent")
            status_frame.grid(row=r, column=4, sticky="w", padx=10)
            
            lbl_status = ctk.CTkLabel(status_frame, text="● CÒN HÀNG" if d_status == 1 else "○ HẾT HÀNG", 
                                      text_color="#2ECC71" if d_status == 1 else self.text_sub, font=ctk.CTkFont(size=11, weight="bold"))
            lbl_status.pack(side="left", padx=(0, 5))

            switch_var = ctk.StringVar(value="on" if d_status == 1 else "off")
            ctk.CTkSwitch(status_frame, text="", variable=switch_var, onvalue="on", offvalue="off", width=40,
                          button_color="#2ECC71" if d_status == 1 else "#E74C3C", progress_color="#196F3D",
                          command=lambda id=d_id, curr=d_status: self.controller.toggle_item_status(id, curr) or self.refresh_menu_list()).pack(side="left")

            # 6. Hành động
            action_frame = ctk.CTkFrame(self.list_scroll, fg_color="transparent")
            action_frame.grid(row=r, column=5, sticky="w", padx=10)
            ctk.CTkButton(action_frame, text="Sửa", width=40, fg_color="#333333", text_color="white", hover_color="#555555", command=lambda id=d_id: self.ui_drink_popup(id)).pack(side="left", padx=2)
            ctk.CTkButton(action_frame, text="Xóa", width=40, fg_color="transparent", border_width=1, border_color="#E74C3C", text_color="#E74C3C", hover_color="#641E16", command=lambda id=d_id: self.ui_delete_drink(id)).pack(side="left", padx=2)

            ctk.CTkFrame(self.list_scroll, height=1, fg_color=self.border_color).grid(row=r+1, column=0, columnspan=6, sticky="ew", pady=5)

    # ==========================================
    # CÁC POPUP TƯƠNG TÁC
    # ==========================================
    def ui_category_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Thiết lập Danh Mục")
        popup.geometry("400x550") 
        popup.attributes("-topmost", True)
        popup.configure(fg_color=self.bg_color)

        ctk.CTkLabel(popup, text="✨ THIẾT LẬP DANH MỤC THỰC ĐƠN", font=ctk.CTkFont(size=16, weight="bold"), text_color=self.text_main).pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(popup, text="Phân loại các nhóm đồ uống giúp nhân viên dễ thao tác.", text_color=self.text_sub, justify="left").pack(anchor="w", padx=20, pady=(0, 15))

        btn_finish = ctk.CTkButton(popup, text="Hoàn tất thiết lập danh mục", fg_color="#2C3E50", hover_color="#1A252F", text_color="white", command=lambda: [popup.destroy(), self.refresh_menu_list()])
        btn_finish.pack(side="bottom", fill="x", padx=20, pady=20)

        ctk.CTkLabel(popup, text="THÊM DANH MỤC MỚI:", font=ctk.CTkFont(size=11, weight="bold"), text_color=self.text_sub).pack(anchor="w", padx=20)
        add_frame = ctk.CTkFrame(popup, fg_color="transparent")
        add_frame.pack(fill="x", padx=20, pady=(5, 15))
        
        e_new = ctk.CTkEntry(add_frame, placeholder_text="e.g. Trà Hoa Quả...", fg_color=self.card_color, border_color=self.border_color, text_color=self.text_main)
        e_new.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        def add_cat():
            if e_new.get().strip():
                self.controller.add_category(e_new.get().strip())
                refresh_cat_list()
                e_new.delete(0, 'end')
                
        ctk.CTkButton(add_frame, text="Thêm", width=80, fg_color=self.color_accent, hover_color="#D35400", command=add_cat).pack(side="right")

        ctk.CTkLabel(popup, text="DANH MỤC THỰC ĐƠN HIỆN CÓ:", font=ctk.CTkFont(size=11, weight="bold"), text_color=self.text_sub).pack(anchor="w", padx=20)
        cat_list = ctk.CTkScrollableFrame(popup, fg_color="transparent")
        cat_list.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        def delete_cat(cat_name):
            if messagebox.askyesno("Xóa", f"Xóa danh mục '{cat_name}'? Các món thuộc danh mục này sẽ chuyển về 'Khác'.", parent=popup):
                self.controller.delete_category(cat_name)
                refresh_cat_list()
                self.refresh_menu_list()

        def refresh_cat_list():
            for w in cat_list.winfo_children(): w.destroy()
            for cat in self.controller.get_categories():
                row = ctk.CTkFrame(cat_list, fg_color=self.card_color, border_width=1, border_color=self.border_color, corner_radius=8, height=40)
                row.pack(fill="x", pady=4, padx=10)
                row.pack_propagate(False)
                ctk.CTkLabel(row, text=cat, font=ctk.CTkFont(weight="bold"), text_color=self.text_main).pack(side="left", padx=15)
                ctk.CTkButton(row, text="🗑", width=30, fg_color="transparent", text_color=self.text_sub, hover_color="#641E16", command=lambda c=cat: delete_cat(c)).pack(side="right", padx=10)

        refresh_cat_list()

    def ui_drink_popup(self, drink_id=None):
        popup = ctk.CTkToplevel(self)
        popup.title("Thêm/Sửa Đồ Uống")
        popup.geometry("550x780")
        popup.attributes("-topmost", True)
        popup.configure(fg_color=self.bg_color)

        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(side="bottom", fill="x", padx=20, pady=20)
        
        scroll = ctk.CTkScrollableFrame(popup, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=(20, 0))

        title_text = "THÊM ĐỒ UỐNG MỚI VÀO THỰC ĐƠN" if not drink_id else "CHỈNH SỬA ĐỒ UỐNG"
        ctk.CTkLabel(scroll, text=title_text, font=ctk.CTkFont(size=16, weight="bold"), text_color=self.text_main).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(scroll, text="Nhập thông tin đồ uống mới để xuất ngay trên sơ đồ thanh toán.", text_color=self.text_sub).pack(anchor="w", pady=(0, 20))

        # 1. Tên món
        ctk.CTkLabel(scroll, text="TÊN MÓN NƯỚC UỐNG:", font=ctk.CTkFont(size=11, weight="bold"), text_color=self.text_sub).pack(anchor="w")
        e_name = ctk.CTkEntry(scroll, placeholder_text="e.g. Cà Phê Cốt Dừa", height=35, fg_color=self.bg_color, border_color=self.border_color, text_color=self.text_main)
        e_name.pack(fill="x", pady=(5, 15))

        # 2. Giá & Danh mục
        row2 = ctk.CTkFrame(scroll, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 15))
        
        col1 = ctk.CTkFrame(row2, fg_color="transparent")
        col1.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(col1, text="ĐƠN GIÁ BÁN (VND):", font=ctk.CTkFont(size=11, weight="bold"), text_color=self.text_sub).pack(anchor="w")
        e_price = ctk.CTkEntry(col1, placeholder_text="e.g. 35000", height=35, fg_color=self.bg_color, border_color=self.border_color, text_color=self.text_main)
        e_price.pack(fill="x", pady=(5, 0))

        col2 = ctk.CTkFrame(row2, fg_color="transparent")
        col2.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(col2, text="NHÓM DANH MỤC:", font=ctk.CTkFont(size=11, weight="bold"), text_color=self.text_sub).pack(anchor="w")
        cb_cat = ctk.CTkComboBox(col2, values=self.controller.get_categories() or ["Khác"], height=35, fg_color=self.card_color, border_color=self.border_color, text_color=self.text_main)
        cb_cat.pack(fill="x", pady=(5, 0))

        # 3. Hình ảnh
        img_card = ctk.CTkFrame(scroll, fg_color=self.card_color, border_width=1, border_color=self.border_color, corner_radius=8)
        img_card.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(img_card, text="ẢNH MINH HỌA ĐỒ UỐNG", font=ctk.CTkFont(size=11, weight="bold"), text_color=self.text_sub).pack(anchor="w", padx=15, pady=(15, 5))
        
        img_picker_frame = ctk.CTkFrame(img_card, fg_color="transparent")
        img_picker_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        lbl_preview = ctk.CTkLabel(img_picker_frame, text="☕", font=ctk.CTkFont(size=30), width=60, height=60, fg_color="#333333", corner_radius=8)
        lbl_preview.pack(side="left", padx=(0, 15))
        
        selected_img_path = [None]
        current_status = [1] # [LƯU TRẠNG THÁI]: Để không bị reset khi nhấn Sửa
        
        lbl_img_name = ctk.CTkLabel(img_picker_frame, text="Chưa có ảnh nào được chọn.", text_color=self.text_sub, font=ctk.CTkFont(slant="italic"))

        def pick_image():
            popup.attributes("-topmost", False)
            path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
            popup.attributes("-topmost", True)
            
            if path:
                selected_img_path[0] = path
                lbl_img_name.configure(text=os.path.basename(path), text_color="#3498DB")
                img = self.get_image(path, size=(60, 60))
                if img: lbl_preview.configure(image=img, text="")

        btn_pick = ctk.CTkButton(img_picker_frame, text="↑ Chọn ảnh từ thiết bị...", fg_color="transparent", border_width=1, border_color=self.text_sub, text_color=self.text_main, hover_color="#333333", command=pick_image)
        btn_pick.pack(side="top", fill="x", expand=True)
        lbl_img_name.pack(side="top", anchor="w", pady=(5, 0))

        # 4. Công thức (Recipe)
        ctk.CTkLabel(scroll, text="CẤU HÌNH ĐỊNH LƯỢNG TRỪ KHO TỰ ĐỘNG (RECIPE):", font=ctk.CTkFont(size=11, weight="bold"), text_color=self.text_sub).pack(anchor="w")
        recipe_card = ctk.CTkFrame(scroll, fg_color=self.card_color, border_width=1, border_color=self.border_color, corner_radius=8)
        recipe_card.pack(fill="x", pady=(5, 20))

        self.ingredient_data = self.controller.get_ingredients()
        
        ingredient_entries = []
        for ing in self.ingredient_data:
            ing_id, ing_name, ing_unit = ing[0], ing[1], ing[2]
            row = ctk.CTkFrame(recipe_card, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=8)
            
            ctk.CTkLabel(row, text=f"{ing_name}", font=ctk.CTkFont(weight="bold"), text_color=self.text_main).pack(side="left")
            
            qty_var = ctk.StringVar(value="")
            ctk.CTkLabel(row, text=ing_unit, text_color=self.text_sub).pack(side="right", padx=(5, 0))
            e_qty = ctk.CTkEntry(row, textvariable=qty_var, width=80, placeholder_text="0", justify="center", fg_color=self.bg_color, border_color=self.border_color, text_color=self.text_main)
            e_qty.pack(side="right")
            
            ingredient_entries.append({"id": ing_id, "name": ing_name, "var": qty_var})
            ctk.CTkFrame(recipe_card, height=1, fg_color=self.border_color).pack(fill="x", padx=15)

        # Đổ dữ liệu nếu là Sửa
        if drink_id:
            drink = self.controller.get_drink(drink_id)
            if drink:
                e_name.insert(0, drink[2])
                cb_cat.set(drink[3])
                e_price.insert(0, str(drink[4]))
                current_status[0] = drink[5] # Giữ lại trạng thái con_hang
                
                if drink[6]: 
                    selected_img_path[0] = drink[6]
                    lbl_img_name.configure(text=os.path.basename(drink[6]))
                    img = self.get_image(drink[6], size=(60, 60))
                    if img: lbl_preview.configure(image=img, text="")
                
                recipe = self.controller.get_recipe(drink_id)
                if recipe:
                    for ent in ingredient_entries:
                        if ent["id"] in recipe:
                            ent["var"].set(str(recipe[ent["id"]]))

        ctk.CTkButton(btn_frame, text="Hủy bỏ", fg_color="transparent", border_width=1, border_color=self.text_sub, text_color=self.text_main, hover_color="#333333", height=40, command=popup.destroy).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        def save_drink():
            name = e_name.get().strip()
            cat = cb_cat.get().strip()
            price_str = e_price.get().strip().replace(".", "") # Xóa dấu chấm nếu người dùng có nhập
            
            if not name or not price_str.isdigit():
                return messagebox.showerror("Lỗi", "Tên món không được trống và giá bán phải là số hợp lệ.", parent=popup)

            price = int(price_str)
            recipe_data = {}
            for ent in ingredient_entries:
                val = ent["var"].get().strip()
                if val:
                    try:
                        recipe_data[ent["id"]] = float(val.replace(",", "."))
                    except ValueError:
                        return messagebox.showerror("Lỗi", f"Số lượng cho '{ent['name']}' phải là số.", parent=popup)

            if drink_id:
                self.controller.update_item(drink_id, name, cat, price, selected_img_path[0], current_status[0], recipe_data)
            else:
                self.controller.add_item(name, cat, price, selected_img_path[0], recipe_data)
            
            self.refresh_menu_list()
            popup.destroy()

        ctk.CTkButton(btn_frame, text="Lưu vào thực đơn", fg_color=self.color_accent, hover_color="#D35400", text_color="white", height=40, font=ctk.CTkFont(weight="bold"), command=save_drink).pack(side="right", fill="x", expand=True, padx=(5, 0))

    def ui_delete_drink(self, drink_id):
        if messagebox.askyesno("Xác nhận", "Xóa món này khỏi Menu? Dữ liệu không thể khôi phục."):
            self.controller.delete_item(drink_id)
            self.refresh_menu_list()