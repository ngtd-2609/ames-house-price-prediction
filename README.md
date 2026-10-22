# Dự báo giá nhà bằng Học máy

Bài tập lớn môn Học máy — Nhóm 5, Trường Công nghệ Thông tin Phenikaa. Giảng viên hướng dẫn: TS. Nguyễn Ngọc Giang.

Dự án dự báo `SalePrice` trên bộ dữ liệu House Prices – Ames Housing: phân tích dữ liệu, tiền xử lý, tạo đặc trưng, so sánh các thuật toán hồi quy và xây dựng ứng dụng Streamlit.

## Báo cáo và tài liệu

- [Báo cáo Học máy](reports/Bao_cao_Hoc_may.docx): bản Word định dạng theo mẫu, cập nhật ngày 21/10/2026.
- [Slide thuyết trình](slides/Slide_Hoc_may.pptx): 25 slide đã đồng bộ thông tin nhóm và giảng viên.
- [Sổ tay thuyết trình](docs/So_tay_thuyet_trinh_Hoc_may.docx): giải thích phương pháp, kết quả và câu hỏi thảo luận.
- Notebook: [Detailed](notebooks/House_Price_Prediction_Detailed.ipynb) và [Basic](notebooks/House_Price_Prediction_Basic.ipynb).
- [Phân công công việc](team/Phan_cong_cong_viec_4_thanh_vien.xlsx) và [biên bản họp](team/bien_ban_hop/).

Mã lớp học phần còn trống trong báo cáo và slide.

## Kết quả

Dữ liệu gồm 1.460 quan sát, chia cố định thành train 1.168 mẫu (80%), validation 146 mẫu (10%) và test 146 mẫu (10%). Đầu vào có 79 biến; bước feature engineering tạo thêm 15 đặc trưng trước mã hóa.

Chín thuật toán được khảo sát: Linear Regression, Ridge, ElasticNet, KNN, Decision Tree, Random Forest, Extra Trees, Gradient Boosting và HistGradientBoosting; Dummy median là mô hình cơ sở. Tuning được thực hiện cho Ridge và ElasticNet bằng CV 3 fold trên train. Mô hình cuối là **ElasticNet**, với `alpha=0.001` và `l1_ratio=0.2`.

| Chỉ số | Validation | Test |
|---|---:|---:|
| RMSE (USD) | 24,855.66 | 22,228.60 |
| MAE (USD) | 15,376.31 | 15,452.34 |
| R² | 0.9172 | 0.9076 |
| RMSLE | 0.1202 | 0.1177 |

Số liệu gốc nằm trong [outputs/summary.json](outputs/summary.json). Mô hình được chọn bằng validation/CV trước khi fit cuối trên train + validation và đánh giá test. Tiền xử lý nằm trong Pipeline; `Id` và `SalePrice` không được dùng làm đặc trưng.

## Cài đặt và chạy ứng dụng

Yêu cầu Python >=3.11; môi trường tạo mô hình dùng scikit-learn 1.8.0. Chạy các lệnh từ thư mục gốc của repo:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e .
python -m streamlit run app/Home.py
```

Trên Linux/macOS, kích hoạt môi trường bằng `source .venv/bin/activate`.

Ứng dụng hỗ trợ nhập nhanh 15 biến, nhập đủ 79 biến, dự báo hàng loạt qua CSV và xem thông tin mô hình. Dùng [house_input_sample.csv](data/house_input_sample.csv) làm tệp mẫu. Ứng dụng nạp mô hình đã huấn luyện từ `models/house_price_pipeline.joblib`.

## Kiểm thử và tái lập

```powershell
python -m pytest
python scripts/smoke_test.py
python scripts/generate_audit_evidence.py
```

Lệnh cuối chạy pytest kèm coverage cho `src/house_price` và `backend`, lưu kết quả trong `outputs/audit/`. Hướng dẫn chạy lại pipeline và notebook nằm trong [REPRODUCIBILITY.md](REPRODUCIBILITY.md).

Kết quả kiểm tra ngày 22/10/2026: **69 passed**, không có kiểm thử lỗi hoặc bị bỏ qua; source coverage **99.7%**.

## Cấu trúc

| Thư mục | Nội dung |
|---|---|
| `src/house_price/` | Đọc dữ liệu, tiền xử lý, đặc trưng, lựa chọn và đánh giá mô hình |
| `app/`, `backend/` | Giao diện Streamlit và dịch vụ dự báo |
| `data/` | Các tập train/validation/test và CSV mẫu |
| `models/` | Mô hình, schema đầu vào và metadata |
| `notebooks/` | Hai notebook thực nghiệm |
| `outputs/` | Kết quả, bảng, biểu đồ và kết quả kiểm thử |
| `reports/`, `slides/`, `docs/` | Báo cáo, slide và hướng dẫn |
| `scripts/`, `tests/` | Lệnh tái lập và bộ kiểm thử |
| `team/` | Phân công và biên bản họp |

## Giới hạn

Dữ liệu Ames mang tính lịch sử và địa phương, chưa có kiểm chứng trên thị trường khác. Ngân sách tuning còn nhỏ; CV RMSE biến động lớn và sai số tuyệt đối tăng ở nhóm nhà giá cao. Chưa có ablation cho từng đặc trưng hoặc khoảng dự báo cho từng căn nhà. Các cờ `Has*` hiện gộp số thiếu với không có tiện ích; cần thực nghiệm lại nếu thay đổi quy tắc này.

Kết quả phục vụ học tập. Trạng thái suy luận của ứng dụng cloud chưa được xác minh lại trong lần cập nhật này.

Thông tin chi tiết: [dữ liệu](DATA_CARD.md), [mô hình](MODEL_CARD.md), [kiến trúc](docs/ARCHITECTURE.md), [hướng dẫn demo](docs/DEMO_GUIDE.md), [triển khai](docs/DEPLOYMENT.md).

## Thành viên

| Họ và tên | MSSV |
|---|---|
| Nguyễn Tùng Dương | 24100358 |
| Đào Trọng Đức | 24107712 |
| Nguyễn Hưng Vũ | 24102769 |
| Nguyễn Anh Tuấn | 24100324 |
