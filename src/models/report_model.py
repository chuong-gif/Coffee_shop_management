import sqlite3
from src.config import DB_PATH

class ReportModel:
    def __init__(self):
        self.db_path = str(DB_PATH)

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def get_sales_summary(self, start_date, end_date):
        conn = self._connect()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COALESCE(SUM(tong_tien), 0), COALESCE(COUNT(*), 0) "
            "FROM don_hang "
            "WHERE trang_thai = 'Đã Thanh Toán' AND date(thoi_gian_thanh_toan) BETWEEN ? AND ?",
            (start_date, end_date),
        )
        total_revenue, total_orders = cursor.fetchone()

        cursor.execute(
            "SELECT COALESCE(SUM(so_luong), 0) "
            "FROM chi_tiet_don_hang "
            "WHERE don_hang_id IN ("
            "SELECT id FROM don_hang WHERE trang_thai = 'Đã Thanh Toán' AND date(thoi_gian_thanh_toan) BETWEEN ? AND ?"
            ")",
            (start_date, end_date),
        )
        total_items = cursor.fetchone()[0]

        # [TÍNH NĂNG MỚI]: Tính tổng chi phí dòng tiền nhập hàng (Thay vì tính hao hụt)
        cursor.execute(
            "SELECT COALESCE(SUM(chi_phi), 0) "
            "FROM lich_su_kiem_kho "
            "WHERE date(thoi_gian_kiem_kho) BETWEEN ? AND ?",
            (start_date, end_date),
        )
        total_restock_cost = cursor.fetchone()[0]
        
        conn.close()
        return {
            "total_revenue": total_revenue,
            "total_orders": total_orders,
            "total_items": total_items,
            "total_restock_cost": total_restock_cost,
        }

    def get_top_selling_items(self, start_date, end_date, limit=5):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT d.id, d.ten_mon, d.phan_loai, d.hinh_anh, SUM(c.so_luong) AS total_sold, SUM(c.so_luong * c.don_gia) AS total_revenue "
            "FROM chi_tiet_don_hang c "
            "JOIN do_uong d ON c.do_uong_id = d.id "
            "WHERE c.don_hang_id IN ("
            "SELECT id FROM don_hang WHERE trang_thai = 'Đã Thanh Toán' AND date(thoi_gian_thanh_toan) BETWEEN ? AND ?"
            ") "
            "GROUP BY d.id, d.ten_mon, d.phan_loai, d.hinh_anh "
            "ORDER BY total_sold DESC "
            "LIMIT ?",
            (start_date, end_date, limit),
        )
        items = cursor.fetchall()
        conn.close()
        return items

    def get_revenue_by_date(self, start_date, end_date):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT date(thoi_gian_thanh_toan) AS ngay, SUM(tong_tien) "
            "FROM don_hang "
            "WHERE trang_thai = 'Đã Thanh Toán' AND date(thoi_gian_thanh_toan) BETWEEN ? AND ? "
            "GROUP BY ngay ORDER BY ngay",
            (start_date, end_date)
        )
        data = cursor.fetchall()
        conn.close()
        return data