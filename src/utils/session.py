# Biến toàn cục lưu thông tin user đang đăng nhập
current_user = {
    "id": None,
    "ten_dang_nhap": None,
    "ho_ten": None,
    "quyen_ban_hang": 0,
    "quyen_do_uong": 0,
    "quyen_kho": 0,
    "quyen_thong_ke": 0,
    "quyen_lich_su": 0,       # <-- MỚI
    "quyen_tai_khoan": 0,     # <-- MỚI
    "quyen_du_lieu": 0,
    "quyen_ma_giam_gia": 0
}

def login(user_data):
    global current_user
    current_user.update(user_data)

def logout():
    global current_user
    for key in current_user:
        current_user[key] = 0 if "quyen" in key else None