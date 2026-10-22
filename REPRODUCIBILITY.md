# Tái lập kết quả

Chạy từ thư mục gốc sau khi cài `requirements.txt` và `python -m pip install -e .`. Bộ mô hình hiện hành được tạo với Python 3.13.5, scikit-learn 1.8.0, pandas 2.2.3, numpy 2.3.5; `random_state=42`.

## Kiểm tra mô hình đã lưu

```powershell
python -m pytest
python scripts/smoke_test.py
python scripts/generate_audit_evidence.py
python scripts/check_project_consistency.py
```

Lệnh tạo bằng chứng chạy toàn bộ pytest với coverage trên `src/house_price` và `backend`. Các tệp `outputs/audit/test_summary.json` và `outputs/audit/coverage.json` ghi số kiểm thử và coverage thực tế; hai tệp `.txt` cùng thư mục lưu kết quả chạy chi tiết. Lệnh kiểm tra nhất quán đối chiếu mô hình, metadata, policy, notebook, báo cáo và slide với kết quả đã lưu.

Kiểm tra ngày 22/10/2026: **69 passed**, 0 failed, 0 skipped; source coverage **99.7%**.

## Huấn luyện lại

```powershell
python scripts/audit_data.py
python scripts/train_full_project.py
python scripts/build_metadata.py
python scripts/build_source_fingerprint.py
```

Các lệnh này ghi lại mô hình và kết quả trong `models/`, `outputs/`. Giữ nguyên ba tập CSV: chưa có script tái tạo bước chia ban đầu. Pipeline chỉ dùng train/validation để EDA, tuning và chọn mô hình; sau khi chốt mới đọc test để đánh giá cuối.

Nguồn đối chiếu:

- `outputs/summary.json`: mô hình ElasticNet, tham số và metric.
- `models/model_metadata.json`: metadata và SHA-256 của mô hình.
- `outputs/model_selection_policy.json`: tiêu chí lựa chọn, không dùng test.
- `outputs/tables/data_hashes.csv`: checksum các tập dữ liệu.
- `outputs/source_fingerprint.json`: checksum mã nguồn dùng trong notebook.

## Notebook

```powershell
python scripts/execute_notebooks.py
python scripts/build_notebook_summary.py
```

Chạy một notebook bằng `--only detailed` hoặc `--only basic`. Notebook dùng cùng môi trường Python đang gọi lệnh. Nếu cần tạo lại notebook từ mã nguồn, chạy `python scripts/build_notebooks.py` trước; lệnh này thay nội dung notebook hiện có.

## Báo cáo và slide

Bản hiện hành là `reports/Bao_cao_Hoc_may.docx` và `slides/Slide_Hoc_may.pptx`, cập nhật ngày 21/10/2026. Hai tài liệu được biên soạn từ kết quả thực nghiệm đã lưu, không phải một lần huấn luyện mới. Nếu huấn luyện lại, cần đối chiếu và cập nhật số liệu trong tài liệu trước khi sử dụng.
