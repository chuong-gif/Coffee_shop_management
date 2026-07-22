# ☕ Coffee Shop Management System (POS Offline)

Phần mềm quản lý quán cà phê chạy **ngoại tuyến** (Desktop App), xây dựng bằng **Python** + **CustomTkinter**, theo kiến trúc **MVC** (Model - View - Controller), hướng tới các mô hình F&B quy mô vừa và nhỏ.

## 🎬 Demo

Video quay lướt qua các trang và tính năng chính: [`docs/Video Demo.mp4`](./docs/Video%20Demo.mp4)

## 🚀 Tính Năng Chính

**Bán hàng (POS)**
- Sơ đồ bàn trực quan (trống / có khách), đơn tại bàn và mang về
- Tùy chỉnh định lượng nguyên liệu theo món (custom recipe)
- Mã giảm giá theo % hoặc tiền mặt, có ngày bắt đầu/kết thúc

**Quản lý kho**
- Theo dõi song song tồn kho lý thuyết (trừ tự động) và tồn thực tế (kiểm đếm tay)
- Tự động tính giá vốn trung bình động khi nhập hàng
- Lịch sử kiểm kho, theo dõi hao hụt

**Hóa đơn & Báo cáo**
- Lọc hóa đơn theo khoảng thời gian, in lại, hủy đơn (tự động hoàn kho)
- Sửa hóa đơn thông minh: mở lại đơn cũ, hoàn kho, chỉnh sửa và thanh toán lại mà không lệch dữ liệu báo cáo
- Dashboard báo cáo doanh thu với các thẻ KPI và danh sách món bán chạy

**Quản lý dữ liệu & Sao lưu**
- Sao lưu đóng gói dạng zip có gắn mốc thời gian, dùng cơ chế backup gốc của SQLite
- Xoay vòng bản sao lưu cục bộ, đồng bộ lên Google Drive để lưu trữ ngoài
- `manifest.json` kiểm soát tương thích phiên bản khi khôi phục

**Tài khoản**
- Đăng nhập, phân quyền chi tiết giữa nhân viên và quản trị viên

## 🛠️ Công Nghệ Sử Dụng

- **Ngôn ngữ:** Python 3.x
- **Giao diện:** CustomTkinter
- **Cơ sở dữ liệu:** SQLite
- **Xuất báo cáo:** Excel (openpyxl/tương tự), Google Drive API (sao lưu)
- **Đóng gói:** PyInstaller (`CoffeeShopPOS.spec`)

## ⚙️ Cài Đặt & Chạy

```bash
git clone <repo-url>
cd <ten-thu-muc-du-an>

python -m venv venv
venv\Scripts\activate      # Windows

pip install -r requirements.txt

python main.py
```

## 📁 Cấu Trúc Dự Án

```text
.
├── main.py                  # Điểm khởi chạy ứng dụng
├── requirements.txt
├── CoffeeShopPOS.spec       # Cấu hình đóng gói PyInstaller
├── docs/
│   └── Video Demo.mp4       # Video giới thiệu tính năng
└── src/                     # Mã nguồn chính — xem src/README.md
```

Chi tiết kiến trúc mã nguồn: xem [`src/README.md`](./src/README.md).

---

*Developed by Ngo Van Chuong.*
