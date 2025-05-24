## 📌 **Vi phạm loại 8 – General – Purpose**

> **"Observed cookie name shows no semantic similarity with any general-purpose label declared in the policy (e.g., cosine similarity < 0.5)."**

* So sánh **ngữ nghĩa tên cookie thực tế** (`cookie.name`) với **danh sách các mục đích khai báo** trong `declared_purpose` của policy.
* Nếu **độ tương đồng cosine < 0.5** giữa tên cookie và nhãn mục đích => Không khớp về ngữ nghĩa → Vi phạm.

---

## 🧠 **Hàm xử lý gợi ý (mô phỏng cosine similarity)**

Dùng `sentence-transformers` hoặc `sklearn TfidfVectorizer + cosine_similarity`.

--> Bổ sung giải thích lý do.

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def _check_low_similarity_cookie_name(
    self, actual_cookie: ActualCookie, declared_policy_cookies: List[PolicyCookie]
):
    cookie_name = actual_cookie.name.lower()

    # So sánh với tất cả nhãn declared_purpose trong policy
    for policy_cookie in declared_policy_cookies:
        purpose = policy_cookie.declared_purpose.lower()

        vectorizer = TfidfVectorizer().fit([cookie_name, purpose])
        vectors = vectorizer.transform([cookie_name, purpose])
        sim_score = cosine_similarity(vectors[0], vectors[1])[0][0]

        if sim_score < 0.5:
            self._log_violation(
                type="General",
                category="Purpose",
                cookie_name=actual_cookie.name,
                severity="Medium",
                detail=(
                    f"Observed cookie name '{actual_cookie.name}' shows low semantic similarity "
                    f"(cosine={sim_score:.2f}) with declared purpose label '{purpose}'."
                )
            )
```

### ✅ Use Case 1 – Cookie tên “xyz\_uid” nhưng chính sách khai là “Analytical”

```python
# Actual cookie
ActualCookie(
    name="xyz_uid",
    value="abc123",
    domain=".example.com",
    expires=datetime.now() + timedelta(days=365),
    third_party_requests=[]
)

# Policy cookie
PolicyCookie(
    cookie_name="xyz_uid",
    declared_purpose="Analytical",
    declared_retention="13 months",
    declared_third_parties=["First Party"],
    declared_description="Used for analytical tracking of user behavior"
)
```

* Độ tương đồng giữa `xyz_uid` và `"analytical"` < 0.5 → Vi phạm.

---

### ✅ Use Case 2 – Cookie tên “clicktrack” nhưng khai là “Strictly Necessary”

```python
ActualCookie(name="clicktrack", value="...", ...)
PolicyCookie(cookie_name="clicktrack", declared_purpose="Strictly Necessary", ...)
```

* `"clicktrack"` thiên về hành vi người dùng → không khớp với `"Strictly Necessary"` → Vi phạm ngữ nghĩa.

---

### ✅ Use Case 3 – Cookie “ga\_qs” nhưng khai là “Performance”

```python
ActualCookie(name="ga_qs", ...)
PolicyCookie(cookie_name="ga_qs", declared_purpose="Performance", ...)
```

* `"ga_qs"` thường dùng cho Google Analytics → không khớp rõ ràng với `"Performance"` nếu không có ngữ cảnh rõ ràng → độ tương đồng thấp → Cần ghi rõ hơn trong mô tả.

---

### ✅ Use Case 4 – Cookie tên khó hiểu, khai là “Advertising”

```python
ActualCookie(name="a1b2c3x", ...)
PolicyCookie(cookie_name="a1b2c3x", declared_purpose="Advertising", ...)
```

* Tên cookie không gợi lên mục đích quảng cáo → cosine < 0.5 → Vi phạm.

---

### ❌ Use Case 5 – Cookie tên “analytics\_user” khai là “Analytical”

```python
ActualCookie(name="analytics_user", ...)
PolicyCookie(cookie_name="analytics_user", declared_purpose="Analytical", ...)
```

* Có độ tương đồng cao → cosine > 0.7 → Không vi phạm.

---

### ✅ Use Case 6 – Cookie “px\_id” khai là “Security”

```python
ActualCookie(name="px_id", ...)
PolicyCookie(cookie_name="px_id", declared_purpose="Security", ...)
```

* `"px_id"` thường là tracker → cosine với `"security"` thấp → Vi phạm.

---

Bạn muốn mình đóng gói các use case vi phạm này thành một bảng tổng hợp (ví dụ CSV/Pandas) để tích hợp vào hệ thống báo cáo không?
