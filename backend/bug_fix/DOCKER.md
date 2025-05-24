#### ✅ 1. Kiểm tra MongoDB có đang chạy không

Chạy lệnh sau để kiểm tra:

```bash
sudo systemctl status mongod
```
Nếu chưa chạy, hãy khởi động nó:

```bash
sudo systemctl start mongod
```
---

#### ✅ 2. Kiểm tra MongoDB có đang lắng nghe trên `localhost:27017` không
Chạy:

```bash
netstat -tulnp | grep 27017
# hoặc nếu netstat không có:
ss -tuln | grep 27017
```

---
#### ✅ 3. Kiểm tra file cấu hình MongoDB (`/etc/mongod.conf`)

Mở file cấu hình:

```bash
sudo nano /etc/mongod.conf
```

Đảm bảo có:

```yaml
bindIp: 127.0.0.1
port: 27017
```

Sau đó khởi động lại MongoDB:

```bash
sudo systemctl restart mongod
```

---

#### ✅ 4. Kiểm tra bằng `mongo` shell (nếu cài)

```bash
mongo --host 127.0.0.1 --port 27017
```

Nếu vẫn không thể kết nối, thì có thể MongoDB đang bị lỗi khởi động hoặc cấu hình sai.

---

#### ✅ 5. Kiểm tra log của MongoDB

```bash
sudo journalctl -u mongod
```

hoặc:

```bash
cat /var/log/mongodb/mongod.log
```
---

### Nếu đang dùng Docker

Nếu MongoDB chạy trong container:
* Kiểm tra container có đang chạy:
  ```bash
  docker ps
  ```
* Nếu container MongoDB không expose port 27017 ra ngoài, bạn cần dùng `docker exec` hoặc sửa Docker Compose file để expose cổng.
---
