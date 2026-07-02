import os
import datetime
import sqlite3
import win32print  
import win32ui
import win32con
from src.config import DB_PATH

class PrinterHelper:
    def __init__(self):
        # Đây là thư mục lưu các file .txt ảo thay cho giấy in thật
        self.output_dir = os.path.join(os.path.dirname(DB_PATH), "mock_receipts")
        os.makedirs(self.output_dir, exist_ok=True)
        self.db_path = str(DB_PATH)

    def _get_receipt_template(self):
        """Lấy thiết lập mẫu hóa đơn từ Database thực tế"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT ten_quan, dia_chi, dien_thoai, loi_cam_on FROM mau_hoa_don WHERE id = 1")
            row = cursor.fetchone()
        except:
            row = None
        conn.close()
        
        if row:
            return {"ten_quan": row[0], "dia_chi": row[1], "dien_thoai": row[2], "loi_cam_on": row[3]}
        else:
            # Fallback nếu chưa ai thiết lập mẫu
            return {
                "ten_quan": "COFFEE SHOP OFFLINE", 
                "dia_chi": "Địa chỉ quán", 
                "dien_thoai": "Hotline", 
                "loi_cam_on": "Cam on va hen gap lai!"
            }

    def print_receipt(self, order_id, table_name, items, total, cash_received, change_returned):
        """
        Dựng chuỗi hóa đơn chuẩn format K80 (Khoảng 42-48 ký tự/dòng) 
        rồi đẩy ra file .txt hoặc máy in.
        """
        # 1. Lấy khung Mẫu hóa đơn từ Database
        template = self._get_receipt_template()
        name = template["ten_quan"]
        addr = template["dia_chi"]
        phone = template["dien_thoai"]
        footer = template["loi_cam_on"]
        
        divider = "-" * 42
        now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # 2. Xây dựng Chuỗi hóa đơn bằng f-string đa dòng
        bill_lines = []
        
        # Header (Căn giữa)
        bill_lines.append(name.center(42))
        bill_lines.append(addr.center(42))
        bill_lines.append(phone.center(42))
        bill_lines.append(divider)
        bill_lines.append("HOA DON THANH TOAN".center(42))
        
        # Info
        bill_lines.append(f"So don: #{order_id}")
        bill_lines.append(f"Khu vuc: {table_name}")
        bill_lines.append(f"Ngay in: {now_str}")
        bill_lines.append(divider)
        
        # Bảng món ăn
        bill_lines.append("TEN MON                   SL    THANH TIEN")
        bill_lines.append(divider)
        
        for item in items:
            ten_mon = item[2]
            sl = int(item[3])
            thanh_tien = int(item[6])
            
            # Cắt ngắn tên món nếu quá dài (giữ tối đa 20 ký tự)
            if len(ten_mon) > 20:
                ten_mon = ten_mon[:17] + "..."
            
            # Căn lề: Tên món (22 char, Left) - SL (4 char, Center) - Tiền (14 char, Right)
            line = f"{ten_mon:<22}{str(sl).center(4)}{f'{thanh_tien:,.0f} đ':>16}"
            bill_lines.append(line.replace(",", "."))
        
        bill_lines.append(divider)
        
        # Tổng kết (Căn phải)
        bill_lines.append(f"TONG TIEN:              {f'{int(total):,.0f} đ':>18}".replace(",", "."))
        bill_lines.append(f"KHACH DUA:              {f'{int(cash_received):,.0f} đ':>18}".replace(",", "."))
        bill_lines.append(f"TIEN THUA:              {f'{int(change_returned):,.0f} đ':>18}".replace(",", "."))
        
        bill_lines.append(divider)
        
        # Footer
        bill_lines.append(footer.center(42))
        
        # 3. Gộp thành 1 chuỗi hoàn chỉnh
        final_receipt = "\n".join(bill_lines)

        try:
            # Lấy tên máy in mặc định trong Windows
            printer_name = win32print.GetDefaultPrinter()
            
            # Mở thiết bị in
            hDC = win32ui.CreateDC()
            hDC.CreatePrinterDC(printer_name)
            
            # Bắt đầu tác vụ in
            hDC.StartDoc("Receipt_" + str(order_id))
            hDC.StartPage()
            
            # Font chữ máy in nhiệt thường dùng (Courier New tạo cảm giác giống in nhiệt)
            font = win32ui.CreateFont({
                "name": "Courier New",
                "height": 20,
                "weight": 400,
            })
            hDC.SelectObject(font)

            # In từng dòng một
            y_pos = 100
            for line in bill_lines:
                hDC.TextOut(100, y_pos, line)
                y_pos += 30 # Khoảng cách dòng

            hDC.EndPage()
            hDC.EndDoc()
            hDC.DeleteDC()
            
            print(f"Đã gửi lệnh in đến máy: {printer_name}")

        except Exception as e:
            print(f"Lỗi kết nối máy in, đang chuyển sang lưu file dự phòng: {e}")
            
            # --- FALLBACK: TỰ ĐỘNG LƯU FILE TXT KHI IN LỖI ---
            filename = f"receipt_backup_{order_id}_{datetime.datetime.now().strftime('%H%M%S')}.txt"
            file_path = os.path.join(self.output_dir, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(final_receipt)
            
            # Thông báo cho người dùng biết là đã lưu file thay vì in
            try:
                import tkinter.messagebox as messagebox
                messagebox.showwarning("Cảnh báo máy in", f"Không thể in hóa đơn (lỗi: {e}).\nĐã lưu hóa đơn vào file dự phòng!")
            except:
                pass