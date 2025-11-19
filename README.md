# 🐾 Animal Detection System

Hệ thống nhận diện động vật sử dụng YOLOv8 với giao diện web React và backend FastAPI.

## 📋 Mô Tả

Ứng dụng web cho phép người dùng upload ảnh và nhận diện 80 lớp động vật khác nhau sử dụng mô hình YOLOv8n đã được training. Hệ thống hiển thị kết quả với bounding boxes, thống kê chi tiết và cho phép tùy chỉnh các tham số detection.

**Kết quả:**
- mAP50: **0.7565** (75.65%)
- Precision: **0.7140**
- Recall: **0.7469**
- Cải thiện **+9.2%** so với baseline

## 🏗️ Cấu Trúc Dự Án

```
Animal-Detection-System-Data-Mining-Project/
├── backend/                      # FastAPI backend
│   ├── app.py                    # Main API application
│   ├── inference.py              # AnimalDetector class
│   └── requirements.txt          # Python dependencies
├── frontend/                     # React frontend
│   ├── src/
│   │   ├── components/           # React components
│   │   ├── services/             # API service
│   │   └── App.jsx               # Main app component
│   └── package.json              # Node dependencies
├── code_train_model/             # Training scripts
│   ├── data_preparation_pro.py   # Data preparation pipeline
│   ├── model_training_optimized.py
│   └── result_*.txt              # Training results
├── best.pt                       # Trained YOLOv8n model
├── BAO_CAO.md                    # Báo cáo đồ án
├── SLIDE_THUYET_TRINH.md         # Nội dung slide thuyết trình
├── start_backend.sh              # Script chạy backend
└── start_frontend.sh             # Script chạy frontend
```

## 🚀 Cài Đặt và Chạy

### Yêu Cầu Hệ Thống

- **Python**: 3.8+
- **Node.js**: 14+ (khuyến nghị 16+)
- **Model file**: `best.pt` (đã có sẵn)

### Cách 1: Sử dụng Scripts (Khuyến nghị)

**Terminal 1 - Backend:**
```bash
chmod +x start_backend.sh
./start_backend.sh
```

**Terminal 2 - Frontend:**
```bash
chmod +x start_frontend.sh
./start_frontend.sh
```

### Cách 2: Chạy Thủ Công

#### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Backend chạy tại: `http://localhost:8000`  
API docs: `http://localhost:8000/docs`

#### Frontend

```bash
cd frontend
npm install
npm start
```

Frontend tự động mở tại: `http://localhost:3000`

## 📖 Hướng Dẫn Sử Dụng

### 1. Upload Ảnh
- **Single**: Click "Select Single Image" hoặc drag & drop
- **Batch**: Click "Select Multiple Images" (tối đa 20 ảnh)

### 2. Điều Chỉnh Settings
- **Confidence Threshold** (0.0 - 1.0): Mặc định 0.25
- **IoU Threshold** (0.0 - 1.0): Mặc định 0.45

### 3. Nhận Diện
- Click "Detect" để bắt đầu
- Kết quả hiển thị:
  - Ảnh với bounding boxes
  - Bảng detections chi tiết (sortable)
  - Thống kê tổng hợp

### 4. Tính Năng Khác
- **Compare Thresholds**: So sánh kết quả với nhiều thresholds
- **Batch Navigation**: Sử dụng nút Previous/Next hoặc phím ← →
- **Keyboard Shortcuts**: Arrow keys để chuyển ảnh

## 🎯 Tính Năng

- ✅ Upload và preview ảnh (drag & drop)
- ✅ Nhận diện 80 lớp động vật với YOLOv8
- ✅ Hiển thị bounding boxes trên ảnh
- ✅ Bảng kết quả chi tiết (sortable)
- ✅ Thống kê tổng hợp (phân bố classes, confidence)
- ✅ Tùy chỉnh confidence và IoU thresholds
- ✅ So sánh kết quả với nhiều thresholds
- ✅ Batch processing (nhiều ảnh cùng lúc)
- ✅ Keyboard shortcuts (arrow keys)
- ✅ Giao diện responsive, dễ sử dụng

## 🔧 API Endpoints

### `GET /api/model-info`
Lấy thông tin model (số classes, danh sách classes, thresholds mặc định)

### `POST /api/detect`
Nhận diện động vật trong 1 ảnh

**Request:**
- `file`: File ảnh (multipart/form-data)
- `conf_threshold`: float (optional, default: 0.25)
- `iou_threshold`: float (optional, default: 0.45)

**Response:**
```json
{
  "success": true,
  "detections": [...],
  "image_base64": "data:image/jpeg;base64,...",
  "statistics": {...}
}
```

### `POST /api/detect-batch`
Nhận diện nhiều ảnh cùng lúc (tối đa 20 ảnh)

### `POST /api/compare-thresholds`
So sánh kết quả với các confidence threshold khác nhau

## 📊 Model Performance

### Metrics

| Metric | Giá trị |
|--------|---------|
| mAP50 | 0.7565 (75.65%) |
| mAP50-95 | 0.6322 (63.22%) |
| Precision | 0.7140 |
| Recall | 0.7469 |
| F1-Score | 0.7301 |

### Training Details

- **Model**: YOLOv8n (nano)
- **Dataset**: 28,184 samples (80 classes)
- **Train/Val**: 22,518 / 5,666 (80/20)
- **Epochs**: 100
- **Training time**: 8 giờ 21 phút
- **Hardware**: Tesla P100 GPU (16GB)

### Improvement

- **Baseline** (imbalanced data): mAP50 = 0.6925
- **After balancing**: mAP50 = 0.7565
- **Improvement**: **+9.2%** 🎉

## 📚 Tài Liệu

- **Báo cáo**: Xem file `BAO_CAO.md` để biết chi tiết về dự án
- **Slide thuyết trình**: Xem file `SLIDE_THUYET_TRINH.md` để có nội dung cho presentation

## 🐛 Troubleshooting

### Backend không chạy được
1. Kiểm tra Python version: `python3 --version` (cần 3.8+)
2. Kiểm tra model path trong `backend/app.py`
3. Kiểm tra dependencies: `pip install -r backend/requirements.txt`

### Frontend không kết nối được backend
1. Đảm bảo backend đang chạy tại `http://localhost:8000`
2. Kiểm tra CORS settings trong `backend/app.py`
3. Kiểm tra API URL trong `frontend/src/services/api.js`

### Model không load được
1. Kiểm tra file `best.pt` có tồn tại trong thư mục gốc
2. Kiểm tra đường dẫn `MODEL_PATH` trong `backend/app.py`

## 📝 Ghi Chú

- File upload được lưu tạm trong `backend/uploads/` và tự động xóa sau khi xử lý
- Model được load một lần khi khởi động backend
- Frontend sử dụng Tailwind CSS cho styling

## 📄 License

Dự án này được phát triển cho mục đích học tập và nghiên cứu.

---

**Sinh viên:** Phan Văn Tài - MSSV: 2202081  
**Giảng viên hướng dẫn:** Tiến sĩ Trần Ngọc Anh  
**Trường Đại học Tân Tạo - Khoa Công nghệ Thông tin**
