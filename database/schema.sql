-- 1. Bảng quản lý Bàn (Trang 1)
CREATE TABLE IF NOT EXISTS ban (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ten_ban TEXT NOT NULL UNIQUE,
    trang_thai TEXT NOT NULL DEFAULT 'Trống' -- 'Trống' hoặc 'Có khách'
);

-- 2. Bảng quản lý Đồ uống (Trang 2)
CREATE TABLE IF NOT EXISTS do_uong (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_mon TEXT NOT NULL UNIQUE,
    ten_mon TEXT NOT NULL,
    phan_loai TEXT NOT NULL,
    gia_ban INTEGER NOT NULL,
    hinh_anh TEXT DEFAULT NULL,
    con_hang INTEGER NOT NULL DEFAULT 1, -- 1 là còn hàng, 0 là hết hàng
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2a. Bảng Danh mục đồ uống
CREATE TABLE IF NOT EXISTS danh_muc (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ten_danh_muc TEXT NOT NULL UNIQUE
);

-- 3. Bảng Đơn hàng (Trang 1 & 4)
CREATE TABLE IF NOT EXISTS don_hang (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_don TEXT UNIQUE,
    ban_id INTEGER,
    loai_don TEXT NOT NULL DEFAULT 'Tại bàn', -- 'Tại bàn' hoặc 'Mang về'
    tong_tien INTEGER NOT NULL DEFAULT 0,
    tien_khach_dua INTEGER NOT NULL DEFAULT 0,
    tien_thua INTEGER NOT NULL DEFAULT 0,
    ghi_chu TEXT DEFAULT NULL,
    trang_thai TEXT NOT NULL DEFAULT 'Mở',
    thoi_gian_tao DATETIME DEFAULT CURRENT_TIMESTAMP,
    thoi_gian_thanh_toan DATETIME,
    FOREIGN KEY(ban_id) REFERENCES ban(id)
);

-- 4. Bảng Chi tiết đơn hàng (Trang 1)
CREATE TABLE IF NOT EXISTS chi_tiet_don_hang (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    don_hang_id INTEGER NOT NULL,
    do_uong_id INTEGER NOT NULL,
    so_luong INTEGER NOT NULL DEFAULT 1,
    don_gia INTEGER NOT NULL,
    ghi_chu TEXT DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(don_hang_id) REFERENCES don_hang(id),
    FOREIGN KEY(do_uong_id) REFERENCES do_uong(id)
);

-- 5. Bảng Kho nguyên liệu (Trang 3)
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

-- 6. Bảng Lịch sử kiểm kho (Trang 3 & 4)
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

-- 7. Bảng Công thức liên kết đồ uống với nguyên liệu (dùng để trừ kho tự động)
CREATE TABLE IF NOT EXISTS cong_thuc (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    do_uong_id INTEGER NOT NULL,
    nguyen_lieu_id INTEGER NOT NULL,
    so_luong_tru REAL NOT NULL,
    FOREIGN KEY(do_uong_id) REFERENCES do_uong(id),
    FOREIGN KEY(nguyen_lieu_id) REFERENCES kho_nguyen_lieu(id)
);
