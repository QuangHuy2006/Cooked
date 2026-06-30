import sqlite3
from datetime import datetime
import json

DB_NAME = "gplx_history.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verified_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gplx TEXT UNIQUE NOT NULL,
            dob TEXT NOT NULL,
            status TEXT NOT NULL,
            data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def is_gplx_verified(gplx: str) -> bool:
    """Kiểm tra xem GPLX đã được xác thực thành công chưa."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM verified_users WHERE gplx = ? AND status = "success"', (gplx,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def get_verified_data(gplx: str):
    """Lấy dữ liệu GPLX đã xác thực."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT data FROM verified_users WHERE gplx = ? AND status = "success"', (gplx,))
    result = cursor.fetchone()
    conn.close()
    if result and result[0]:
        return json.loads(result[0])
    return None

def get_stored_dob(gplx: str):
    """Lấy ngày sinh đã lưu của GPLX."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT dob FROM verified_users WHERE gplx = ? AND status = "success"', (gplx,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def save_verification(gplx: str, dob: str, status: str, data: dict = None):
    """Lưu kết quả xác thực."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    data_str = json.dumps(data, ensure_ascii=False) if data else None
    
    # Dùng REPLACE để ghi đè nếu đã tồn tại nhưng có thể trước đó là lỗi, nay thành công
    cursor.execute('''
        INSERT OR REPLACE INTO verified_users (id, gplx, dob, status, data, created_at)
        VALUES (
            (SELECT id FROM verified_users WHERE gplx = ?),
            ?, ?, ?, ?, ?
        )
    ''', (gplx, gplx, dob, status, data_str, datetime.now()))
    
    conn.commit()
    conn.close()

def get_all_history():
    """Lấy toàn bộ lịch sử (cho trang quản trị nếu cần)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT gplx, dob, status, created_at, data FROM verified_users ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        name = ""
        if r[4]:
            try:
                data_dict = json.loads(r[4])
                # Tìm trường có chữ "tên" để lấy tên
                if isinstance(data_dict, dict):
                    for k, v in data_dict.items():
                        if "tên" in k.lower() or "name" in k.lower():
                            name = str(v)
                            break
            except Exception:
                pass
                
        result.append({
            "gplx": r[0], 
            "dob": r[1], 
            "status": r[2], 
            "created_at": r[3],
            "name": name
        })
    return result

# Khởi tạo DB khi load module
init_db()
