Dưới đây là danh sách **tài liệu cần thiết** cho quá trình phát triển và hoàn thiện dự án **PDCA Progress Manager** (hệ thống theo dõi tiến độ cá nhân dựa trên PDCA), triển khai trên **Web + Mobile App**.

---

## 📁 1. **Tài liệu định hướng và yêu cầu dự án**

| Tên tài liệu             | Mục đích                                                     |
| ------------------------ | ------------------------------------------------------------ |
| `01_Project_Vision.md`   | Mô tả mục tiêu, tầm nhìn, vấn đề giải quyết                  |
| `02_User_Personas.md`    | Chân dung người dùng mục tiêu (student, developer, coach...) |
| `03_Use_Cases.md`        | Danh sách các Use Case + input/output                        |
| `04_Feature_List.xlsx`   | Bảng tổng hợp các tính năng và trạng thái phát triển         |
| `05_Roadmap_Timeline.md` | Giai đoạn phát triển theo tuần/tháng                         |

---

## 🧠 2. **Thiết kế chức năng và trải nghiệm người dùng**

| Tên tài liệu                  | Mục đích                                               |
| ----------------------------- | ------------------------------------------------------ |
| `06_Wireframes.fig`           | Bản phác họa giao diện bằng Figma                      |
| `07_UX_Flowchart.png`         | Sơ đồ luồng chuyển đổi màn hình                        |
| `08_Component_Diagram.drawio` | Sơ đồ các thành phần React, cấu trúc liên kết          |
| `09_Data_Model_Specs.md`      | Thiết kế schema cho Goal, Challenge, UserProfile...    |
| `10_Permission_Matrix.md`     | Bảng quyền (đặc biệt nếu có Coach/Viewer mode sau này) |

---

## ⚙️ 3. **Tài liệu kỹ thuật**

| Tên tài liệu                  | Mục đích                                             |
| ----------------------------- | ---------------------------------------------------- |
| `11_Architecture_Overview.md` | Clean Architecture / Monorepo cấu trúc               |
| `12_API_Contracts.yaml`       | Swagger / OpenAPI định nghĩa endpoint                |
| `13_Firebase_Config.md`       | Hướng dẫn cấu hình Auth, Firestore, Rules            |
| `14_AI_Service_Guide.md`      | Cách kết nối API Gemini/OpenAI                       |
| `15_CI_CD_Setup.md`           | Thiết lập Github Actions hoặc Vercel, Expo EAS build |

---

## 📱 4. **Tài liệu dành cho frontend & UX**

| Tên tài liệu                 | Mục đích                                                       |
| ---------------------------- | -------------------------------------------------------------- |
| `16_UI_Style_Guide.md`       | Màu sắc, font, button, spacing chuẩn toàn hệ thống             |
| `17_Component_Library.md`    | Các component tái sử dụng được (Button, Modal, Card...)        |
| `18_Responsiveness_Specs.md` | Thiết kế responsive theo screen size (Mobile, Tablet, Desktop) |

---

## 📊 5. **Tài liệu phân tích & đo lường**

| Tên tài liệu                | Mục đích                                                               |
| --------------------------- | ---------------------------------------------------------------------- |
| `19_KPI_Success_Metrics.md` | Chỉ số đánh giá hiệu quả hệ thống (retention, goal completion rate...) |
| `20_User_Feedback_Log.xlsx` | Ghi nhận phản hồi từ người dùng thực tế                                |
| `21_Bug_Tracker.md`         | Ghi lỗi và tình trạng fix                                              |

---

## 📝 6. **Tài liệu vận hành và mở rộng**

| Tên tài liệu             | Mục đích                                     |
| ------------------------ | -------------------------------------------- |
| `22_Deployment_Guide.md` | Hướng dẫn deploy web/mobile                  |
| `23_Team_Onboarding.md`  | Dành cho dev mới tham gia dự án              |
| `24_Security_Policy.md`  | Bảo mật Firebase, kiểm soát quyền truy cập   |
| `25_Scalability_Plan.md` | Mở rộng hệ thống cho hàng nghìn user nếu cần |

---

Nếu bạn muốn mình tạo sẵn các **template cho từng tài liệu** (ví dụ: wireframe template, `UserProfile` schema bằng Markdown, hay Figma layout chuẩn), chỉ cần nói nhé. Mình cũng có thể tạo file Notion hoặc Git repo tổ chức tài liệu nếu bạn dùng hệ thống quản lý tài liệu.
