## 1. Collection: `users`

| Thuộc tính | Kiểu dữ liệu | Mô tả |
| --- | --- | --- |
| `_id` | `ObjectId` | Khóa chính, định danh duy nhất của người dùng |
| `email` | `String` | Email đăng nhập, phải là duy nhất trong hệ thống |
| `hashed_password` | `String` | Mật khẩu đã được mã hóa bằng thuật toán hash |
| `full_name` | `String` | Tên đầy đủ của người dùng |
| `role`  | `Enum<String>` | Vai trò: `admin`, `manager`, `provider` |
| `status` | `Enum<String>` | Trạng thái tài khoản: `pending`, `approved`, `rejected` |
| `created_at` | `DateTime` | Thời điểm tạo tài khoản |
| `updated_at` | `DateTime` | Thời điểm cập nhật thông tin lần cuối |

## 2. Collection: `websites`

| Thuộc tính | Kiểu dữ liệu | Mô tả |
| --- | --- | --- |
| `_id` | `ObjectId` | Khóa chính, định danh duy nhất của website |
| `domain` | `String` | Tên miền website, phải là duy nhất (ví dụ: "example.com") |
| `policy_url` | `String` | URL đầy đủ của trang chính sách cookie |
| `policy_status` | `String` | Trạng thái tìm kiếm chính sách: `found`, `not_found`, `error` |
| `provider_id` | `ObjectId` | ID của nhà cung cấp dịch vụ quản lý domain (tùy chọn) |
| `last_scanned_at` | `DateTime` | Thời điểm quét website lần cuối cùng |
| `found_method` | `Enum<String>`  | `LINK_TAG`, `FOOTER_LINK`, `NAVIGATION_LINK`, `BING_SEARCH`, `SITEMAP` |

## 3. Collection: `domain_requests`

| Thuộc tính | Kiểu dữ liệu | Mô tả |
| --- | --- | --- |
| `request_id` | `ObjectId` | Khóa chính, mã định danh duy nhất của yêu cầu |
| `requester_id` | `ObjectId` | Tham chiếu đến `users._id` - người gửi yêu cầu |
| `domains` | `Array<String>` | Danh sách tên miền cần đăng ký giám sát (tối đa 100 domain) |
| `reason` | `String` | Lý do và nguyện vọng đăng ký (10-1000 ký tự) |
| `status` | `Enum<String>` | Trạng thái yêu cầu: `pending`, `approved`, `rejected` |
| `created_at` | `DateTime` | Thời điểm tạo yêu cầu |
| `processed_by` | `ObjectId` | Tham chiếu đến `users._id` - admin xử lý (tùy chọn) |
| `processed_at` | `DateTime` | Thời điểm xử lý yêu cầu (tùy chọn) |
| `feedback` | `String` | Ghi chú/lý do của admin khi xử lý (bắt buộc nếu từ chối) |

## 4. Collection: `policy_contents`

| Thuộc tính | Kiểu dữ liệu | Mô tả |
| --- | --- | --- |
| `_id` | `ObjectId` | Khóa chính, định danh duy nhất của nội dung chính sách |
| `website_id` | `ObjectId` | Tham chiếu đến `websites._id` |
| `policy_url` | `String` | URL chính sách tại thời điểm trích xuất |
| `extracted_at` | `DateTime` | Thời điểm trích xuất nội dung |
| `original_content` | `String` | Nội dung văn bản gốc của chính sách cookie |
| `table_content` | `Array<Object>` | Nội dung dạng bảng đã được trích xuất và cấu trúc hóa |
| `translated_content` | `String` | Nội dung chính sách đã dịch sang tiếng Anh (tùy chọn) |
| `translated_table` | `Array<Object>` | Nội dung bảng đã dịch sang tiếng Anh (tùy chọn) |

## 5. Collection: `analysis_results`

| Thuộc tính | Kiểu dữ liệu | Mô tả |
| --- | --- | --- |
| `_id` | `ObjectId` | Khóa chính, định danh duy nhất của kết quả phân tích |
| `website_id` | `ObjectId` | Tham chiếu đến `websites._id` |
| `feature_id` | `ObjectId` | Tham chiếu đến `cookie_features._id` được sử dụng để so sánh |
| `analyzed_at` | `DateTime` | Thời điểm thực hiện phân tích |
| `summary` | `Object` | Tóm tắt kết quả phân tích (tổng số vi phạm, loại vi phạm) |
| `violations` | `Array<Object>` | Danh sách chi tiết các vi phạm được phát hiện |
| `actual_cookies` | `Array<Object>` | Danh sách cookie thực tế thu thập được khi quét website |

## 6. Collection: `cookie_features`

| Thuộc tính | Kiểu dữ liệu | Mô tả |
| --- | --- | --- |
| `_id` | `ObjectId` | Khóa chính, định danh duy nhất của đặc tả cookie |
| `content_id` | `ObjectId` | Tham chiếu đến `policy_contents._id` được phân tích |
| `analyzed_at` | `DateTime` | Thời điểm thực hiện phân tích bằng LLM |
| `is_specific` | `Integer` | Cờ cho biết chính sách có đặc tả cookie cụ thể (1=có, 0=không) |
| `cookies` | `Array<Object>` | Danh sách các cookie được đặc tả trong chính sách |

## Ghi chú về quan hệ giữa các Collection

- `users` ← `domain_requests.requester_id` & `domain_requests.processed_by`
- `users` ← `websites.provider_id`
- `websites` ← `policy_contents.website_id`
- `websites` ← `analysis_results.website_id`
- `policy_contents` ← `cookie_features.content_id`
- `cookie_features` ← `analysis_results.feature_id`
