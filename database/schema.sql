-- 1. Bảng quản lý Bàn
CREATE TABLE IF NOT EXISTS ban (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ten_ban TEXT NOT NULL UNIQUE,
    trang_thai TEXT NOT NULL DEFAULT 'Trống'
);

-- 2. Bảng quản lý Đồ uống
CREATE TABLE IF NOT EXISTS do_uong (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_mon TEXT NOT NULL UNIQUE,
    ten_mon TEXT NOT NULL,
    phan_loai TEXT NOT NULL,
    gia_ban INTEGER NOT NULL,
    hinh_anh TEXT DEFAULT NULL,
    con_hang INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2a. Bảng Danh mục đồ uống
CREATE TABLE IF NOT EXISTS danh_muc (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ten_danh_muc TEXT NOT NULL UNIQUE
);

-- 3. Bảng Đơn hàng (ĐÃ THÊM: tien_giam_gia, ma_giam_gia_ap_dung)
CREATE TABLE IF NOT EXISTS don_hang (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_don TEXT UNIQUE,
    ban_id INTEGER,
    loai_don TEXT NOT NULL DEFAULT 'Tại bàn',
    tong_tien INTEGER NOT NULL DEFAULT 0,
    tien_giam_gia INTEGER NOT NULL DEFAULT 0,
    ma_giam_gia_ap_dung TEXT DEFAULT NULL,
    tien_khach_dua INTEGER NOT NULL DEFAULT 0,
    tien_thua INTEGER NOT NULL DEFAULT 0,
    ghi_chu TEXT DEFAULT NULL,
    trang_thai TEXT NOT NULL DEFAULT 'Mở',
    thoi_gian_tao DATETIME DEFAULT CURRENT_TIMESTAMP,
    thoi_gian_thanh_toan DATETIME,
    FOREIGN KEY(ban_id) REFERENCES ban(id)
);

-- 4. Bảng Chi tiết đơn hàng (ĐÃ THÊM: cong_thuc_tuy_chinh)
CREATE TABLE IF NOT EXISTS chi_tiet_don_hang (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    don_hang_id INTEGER NOT NULL,
    do_uong_id INTEGER NOT NULL,
    so_luong INTEGER NOT NULL DEFAULT 1,
    don_gia INTEGER NOT NULL,
    gia_von INTEGER NOT NULL DEFAULT 0,
    ghi_chu TEXT DEFAULT NULL,
    cong_thuc_tuy_chinh TEXT DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(don_hang_id) REFERENCES don_hang(id),
    FOREIGN KEY(do_uong_id) REFERENCES do_uong(id)
);

-- 5. Bảng Kho nguyên liệu
CREATE TABLE IF NOT EXISTS kho_nguyen_lieu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ten_nguyen_lieu TEXT NOT NULL UNIQUE,
    don_vi TEXT NOT NULL,
    ton_ly_thuyet REAL NOT NULL DEFAULT 0,
    ton_thuc_te REAL NOT NULL DEFAULT 0,
    muc_canh_bao REAL NOT NULL DEFAULT 0,
    gia_von REAL NOT NULL DEFAULT 0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 6. Bảng Lịch sử kiểm kho
CREATE TABLE IF NOT EXISTS lich_su_kiem_kho (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nguyen_lieu_id INTEGER NOT NULL,
    ton_ly_thuyet REAL NOT NULL,
    ton_thuc_te REAL NOT NULL,
    so_luong_lech REAL NOT NULL,
    ly_do TEXT DEFAULT NULL,
    thoi_gian_kiem_kho DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(nguyen_lieu_id) REFERENCES kho_nguyen_lieu(id)
);

-- 7. Bảng Công thức liên kết đồ uống
CREATE TABLE IF NOT EXISTS cong_thuc (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    do_uong_id INTEGER NOT NULL,
    nguyen_lieu_id INTEGER NOT NULL,
    so_luong_tru REAL NOT NULL,
    FOREIGN KEY(do_uong_id) REFERENCES do_uong(id),
    FOREIGN KEY(nguyen_lieu_id) REFERENCES kho_nguyen_lieu(id)
);

CREATE INDEX idx_don_hang_thoi_gian ON don_hang(thoi_gian_thanh_toan);
CREATE INDEX idx_don_hang_trang_thai ON don_hang(trang_thai);

-- 8. Bảng Tài khoản & Phân quyền (ĐÃ THÊM: TRỌN BỘ 8 QUYỀN)
CREATE TABLE IF NOT EXISTS tai_khoan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ten_dang_nhap TEXT NOT NULL UNIQUE,
    mat_khau TEXT NOT NULL,
    ho_ten TEXT NOT NULL,
    quyen_ban_hang INTEGER DEFAULT 1,
    quyen_do_uong INTEGER DEFAULT 0,
    quyen_kho INTEGER DEFAULT 0,
    quyen_thong_ke INTEGER DEFAULT 0,
    quyen_lich_su INTEGER DEFAULT 0,
    quyen_tai_khoan INTEGER DEFAULT 0,
    quyen_du_lieu INTEGER DEFAULT 0,
    quyen_ma_giam_gia INTEGER DEFAULT 0
);

-- 9. Bảng Mã giảm giá (ĐÃ THÊM: ngay_bat_dau & ngay_ket_thuc)
CREATE TABLE IF NOT EXISTS ma_giam_gia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_code TEXT NOT NULL UNIQUE,
    loai_giam TEXT NOT NULL, 
    gia_tri INTEGER NOT NULL,
    ngay_bat_dau DATETIME NOT NULL,
    ngay_ket_thuc DATETIME NOT NULL
);