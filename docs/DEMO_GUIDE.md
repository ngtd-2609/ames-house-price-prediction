# Demo Guide - Dự báo giá nhà

## 1. Demo objective

Show that the project is not just a notebook: it includes a reproducible ML pipeline, a locked model, a deployable artifact, backend validation and a Streamlit interface.

## 2. Suggested 10-minute flow

| Time | Speaker action | Evidence/file |
|---:|---|---|
| 0-1 min | Giới thiệu bài toán và dataset | README, DATA_CARD |
| 1-2 min | Nói về split và leakage protocol | outputs/summary.json, report chapter 2 |
| 2-3 min | Mở EDA target/missingness | figures 01, 02 |
| 3-4 min | Giải thích feature engineering | outputs/tables/feature_engineering.csv |
| 4-5 min | Trình bày benchmark và model selection | validation_model_comparison.csv, tuning_results.csv |
| 5-6 min | Nêu final test metrics | outputs/summary.json |
| 6-8 min | Demo Streamlit quick/full prediction | app/Home.py |
| 8-9 min | Demo batch CSV | data/house_input_sample.csv |
| 9-10 min | Kết luận, limitations và Q&A | DEFENSE_QA.md |

## 3. Script nói ngắn

“Nhóm dùng dữ liệu Kaggle/Ames gồm 1,460 căn nhà. Mục tiêu không chỉ là dự báo giá mà còn xây dựng pipeline chống leakage. Train và validation được dùng để phát triển và chọn model. Test chỉ được mở sau khi model đã khóa. Artifact cuối là `models/house_price_pipeline.joblib` và model cuối là **ElasticNet** với test RMSE 22,228.60 USD. Sai số cao hơn ở nhóm nhà đắt, nên mô hình chỉ phù hợp học thuật/demo chứ không thay thế thẩm định chuyên nghiệp.”

## 4. Fallback nếu Streamlit chưa chạy

Nếu máy demo chưa cài Streamlit, chạy backend smoke test hoặc mở notebook Basic để chứng minh artifact load và predict raw input được. Không được nói UI đã PASS nếu chưa launch thật.

## 5. Câu hỏi phản biện nên chuẩn bị

Xem `DEFENSE_QA.md`. Các câu trả lời đã được viết riêng theo từng nhóm: dataset, leakage, feature engineering, model, metrics, CV, explainability, deployment và limitation.
