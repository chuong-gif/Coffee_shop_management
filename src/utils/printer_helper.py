# Tạo file hóa đơn text hoặc kết nối lệnh in ra máy in nhiệt
import os
import datetime

class PrinterHelper:
    def __init__(self, shop_name="COFFEE SHOP OFFLINE"):
        self.shop_name = shop_name
        # Lưu ý: Khi ra thực tế cắm máy in qua USB, bạn sẽ dùng:
        # from escpos.printer import Usb
        # self.printer = Usb(0x04b8, 0x0202, 0, profile="TM-T88V")

    def print_receipt(self, order_id, table_name, items, total_amount, cash_given, change):
        """
        Hàm tạo template hóa đơn khổ K80 (khoảng 48 ký tự / dòng)
        Tạm thời xuất ra file .txt và tự động mở lên để mô phỏng máy in.
        """
        divider = "-" * 48
        now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        lines = []
        lines.append(self.shop_name.center(48))
        lines.append("HOA DON THANH TOAN".center(48))
        lines.append(divider)
        lines.append(f"So don: #{order_id}")
        lines.append(f"Khu vuc: {table_name}")
        lines.append(f"Ngay in: {now}")
        lines.append(divider)
        lines.append(f"{'TEN MON':<25} {'SL':<5} {'THANH TIEN':>16}")
        lines.append(divider)

        for item in items:
            # item = (item_id, do_uong_id, ten_mon, so_luong, don_gia, ghi_chu, thanh_tien, custom_recipe)
            ten_mon = item[2][:25] # Cắt ngắn tên nếu quá dài
            sl = item[3]
            thanh_tien = f"{item[6]:,.0f}".replace(",", ".")
            lines.append(f"{ten_mon:<25} {sl:<5} {thanh_tien:>16}")
            
            ghi_chu = item[5]
            if ghi_chu:
                lines.append(f"  * {ghi_chu}")

        lines.append(divider)
        lines.append(f"{'TONG TIEN:':<25} {f'{total_amount:,.0f} VND':>22}".replace(",", "."))
        lines.append(f"{'KHACH DUA:':<25} {f'{cash_given:,.0f} VND':>22}".replace(",", "."))
        lines.append(f"{'TIEN THUA:':<25} {f'{change:,.0f} VND':>22}".replace(",", "."))
        lines.append(divider)
        lines.append("Cam on va hen gap lai!".center(48))
        lines.append("Wifi: CoffeeShop | Pass: 88888888".center(48))
        lines.append("\n\n\n") # Đẩy giấy lên để cắt

        receipt_text = "\n".join(lines)

        # Mô phỏng máy in bằng cách ghi ra file txt và mở lên
        filename = f"receipt_mock_{order_id}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(receipt_text)
        
        # Tự động mở file (Hoạt động trên Windows)
        os.startfile(filename)