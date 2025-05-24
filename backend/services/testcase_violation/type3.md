Dưới đây là các **use case kiểm tra vi phạm loại 3** theo đặc tả:

---

### 📌 **Vi phạm loại 3 – Specific – Retention**

> **Policy states short-term retention (e.g., "30 days"), but observed cookie is set to expire after 1 year.**
> 👉 So sánh giá trị `declared_retention` (ví dụ: `"30 days"`) với `expires` thực tế. Nếu thực tế vượt **365 ngày**, thì là vi phạm.

### ✅ Use Case 1 — Vi phạm (chính sách 30 ngày, thực tế 2 năm)

```python
# Policy
{
  "cookie_name": "short_term_cookie",
  "declared_retention": "30 days",
  ...
}

# Actual
ActualCookie(
    name="short_term_cookie",
    expires=datetime.now() + timedelta(days=730)  # 2 năm
)
```

👉 Vi phạm: chính sách khai 30 ngày, nhưng cookie tồn tại 730 ngày (> 365 ngày)

---

### ❌ Use Case 2 — Không vi phạm (chính sách 30 ngày, thực tế 45 ngày)

```python
# Actual
ActualCookie(
    name="short_term_cookie",
    expires=datetime.now() + timedelta(days=45)
)
```

👉 Không vi phạm: 45 ngày vẫn nằm trong mức chấp nhận.

---

### ❌ Use Case 4 — Không kiểm tra (không khai báo retention)

```python
# Policy
{
  "cookie_name": "no_retention_cookie",
  "declared_retention": null,
  ...
}
```

👉 Bỏ qua: không khai báo → không đủ dữ kiện để kiểm tra loại 3

---

### ✅ Use Case 5 — Chính sách “short-term” dưới dạng văn bản

```python
# Policy
{
  "cookie_name": "ambiguous_cookie",
  "declared_retention": "short-term",  # không parse được
}

# Actual
ActualCookie(
    name="ambiguous_cookie",
    expires=datetime.now() + timedelta(days=500)
)
```

👉 Nếu `strong_policy = True` → flag lỗi vì `declared_retention` không hợp lệ
