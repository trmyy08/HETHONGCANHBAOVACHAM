# Nhóm 13 – Hệ thống mô phỏng cảnh báo va chạm

**Đề tài 36 – Mô phỏng hệ thống cảnh báo va chạm**

## 1. Giới thiệu

Hệ thống mô phỏng cảnh báo nguy cơ va chạm phía trước xe, sử dụng Python, hệ chuyên gia dựa trên luật IF–THEN và Logic mờ để phân tích dữ liệu giao thông, đánh giá mức độ nguy hiểm và đưa ra cảnh báo cho người lái xe.

Project cung cấp giao diện Web Dashboard giúp theo dõi, mô phỏng, kiểm tra kết quả suy diễn và trực quan hóa dữ liệu.

## 2. Chức năng

- **Tổng quan:** Hiển thị thông tin và trạng thái hệ thống.
- **Mô phỏng:** Thực hiện các kịch bản giao thông.
- **Suy diễn luật:** Phân tích dữ liệu đầu vào và xác định mức cảnh báo.
- **Cơ sở luật:** Hiển thị tập luật IF–THEN của hệ thống.
- **Trực quan hóa:** Hiển thị khoảng cách, tốc độ, TTC và biểu đồ kết quả.

## 3. Công nghệ sử dụng

| Công nghệ | Mục đích |
|---|---|
| Python 3.11 | Xây dựng thuật toán và hệ thống |
| FastAPI | Xây dựng Backend và API |
| NumPy | Tính toán dữ liệu |
| Matplotlib | Vẽ biểu đồ |
| HTML, CSS, JavaScript | Xây dựng giao diện Web |
| Docker | Đóng gói môi trường chạy |
| Docker Compose | Quản lý và khởi chạy hệ thống |

## 4. Cấu trúc dự án

CollisionWarningSystem/
├── src/               
├── tests/              
├── web/                 
├── data/              
├── results/              
├── web_app.py       
├── requirements.txt      
├── Dockerfile           
├── docker-compose.yml  
└── README.md           
## 5. Hướng dẫn chạy chương trình

### Yêu cầu

- Windows 10/11
- Docker Desktop đã cài đặt và đang hoạt động

### Khởi chạy

Mở Terminal tại thư mục chứa file `docker-compose.yml` và chạy:

```bash
docker compose up --build
```

Sau khi hệ thống khởi động thành công, truy cập website:

**http://localhost:8000**

### Các lệnh Docker thường dùng

| Lệnh | Chức năng |
|---|---|
| `docker compose up --build` | Build và chạy hệ thống |
| `docker compose up -d` | Chạy hệ thống ở chế độ nền |
| `docker compose logs -f` | Theo dõi nhật ký hoạt động |
| `docker compose restart` | Khởi động lại hệ thống |
| `docker compose down` | Dừng hệ thống |

## 6. Quy trình hoạt động

1. Tiếp nhận hoặc tạo dữ liệu cảm biến mô phỏng.
2. Tính toán khoảng cách, tốc độ tương đối và TTC.
3. Lưu trữ các dữ kiện trong bộ nhớ làm việc (Working Memory).
4. Đối chiếu dữ kiện với các luật IF–THEN trong cơ sở luật.
5. Thực hiện suy diễn và xác định mức độ nguy hiểm.
6. Hiển thị kết quả cảnh báo và giải thích trên giao diện.

## 7. Các mức cảnh báo

| Mức | Ý nghĩa |
|---|---|
| SAFE | Tình huống an toàn |
| WARNING | Có nguy cơ va chạm, cần chú ý |
| DANGER | Nguy cơ va chạm cao |

## 8. Kiểm thử

Chạy các bài kiểm thử bên trong Docker:

```bash
docker compose exec collision-warning python -m unittest discover -s tests -v
```
