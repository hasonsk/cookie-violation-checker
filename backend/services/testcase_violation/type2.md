Dưới đây là **các use case kiểm tra vi phạm loại 2** (`Specific – Retention`):

> **Loại 2**: Thời gian sống thực tế của cookie **vượt quá thời gian khai báo trong chính sách > 30%**.

## ⚙️ **Tiêu chí kiểm tra**:

* Tính phần trăm chênh lệch giữa:

  \frac{{\text{{actual_retention}} - \text{{declared_retention}}}}{{\text{{declared_retention}}}} > 30\%
---

### ✅ **1. Use case hợp lệ (không vi phạm, đúng 13 tháng)**

**Chính sách**:

```json
{
  "cookie_name": "_ga",
  "declared_retention": "13 months"
}
```

**Cookie thực tế**:

```python
ActualCookie(
    name="_ga",
    expires=datetime.now() + timedelta(days=395)  # ~13 tháng
)
```

**Kết luận**: ✅ Không vi phạm
**Giải thích**: Thời gian đúng với chính sách khai báo.

---

### ❌ **2. Vi phạm nhẹ (17 tháng thay vì 13 tháng)**

**Thực tế**:

```python
ActualCookie(
    name="_ga",
    expires=datetime.now() + timedelta(days=517)  # ~17 tháng
)
```

**Tính toán**:

* Declared: 13 tháng ≈ 395 ngày
* Actual: 517 ngày
* Tăng: (517 - 395) / 395 ≈ **30.8%**

**Kết luận**: ❌ Vi phạm loại 2
**Giải thích**: Thời gian thực tế vượt quá 30% so với khai báo.

---
### ✅ **4. Không vi phạm (kém hơn khai báo)**

```python
ActualCookie(
    name="_ga",
    expires=datetime.now() + timedelta(days=300)  # Chỉ ~10 tháng
)
```

**Tính toán**:

* 300 < 395 ⇒ Không vi phạm
  **Kết luận**: ✅ Không vi phạm

---

### ✅ **5. Không vi phạm với biên sai nhỏ (<30%)**

```python
ActualCookie(
    name="_ga",
    expires=datetime.now() + timedelta(days=460)  # ~15 tháng
)
```

**Tính toán**:

* (460 - 395) / 395 = \~16.5%
  **Kết luận**: ✅ Không vi phạm

### ✅ **7. Cookie `"session"` thì bỏ qua**

**Chính sách**:

```json
{
  "cookie_name": "session_id",
  "declared_retention": "Session"
}
```

```python
ActualCookie(
    name="session_id",
    expires=datetime.now() + timedelta(days=1)
)
```
