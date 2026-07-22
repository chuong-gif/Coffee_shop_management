# 📂 Kiến Trúc Mã Nguồn (Source Code Architecture)

Mã nguồn được tổ chức theo mô hình **MVC (Model - View - Controller)**: tách biệt giao diện, luồng xử lý nghiệp vụ và tầng dữ liệu để dễ bảo trì và mở rộng.

## 🗂️ Cấu Trúc Thư Mục

```text
src/
│
├── config.py               # Cấu hình hệ thống, đường dẫn database dùng chung
│
├── controllers/            # Điều phối logic giữa View và Model
│   ├── backup_controller.py
│   ├── menu_controller.py
│   ├── order_controller.py
│   ├── report_controller.py
│   ├── stock_controller.py
│   └── table_controller.py
│
├── models/                 # Tương tác trực tiếp với SQLite & xử lý nghiệp vụ thô
│   ├── db_manager.py       # Quản lý kết nối, backup/restore database
│   ├── menu_model.py
│   ├── order_model.py
│   ├── report_model.py
│   ├── stock_model.py
│   └── table_model.py
│
├── views/                  # Giao diện người dùng (CustomTkinter)
│   ├── login_window.py     # Cửa sổ đăng nhập
│   ├── main_window.py      # Cửa sổ chính, điều hướng sidebar
│   ├── page_account.py     # Quản lý tài khoản & phân quyền
│   ├── page_data.py        # Quản lý dữ liệu / sao lưu
│   ├── page_history.py     # Lịch sử hóa đơn & kế toán
│   ├── page_menu.py        # Quản lý thực đơn
│   ├── page_report.py      # Dashboard báo cáo doanh thu
│   ├── page_stock.py       # Quản lý kho nguyên liệu
│   └── pos/                # Giao diện bán hàng
│       ├── page_pos_main.py
│       ├── left_pane.py
│       └── right_pane.py
│
└── utils/                  # Hàm tiện ích dùng chung
    ├── drive_helper.py     # Đồng bộ sao lưu lên Google Drive
    ├── excel_helper.py     # Xuất dữ liệu ra Excel
    ├── printer_helper.py   # In hóa đơn
    └── session.py          # Quản lý phiên đăng nhập
```

## 🔄 Luồng Hoạt Động (Data Flow)

1. **View** — tiếp nhận thao tác của người dùng (click, nhập liệu), ví dụ bấm "Thanh toán" trong `page_pos_main.py`.
2. **Controller** — nhận sự kiện từ View, kiểm tra ràng buộc, điều phối gọi Model tương ứng (ví dụ `order_controller.py` xử lý logic đặt/thanh toán đơn).
3. **Model** — thực thi truy vấn SQLite (`sqlite3` qua `db_manager.py`), thực hiện trừ kho, cập nhật trạng thái đơn, tính doanh thu, rồi trả kết quả ngược lại cho Controller → View.

## 📌 Ghi Chú Theo Module

- `db_manager.py` đảm nhiệm việc backup/restore database (sao lưu zip có mốc thời gian, kèm `manifest.json` kiểm tra tương thích phiên bản); `backup_controller.py` và `drive_helper.py` phối hợp để đẩy bản sao lưu lên Google Drive.
- `report_model.py` / `report_controller.py` / `page_report.py` tạo thành luồng riêng cho dashboard báo cáo doanh thu (KPI cards, top món bán chạy).
- `views/pos/` tách riêng khỏi các trang còn lại trong `views/` vì giao diện bán hàng có nhiều panel con (`left_pane`, `right_pane`) cần bố cục linh hoạt (grid/PanedWindow) riêng biệt.
