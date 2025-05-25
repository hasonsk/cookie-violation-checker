### 📌 **Vi phạm loại 4 – Specific – Third-party**

> **Cookie is sent to a third-party domain not listed in the `declared_third_parties` attribute.**
> 👉 So sánh `thirdParties` thực tế (tên miền bên thứ ba mà cookie gửi đến) với danh sách `"declared_third_parties"` trong policy. Nếu có tên miền không nằm trong danh sách khai báo, thì vi phạm.

---

## ✅ **Hàm kiểm tra gợi ý**

### ✅ Use Case 1 — Vi phạm: cookie gửi tới bên thứ ba không được khai báo

```python
# Policy
{
  "cookie_name": "_ga",
  "declared_third_parties": ["Google Analytics"]
}

# Actual
ActualCookie(
    name="_ga",
    thirdParties=["google-analytics.com", "doubleclick.net"]
)
```

👉 Vi phạm: `"doubleclick.net"` không được khai báo trong `declared_third_parties`.

---

### ❌ Use Case 2 — Không vi phạm: chỉ gửi tới bên đã khai báo

```python
# Actual
ActualCookie(
    name="_ga",
    thirdParties=["google-analytics.com"]
)
```

👉 Không vi phạm vì `"google-analytics.com"` khớp với `"Google Analytics"`

---

### ✅ Use Case 3 — Vi phạm: gửi đến facebook nhưng không khai báo

```python
# Policy
{
  "cookie_name": "pixel_cookie",
  "declared_third_parties": ["Meta"]
}

# Actual
ActualCookie(
    name="pixel_cookie",
    thirdParties=["facebook.com", "twitter.com"]
)
```

👉 Vi phạm: `"twitter.com"` không nằm trong `declared_third_parties`. Nếu `"Meta"` không bao hàm `"facebook"` → cũng vi phạm.

---

### ❌ Use Case 4 — Không kiểm tra: không có `thirdParties`

```python
# Actual
ActualCookie(
    name="strict_cookie",
    thirdParties=[]
)
```

👉 Không có gửi gì → không có gì để kiểm tra → bỏ qua.

---

### ✅ Use Case 5 — Vi phạm: khai báo bên thứ ba nhưng không khớp miền

```python
# Policy
{
  "cookie_name": "vendor_cookie",
  "declared_third_parties": ["VendorABC"]
}

# Actual
ActualCookie(
    name="vendor_cookie",
    thirdParties=["cdn.vendorabc.net", "ad.vendorabc.com"]
)
```

👉 Nếu dùng khớp gần (fuzzy match), `"vendorabc"` có thể chấp nhận. Nếu không rõ ràng → có thể vi phạm.

Bạn có muốn mình viết logic “fuzzy matching” nâng cao (ví dụ, ánh xạ `"Google Analytics"` với `"google-analytics.com"` hoặc `"Google"` với `"gstatic.com"`), hay giữ khớp theo từ khóa đơn giản?
