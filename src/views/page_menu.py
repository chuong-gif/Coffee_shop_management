import os
import customtkinter as ctk
import tkinter.messagebox as messagebox
from tkinter import filedialog
from src.controllers.menu_controller import MenuController

class PageMenu(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.controller = MenuController()
        self.selected_drink_id = None
        self.image_path = None

        self.lbl_title = ctk.CTkLabel(self, text="QUẢN LÝ MENU ĐỒ UỐNG", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_title.pack(pady=(10, 10))

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=20, pady=(0, 10))
        self.btn_add = ctk.CTkButton(toolbar, text="+ Thêm Món", width=120, command=self.ui_open_drink_dialog)
        self.btn_add.pack(side="right", padx=10)

        content_frame = ctk.CTkFrame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        content_frame.grid_columnconfigure(0, weight=2)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        self.left_panel = ctk.CTkFrame(content_frame)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.right_panel = ctk.CTkFrame(content_frame)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        self.left_title = ctk.CTkLabel(self.left_panel, text="Đồ Uống", font=ctk.CTkFont(size=18, weight="bold"))
        self.left_title.pack(anchor="w", padx=10, pady=(10, 5))

        self.right_title = ctk.CTkLabel(self.right_panel, text="Danh Mục", font=ctk.CTkFont(size=18, weight="bold"))
        self.right_title.pack(anchor="w", padx=10, pady=(10, 5))

        self.category_frame = ctk.CTkFrame(self.right_panel)
        self.category_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.entry_new_category = ctk.CTkEntry(self.category_frame, placeholder_text="Tên danh mục mới")
        self.entry_new_category.pack(side="top", padx=10, pady=10, fill="x")

        self.btn_add_category = ctk.CTkButton(self.category_frame, text="+ Thêm Danh Mục", command=self.ui_add_category)
        self.btn_add_category.pack(side="top", padx=10, pady=(0, 10), fill="x")

        self.category_combo = ctk.CTkComboBox(self.category_frame, values=[], width=180)
        self.category_combo.pack(side="top", padx=10, pady=(0, 10), fill="x")

        self.btn_rename_category = ctk.CTkButton(self.category_frame, text="Sửa Danh Mục", command=self.ui_rename_category)
        self.btn_rename_category.pack(side="top", padx=10, pady=(0, 10), fill="x")

        self.btn_delete_category = ctk.CTkButton(self.category_frame, text="Xóa Danh Mục", fg_color="#E74C3C", hover_color="#C0392B", command=self.ui_delete_category)
        self.btn_delete_category.pack(side="top", padx=10, pady=(0, 10), fill="x")

        self.tab_view = ctk.CTkTabview(self.left_panel)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.refresh_menu_list()

    def ui_open_drink_dialog(self, drink_id=None):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Thêm / Sửa Món")
        dialog.geometry("560x700")
        dialog.minsize(540, 620)
        dialog.attributes("-topmost", True)

        content_frame = ctk.CTkScrollableFrame(dialog)
        content_frame.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        ctk.CTkLabel(content_frame, text="Tên món", anchor="w").pack(fill="x", padx=20, pady=(10, 5))
        ent_name = ctk.CTkEntry(content_frame, placeholder_text="Tên món")
        ent_name.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(content_frame, text="Phân loại", anchor="w").pack(fill="x", padx=20, pady=(10, 5))
        categories = self.controller.get_categories()
        cbo_category = ctk.CTkComboBox(content_frame, values=categories or ["Khác"], width=240)
        cbo_category.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(content_frame, text="Giá bán", anchor="w").pack(fill="x", padx=20, pady=(10, 5))
        ent_price = ctk.CTkEntry(content_frame, placeholder_text="Giá bán")
        ent_price.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(content_frame, text="Hình ảnh món", anchor="w").pack(fill="x", padx=20, pady=(10, 5))
        img_frame = ctk.CTkFrame(content_frame)
        img_frame.pack(fill="x", padx=20, pady=5)
        selected_image = [None]
        img_label = ctk.CTkLabel(img_frame, text="Chưa chọn ảnh")
        img_label.pack(side="left", padx=5)
        def choose_image():
            path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")])
            if path:
                selected_image[0] = path
                img_label.configure(text=os.path.basename(path))
        ctk.CTkButton(img_frame, text="Chọn ảnh", width=100, command=choose_image).pack(side="right", padx=5)

        ctk.CTkLabel(content_frame, text="Chọn nguyên liệu có sẵn trong kho và nhập số lượng dùng cho món", anchor="w", font=ctk.CTkFont(size=12)).pack(fill="x", padx=20, pady=(10, 5))
        self.ingredient_rows = []
        ingredients = self.controller.get_ingredients()
        ingred_frame = ctk.CTkScrollableFrame(content_frame, width=520, height=280)
        ingred_frame.pack(fill="both", padx=20, pady=5, expand=False)

        header_row = ctk.CTkFrame(ingred_frame, fg_color="transparent")
        header_row.pack(fill="x", pady=(0, 5), padx=2)
        ctk.CTkLabel(header_row, text="Nguyên liệu", width=220, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header_row, text="Đơn vị", width=90, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header_row, text="Dùng", width=90, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)

        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(fill="x", padx=20, pady=(0, 15))

        for ing in ingredients:
            ing_id, ing_name, ing_unit, ing_theory, ing_actual, ing_warn, ing_cost = ing
            row_frame = ctk.CTkFrame(ingred_frame, fg_color="#1f1f1f")
            row_frame.pack(fill="x", pady=2, padx=2)
            enabled_var = ctk.StringVar(value="off")
            chk = ctk.CTkCheckBox(row_frame, text=f"{ing_name}", variable=enabled_var, onvalue="on", offvalue="off")
            chk.pack(side="left", padx=5)
            ctk.CTkLabel(row_frame, text=ing_unit, width=90, anchor="w").pack(side="left", padx=5)
            qty_var = ctk.StringVar(value="")
            qty_entry = ctk.CTkEntry(row_frame, width=90, textvariable=qty_var, placeholder_text="Số lượng")
            qty_entry.pack(side="left", padx=5)
            self.ingredient_rows.append({"id": ing_id, "name": ing_name, "unit": ing_unit, "enabled": enabled_var, "qty": qty_var})

        if drink_id:
            drink = self.controller.get_drink(drink_id)
            if drink:
                d_id, ma_mon, ten_mon, phan_loai, gia_ban, con_hang, hinh_anh = drink
                ent_name.insert(0, ten_mon)
                if phan_loai:
                    cbo_category.set(phan_loai)
                ent_price.insert(0, str(gia_ban))
                selected_image[0] = hinh_anh
                img_label.configure(text=os.path.basename(hinh_anh) if hinh_anh else "Chưa chọn ảnh")
                recipe = self.controller.get_recipe(drink_id)
                if recipe:
                    for row in self.ingredient_rows:
                        if row["id"] in recipe:
                            row["enabled"].set("on")
                            row["qty"].set(str(recipe[row["id"]]))

        def submit_drink():
            name = ent_name.get().strip()
            category = cbo_category.get().strip()
            price = ent_price.get().strip()
            recipe_data = {}
            for row in self.ingredient_rows:
                if row["enabled"].get() == "on":
                    qty_text = row["qty"].get().strip()
                    if not qty_text or not qty_text.replace('.', '', 1).isdigit():
                        return messagebox.showerror("Lỗi", f"Số lượng cho {row['name']} không hợp lệ.")
                    recipe_data[row["id"]] = float(qty_text)
            if not name or not category or not price.isdigit():
                return messagebox.showerror("Lỗi", "Tên, phân loại và giá bán phải đúng định dạng.")
            if drink_id:
                self.controller.update_item(drink_id, name, category, int(price), selected_image[0], recipe_data)
            else:
                self.controller.add_item(name, category, int(price), selected_image[0], recipe_data)
            dialog.destroy()
            self.refresh_menu_list()

        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(fill="x", padx=20, pady=(10, 15))
        ctk.CTkButton(button_frame, text="Lưu món", command=submit_drink).pack(side="right")

    def ui_edit_drink(self, drink_id):
        self.ui_open_drink_dialog(drink_id)

    def ui_add_category(self):
        category = self.entry_new_category.get().strip()
        if not category:
            return messagebox.showerror("Lỗi", "Tên danh mục không được để trống.")
        self.controller.add_category(category)
        self.entry_new_category.delete(0, 'end')
        self.refresh_menu_list()

    def ui_rename_category(self):
        old_cat = self.category_combo.get().strip()
        if not old_cat:
            return messagebox.showerror("Lỗi", "Chọn danh mục để sửa.")
        new_cat = messagebox.askstring("Sửa danh mục", f"Nhập tên mới cho danh mục {old_cat}:")
        if new_cat:
            self.controller.rename_category(old_cat, new_cat.strip())
            self.refresh_menu_list()

    def ui_delete_category(self):
        category = self.category_combo.get().strip()
        if not category:
            return messagebox.showerror("Lỗi", "Chọn danh mục để xóa.")
        if messagebox.askyesno("Xác nhận", f"Xóa danh mục {category}? Các món sẽ chuyển sang 'Khác'."):
            self.controller.delete_category(category)
            self.refresh_menu_list()

    def ui_add_drink(self):
        self.ui_open_drink_dialog()

    def refresh_menu_list(self):
        """Xóa tab cũ và vẽ lại giao diện dạng Thẻ (Card) theo từng phân loại"""
        # Xóa các tab hiện tại
        for tab_name in self.tab_view._name_list:
            self.tab_view.delete(tab_name)

        categories = self.controller.get_categories()
        self.category_combo.configure(values=categories)
        if categories and not self.category_combo.get():
            self.category_combo.set(categories[0])

        drinks = self.controller.get_menu()
        
        # Nhóm đồ uống theo phân loại
        grouped = {}
        for drink in drinks:
            _, _, ten_mon, phan_loai, gia_ban, con_hang, _ = drink
            grouped.setdefault(phan_loai or "Khác", []).append(drink)

        # Tạo tab cho mỗi phân loại và vẽ dạng thẻ
        for cat, items in grouped.items():
            self.tab_view.add(cat)
            scroll_frame = ctk.CTkScrollableFrame(self.tab_view.tab(cat), fg_color="transparent")
            scroll_frame.pack(fill="both", expand=True)

            for item in items:
                d_id, ma_mon, d_name, d_cat, d_price, d_status, d_image = item
                
                # Tạo Thẻ (Card) cho từng món
                card = ctk.CTkFrame(scroll_frame, corner_radius=8)
                card.pack(fill="x", pady=5, padx=5)

                color_hex = f"#{abs(hash(d_name)) % 0xFFFFFF:06x}"
                color_block = ctk.CTkFrame(card, width=15, height=40, fg_color=color_hex, corner_radius=0)
                color_block.pack(side="left", fill="y", padx=(0, 10))

                ctk.CTkLabel(card, text=d_name, width=220, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
                ctk.CTkLabel(card, text=f"{d_price:,} đ".replace(",", "."), width=100, anchor="w").pack(side="left", padx=10)

                switch_var = ctk.StringVar(value="on" if d_status == 1 else "off")
                ctk.CTkSwitch(
                    card,
                    text="Còn hàng" if d_status == 1 else "Hết hàng",
                    variable=switch_var,
                    onvalue="on",
                    offvalue="off",
                    button_color="#2ECC71" if d_status == 1 else "#E74C3C",
                    command=lambda id=d_id, curr=d_status: self.ui_toggle_status(id, curr),
                ).pack(side="left", padx=30)

                ctk.CTkButton(
                    card,
                    text="Sửa",
                    width=50,
                    fg_color="#F1C40F",
                    hover_color="#F39C12",
                    command=lambda id=d_id: self.ui_edit_drink(id),
                ).pack(side="right", padx=10)

                ctk.CTkButton(
                    card,
                    text="Xóa",
                    width=50,
                    fg_color="#7F8C8D",
                    hover_color="#95A5A6",
                    command=lambda id=d_id: self.ui_delete_drink(id),
                ).pack(side="right", padx=10)

    def ui_delete_drink(self, drink_id):
        if messagebox.askyesno("Xác nhận", "Xóa món này khỏi Menu?"):
            self.controller.delete_item(drink_id)
            self.refresh_menu_list()

    def ui_toggle_status(self, drink_id, current_status):
        self.controller.toggle_item_status(drink_id, current_status)
        self.refresh_menu_list()