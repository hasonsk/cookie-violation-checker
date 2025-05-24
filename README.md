# cookie-violation-checker

### Lộ trình triển khai:
```shell
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```
1. Bắt đầu với việc thiết lập cấu trúc dự án cơ bản
2. Triển khai từng module core theo thứ tự trong hướng dẫn
3. Tích hợp các module lại với nhau thông qua API
4. Phát triển Chrome Extension để thu thập dữ liệu
5. Kiểm thử và tài liệu hóa

Tổng thời gian ước tính: 4-6 tuần cho một developer, với phương pháp tiếp cận từng bước rõ ràng.

Giải pháp này vẫn giữ được tất cả các chức năng cốt lõi của hệ thống ban đầu, nhưng được đơn giản hóa để một người có thể quản lý và triển khai. Bạn cũng có thể dễ dàng mở rộng thành kiến trúc microservices trong tương lai nếu cần thiết.
