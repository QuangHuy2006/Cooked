import os
import json
from datetime import datetime
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print("Lỗi kết nối Supabase:", e)

def init_db():
    # Supabase không cần tạo bảng từ code Python, bảng được tạo trực tiếp trên giao diện Supabase.
    pass

def is_gplx_verified(gplx: str) -> bool:
    """Kiểm tra xem GPLX đã được xác thực thành công chưa."""
    if not supabase: return False
    try:
        response = supabase.table('verified_users').select('id').eq('gplx', gplx).eq('status', 'success').execute()
        return len(response.data) > 0
    except Exception:
        return False

def get_verified_data(gplx: str):
    """Lấy dữ liệu GPLX đã xác thực."""
    if not supabase: return None
    try:
        response = supabase.table('verified_users').select('data').eq('gplx', gplx).eq('status', 'success').execute()
        if response.data and len(response.data) > 0:
            data = response.data[0].get('data')
            if isinstance(data, str):
                return json.loads(data)
            return data
    except Exception:
        pass
    return None

def get_stored_dob(gplx: str):
    """Lấy ngày sinh đã lưu của GPLX."""
    if not supabase: return None
    try:
        response = supabase.table('verified_users').select('dob').eq('gplx', gplx).eq('status', 'success').execute()
        if response.data and len(response.data) > 0:
            return response.data[0].get('dob')
    except Exception:
        pass
    return None

def save_verification(gplx: str, dob: str, status: str, data: dict = None):
    """Lưu kết quả xác thực (thêm mới hoặc cập nhật)."""
    if not supabase: return
    try:
        data_str = json.dumps(data, ensure_ascii=False) if data else None
        
        payload = {
            "gplx": gplx,
            "dob": dob,
            "status": status,
            "data": data_str
        }
        
        # Kiểm tra xem gplx đã tồn tại chưa
        res = supabase.table('verified_users').select('id').eq('gplx', gplx).execute()
        
        if res.data and len(res.data) > 0:
            # Cập nhật nếu đã có
            supabase.table('verified_users').update(payload).eq('gplx', gplx).execute()
        else:
            # Thêm mới
            supabase.table('verified_users').insert(payload).execute()
    except Exception as e:
        print("Lỗi lưu dữ liệu Supabase:", e)

def get_all_history():
    """Lấy toàn bộ lịch sử (cho trang quản trị)."""
    if not supabase: return []
    try:
        response = supabase.table('verified_users').select('gplx, dob, status, created_at, data').order('created_at', desc=True).execute()
        rows = response.data
        
        result = []
        for r in rows:
            name = ""
            data_val = r.get('data')
            if data_val:
                try:
                    data_dict = json.loads(data_val) if isinstance(data_val, str) else data_val
                    if isinstance(data_dict, dict):
                        for k, v in data_dict.items():
                            if "tên" in k.lower() or "name" in k.lower():
                                name = str(v)
                                break
                except Exception:
                    pass
                    
            result.append({
                "gplx": r.get('gplx'), 
                "dob": r.get('dob'), 
                "status": r.get('status'), 
                "created_at": r.get('created_at'),
                "name": name
            })
        return result
    except Exception as e:
        print("Lỗi lấy lịch sử Supabase:", e)
        return []

# Bỏ init_db vì Supabase tạo bảng trên web
