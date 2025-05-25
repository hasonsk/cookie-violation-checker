Dưới đây là **các use case kiểm tra vi phạm loại 1** (`Specific – Retention`):

> Cookie **được khai báo là "session"** nhưng thực tế lại **tồn tại quá 24 giờ sau khi đóng trình duyệt**.

### ✅ **1. Use case hợp lệ (KHÔNG vi phạm)**

**Mô tả**:
Cookie được khai báo là `"session"` và thực tế không có trường `expires` hoặc expires < 24h.

**Ví dụ**:

```python
ActualCookie(
    name="session_id",
    value="abc123",
    domain="example.com",
    expires=None,  # session cookie thực sự (hết khi đóng trình duyệt)
    secure=True,
    httpOnly=True,
    sameSite="Strict",
    thirdParties=[]
)
```

**Kết luận**: ✅ Không vi phạm

---

### ❌ **2. Use case vi phạm nhẹ (tồn tại 2 ngày)**

**Mô tả**:
Cookie được khai báo là `"Session"` nhưng `expires = now + 2 ngày` → sai định nghĩa "session" cookie.

```python
ActualCookie(
    name="session_id",
    value="abc123def456",
    domain="example.com",
    expires=datetime.now() + timedelta(days=3),
    secure=True,
    httpOnly=True,
    sameSite="Strict",
    thirdParties=[]
)
```

**Kết luận**: ❌ Vi phạm **Loại 1 – Specific Retention**
**Giải thích**: Session cookie nhưng tồn tại > 24h.

---

### ❌ **4. Cookie không được khai báo nhưng là session và tồn tại > 24h**

**Mô tả**:
Cookie **không có trong chính sách** nhưng được set kiểu session và tồn tại lâu.

```python
ActualCookie(
    name="tracker_session",
    value="track123456",
    domain="track.example.com",
    expires=datetime.now() + timedelta(days=3),
    secure=False,
    httpOnly=False,
    sameSite=None,
    thirdParties=["tracker.io"]
)
```

**Kết luận**: ❌ Vi phạm loại **"Undefined Retention"**, **không phải loại 1**
(Vì cookie **không có trong policy**)

---

### ✅ **5. Cookie khai báo `"13 months"` và thực tế đúng**

**Mô tả**:
Cookie `_ga` có thời gian lưu đúng như chính sách.

```python
ActualCookie(
    name="_ga",
    value="GA1.2.1234567890.1640995200",
    domain=".example.com",
    expires=datetime.now() + timedelta(days=395),  # Gần đúng với 13 tháng
    secure=True,
    httpOnly=False,
    sameSite="Lax",
    thirdParties=[]
)
```

**Kết luận**: ✅ Không vi phạm loại 1
(Mặc dù có thể vi phạm loại 2 nếu vượt quá 30%, nhưng không phải loại 1 vì không khai là `"session"`)

---

### Tổng kết kiểm tra loại 1:

| Cookie name     | Declared retention    | Thực tế expires          | Vi phạm loại 1?     | Ghi chú                               |
| --------------- | --------------------- | ------------------------ | ------------------- | ------------------------------------- |
| session\_id     | Session               | +2 days                  | ✅ Vi phạm           | Session nhưng sống > 24h              |
| session\_id     | Session               | None (phiên trình duyệt) | ❌ Không             | Session cookie chuẩn                  |
| \_ga            | 13 months             | +400 days                | ❌ Không             | Không khai là session                 |
| tracking\_pixel | Không có trong policy | +730 days                | ❌ Không (khác loại) | Không thuộc loại 1, mà là "undefined" |

---

✅ Nếu bạn muốn mình **viết luôn hàm kiểm tra loại vi phạm này** bằng Python (so sánh `declared_retention == "Session"` và `actual.expires > now + 24h`), mình có thể hỗ trợ ngay.
