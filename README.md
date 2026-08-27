# Dự báo giá nhà bằng Machine Learning

Dự án Machine Learning end-to-end dự báo giá bán nhà trên bộ dữ liệu **Kaggle House Prices - Advanced Regression Techniques**, vốn được xây dựng từ Ames Housing dataset của Dean De Cock. Phiên bản cuối này được hợp nhất từ hai nguồn: bản BTL cũ có tài liệu học thuật đầy đủ và bản kỹ thuật mới có core ML, kiểm soát leakage, artifact, testing và audit tốt hơn.

> **Trạng thái hiện tại:** technical package đã được đồng bộ theo canonical outputs. Phần thông tin hành chính như tên nhóm, giảng viên, lớp học phần và thành viên vẫn cần người dùng điền trước khi nộp chính thức.

## Mục lục

1. [Kết quả chính](#1-kết-quả-chính)
2. [Bối cảnh và mục tiêu](#2-bối-cảnh-và-mục-tiêu)
3. [Dataset và provenance](#3-dataset-và-provenance)
4. [Chức năng sản phẩm](#4-chức-năng-sản-phẩm)
5. [Kiến trúc hệ thống](#5-kiến-trúc-hệ-thống)
6. [Workflow Machine Learning](#6-workflow-machine-learning)
7. [Chống data leakage](#7-chống-data-leakage)
8. [EDA](#8-eda)
9. [Feature engineering](#9-feature-engineering)
10. [Preprocessing](#10-preprocessing)
11. [Model benchmark và tuning](#11-model-benchmark-và-tuning)
12. [Model selection](#12-model-selection)
13. [Final evaluation](#13-final-evaluation)
14. [Explainability và error analysis](#14-explainability-và-error-analysis)
15. [Cấu trúc dự án](#15-cấu-trúc-dự-án)
16. [Cài đặt](#16-cài-đặt)
17. [Chạy pipeline, notebook và test](#17-chạy-pipeline-notebook-và-test)
18. [Chạy Streamlit](#18-chạy-streamlit)
19. [Reproducibility](#19-reproducibility)
20. [Deployment](#20-deployment)
21. [Deliverables](#21-deliverables)
22. [Troubleshooting](#22-troubleshooting)
23. [Limitations và future work](#23-limitations-và-future-work)
24. [Thông tin cần điền trước khi nộp](#24-thông-tin-cần-điền-trước-khi-nộp)

## 1. Kết quả chính

| Hạng mục | Giá trị |
|---|---|
| Model cuối | **ElasticNet** |
| Tham số cuối | `{'regressor__model__l1_ratio': 0.2, 'regressor__model__alpha': 0.001}` |
| Canonical artifact | `models/house_price_pipeline.joblib` |
| Model SHA-256 | `5101114637e8001c91f06a42737cd3cc8ee143cb1d6a3a27631a41b48f3efcf1` |
| Raw input features | 79 |
| Engineered features added | 15 |
| Test RMSE | **22,228.60 USD** |
| Test MAE | **15,452.34 USD** |
| Test R2 | **0.9076** |
| Test RMSLE | **0.1177** |
| Pytest | 67 passed |
| Source coverage (`src/house_price + backend`) | 99.9% |
| Streamlit in this container | NOT VERIFIED IN CONTAINER - streamlit executable not available |

| Metric | Validation | Test |
|---|---:|---:|
| RMSE | 24,855.66 USD | 22,228.60 USD |
| MAE | 15,376.31 USD | 15,452.34 USD |
| R2 | 0.9172 | 0.9076 |
| RMSLE | 0.1202 | 0.1177 |

Test chỉ được sử dụng sau khi model đã khóa. Những con số trên lấy từ `outputs/summary.json`, không phải gõ tay ở nhiều tài liệu riêng lẻ.

## 2. Bối cảnh và mục tiêu

Bài toán dự báo giá nhà là một bài toán hồi quy điển hình trong Machine Learning. Mục tiêu của đồ án không chỉ là đạt metric tốt, mà còn xây dựng một pipeline có thể tái lập, kiểm soát leakage, đóng gói model và đưa vào ứng dụng demo.

Các mục tiêu chính:

- Hiểu cấu trúc dữ liệu nhà ở và biến mục tiêu `SalePrice`.
- Phân tích EDA, missingness, correlation, categorical effects và outlier.
- Xây dựng feature engineering có ý nghĩa với domain nhà ở.
- So sánh nhiều thuật toán hồi quy bằng cùng protocol.
- Khóa model trước khi mở test.
- Đánh giá model cuối bằng RMSE, MAE, R2, RMSLE, bootstrap CI, residual và error analysis.
- Đóng gói artifact end-to-end nhận raw input.
- Tạo backend và Streamlit app cho quick input, full input, batch prediction và model information.

## 3. Dataset và provenance

Dự án sử dụng 1,460 quan sát từ Kaggle House Prices - Advanced Regression Techniques, một phiên bản competition phổ biến được xây dựng từ Ames Housing dataset. Dữ liệu có `Id`, 79 explanatory variables và target `SalePrice`.

| Split | Shape | Vai trò |
|---|---:|---|
| Train | [1168, 81] | Fit preprocessing/model, CV và tuning theo protocol |
| Validation | [146, 81] | So sánh model và quyết định model lock |
| Test | [146, 81] | Đánh giá cuối sau khi model đã khóa |

`split_origin_reproducible = False`. Vì vậy project không tự ý đổi split để làm metric đẹp hơn.

### Data hashes

| file                         |   bytes | sha256                                                           |
|:-----------------------------|--------:|:-----------------------------------------------------------------|
| data/house_train_80.csv      |  369865 | 6af30124e1522a6b42806ebbfba4c88d938ed06b8fec98f9f8dbf3566a638c7a |
| data/house_validation_10.csv |   46936 | 58828c452645ee3181c4035881ef3f0ff792fa8d4f01107e62778606807bd8c8 |
| data/house_test_10.csv       |   47057 | a0f077b3f09007424a3f819b2669c02aee3d2312be117b00451b3b686bdf4cfc |

## 4. Chức năng sản phẩm

### 4.1. Quick Prediction

Người dùng nhập nhóm biến quan trọng như `OverallQual`, `GrLivArea`, `GarageCars`, `TotalBsmtSF`, `YearBuilt`, `Neighborhood`. Các biến còn lại được điền bằng default từ schema huấn luyện. Chế độ này phù hợp để demo nhanh và giảm gánh nặng nhập đủ 79 biến.

### 4.2. Full Input

Người dùng có thể nhập đầy đủ 79 biến raw theo `models/input_schema.json`. Schema đã có friendly label, group semantic, unit, min/max, default và category options.

### 4.3. Batch Prediction

Người dùng tải lên CSV. Backend kiểm tra thiếu cột, sai kiểu, file rỗng và cột target. Output giữ các cột hợp lệ và bổ sung `PredictedSalePrice`.

### 4.4. Model Information

Trang model information đọc metric từ canonical source, trình bày model cuối, hash artifact, feature importance, limitation và cảnh báo học thuật.

## 5. Kiến trúc hệ thống

```text
User
  -> Streamlit UI
  -> backend/service.py
  -> src/house_price prediction utilities
  -> models/house_price_pipeline.joblib
  -> PredictedSalePrice
```

Training architecture:

```text
Raw CSV
  -> data validation
  -> EDA outputs
  -> AmesFeatureEngineer
  -> ColumnTransformer
  -> ElasticNet
  -> TransformedTargetRegressor log1p/expm1
  -> canonical artifact
```

`src/house_price` là nguồn logic chính. Notebook, script training, backend và app không nên copy lại feature engineering hoặc preprocessing.

## 6. Workflow Machine Learning

```text
Data validation
-> EDA trên train/validation được phép
-> Feature engineering
-> Preprocessing pipeline
-> Baseline và model candidates
-> Tuning/CV
-> Model selection
-> MODEL LOCK
-> TEST UNLOCK
-> Final evaluation
-> Artifact + app
```

## 7. Chống data leakage

Các nguyên tắc:

- Không dùng `SalePrice` test trước model lock.
- Không dùng test metric để chọn model.
- `Id` và `SalePrice` bị loại khỏi feature matrix.
- Feature engineering là row-wise, không fit thống kê từ validation/test.
- Imputer, scaler, encoder và estimator nằm trong sklearn Pipeline.
- Test chỉ dùng cho final evaluation, diagnostic và explainability sau khi model đã khóa.

## 8. EDA

Target `SalePrice` lệch phải, log1p giúp giảm skewness từ 1.888 xuống 0.168. Một số biến tương quan cao với giá gồm:

| Feature      |   Correlation_with_SalePrice |
|:-------------|-----------------------------:|
| OverallQual  |                       0.7903 |
| GrLivArea    |                       0.7052 |
| GarageCars   |                       0.6377 |
| GarageArea   |                       0.6084 |
| TotalBsmtSF  |                       0.5994 |
| 1stFlrSF     |                       0.598  |
| FullBath     |                       0.5531 |
| TotRmsAbvGrd |                       0.5179 |
| YearRemodAdd |                       0.5138 |
| YearBuilt    |                       0.5123 |
| GarageYrBlt  |                       0.4815 |
| Fireplaces   |                       0.4619 |

Missingness/semantic absence nổi bật:

| Column       |   Missing_or_absence_count |   Missing_or_absence_pct |
|:-------------|---------------------------:|-------------------------:|
| PoolQC       |                       1161 |                  99.4    |
| MiscFeature  |                       1125 |                  96.32   |
| Alley        |                       1095 |                  93.75   |
| Fence        |                        943 |                  80.74   |
| MasVnrType   |                        693 |                  59.33   |
| FireplaceQu  |                        555 |                  47.52   |
| LotFrontage  |                        212 |                  18.15   |
| GarageQual   |                         63 |                   5.3938 |
| GarageFinish |                         63 |                   5.3938 |
| GarageType   |                         63 |                   5.3938 |
| GarageYrBlt  |                         63 |                   5.3938 |
| GarageCond   |                         63 |                   5.3938 |

Các hình chính nằm ở `outputs/figures/01_target_distribution.png` đến `outputs/figures/06_split_distribution_check.png`.

## 9. Feature engineering

- `HouseAge`: Tuổi nhà tại thời điểm bán. Công thức: `YrSold - YearBuilt`.
- `RemodAge`: Tuổi từ lần cải tạo. Công thức: `YrSold - YearRemodAdd`.
- `GarageAge`: Tuổi gara. Công thức: `YrSold - GarageYrBlt`.
- `TotalSF`: Tổng diện tích sàn. Công thức: `TotalBsmtSF + 1stFlrSF + 2ndFlrSF`.
- `TotalBathrooms`: Tổng phòng tắm quy đổi. Công thức: `Full + 0.5 Half + basement`.
- `TotalPorchSF`: Không gian hiên. Công thức: `Tổng 5 loại hiên/sàn`.
- `TotalOutdoorSF`: Không gian ngoài trời. Công thức: `TotalPorchSF + PoolArea`.
- `HasGarage/HasBsmt/HasFireplace/HasPool/Has2ndFloor/HasMasVnr`: Có/không tiện ích. Công thức: `Cờ 0/1`.
- `MoSold_sin/cos`: Mã hóa chu kỳ tháng. Công thức: `sin/cos(2π MoSold/12)`.

Không trình bày các feature không tồn tại như `IsRemodeled`, `TotalRooms`, `GarageAreaPerCar`, `LivLotRatio`, `SeasonSold`.

## 10. Preprocessing

- Numeric: median imputation và scaling khi phù hợp.
- Categorical: impute true missing thành `Missing`, semantic absence token như `NA`/`None` được giữ khi có nghĩa trong data dictionary.
- Encoding: OneHotEncoder với `handle_unknown="ignore"`.
- Target: log1p khi huấn luyện và expm1 khi dự báo.
- Artifact cuối nhận raw 79 feature và tự thực hiện feature engineering + preprocessing + prediction.

## 11. Model benchmark và tuning

| Model                         |   Train_RMSE |   Validation_RMSE |     MAE |   Validation_R2 |   RMSLE |   RMSE_gap |   Dummy_improvement_pct |
|:------------------------------|-------------:|------------------:|--------:|----------------:|--------:|-----------:|------------------------:|
| ElasticNet                    |   20829.2    |           24855.7 | 15376.3 |          0.9172 |  0.1202 |    4026.48 |                   71.95 |
| Ridge                         |   22597.6    |           25213.2 | 15384.6 |          0.9148 |  0.1212 |    2615.6  |                   71.55 |
| LinearRegression              |   16531.4    |           26276.9 | 16712.4 |          0.9075 |  0.1542 |    9745.5  |                   70.35 |
| ExtraTreesRegressor           |       0      |           26552.1 | 16503.2 |          0.9056 |  0.1404 |   26552.1  |                   70.04 |
| RandomForestRegressor         |   12994.7    |           27861.1 | 14376.9 |          0.896  |  0.12   |   14866.3  |                   68.56 |
| DecisionTreeRegressor         |   21878.5    |           31457.9 | 22219.6 |          0.8674 |  0.1707 |    9579.45 |                   64.5  |
| KNeighborsRegressor           |       0.0032 |           34184.2 | 19291.9 |          0.8435 |  0.1537 |   34184.2  |                   61.42 |
| HistGradientBoostingRegressor |   31298      |           36644.3 | 18140.2 |          0.8201 |  0.1415 |    5346.35 |                   58.65 |
| GradientBoostingRegressor     |   46569.1    |           53014.2 | 27105.1 |          0.6235 |  0.2117 |    6445.1  |                   40.17 |
| DummyRegressor (median)       |   81264.5    |           88612.2 | 58271.2 |         -0.0519 |  0.4178 |    7347.67 |                    0    |

Tuning results:

| Model              |    RMSE |     MAE |     R2 |   RMSLE |   CV_RMSE_mean |   CV_RMSE_std |   CV_train_RMSE_mean |   Search_seconds |   Candidates_evaluated | Best_params                                                           |
|:-------------------|--------:|--------:|-------:|--------:|---------------:|--------------:|---------------------:|-----------------:|-----------------------:|:----------------------------------------------------------------------|
| ElasticNet (Tuned) | 24855.7 | 15376.3 | 0.9172 |  0.1202 |        39728.8 |       15890.5 |              19047.6 |           1.2239 |                      3 | {"regressor__model__l1_ratio": 0.2, "regressor__model__alpha": 0.001} |
| Ridge (Tuned)      | 25362.2 | 15209.6 | 0.9138 |  0.1191 |        41703.9 |       19210.7 |              24903.7 |           1.2008 |                      3 | {"regressor__model__alpha": 28.48035868435799}                        |

## 12. Model selection

Model cuối: **ElasticNet**.

Lý do chọn:

- Primary metric executable: validation RMSE.
- Ridge chỉ được ưu tiên khi nằm trong tolerance 2% so với best validation RMSE và `CV_RMSE_mean` không tệ hơn.
- Test không tham gia selection; deployability/interpretability chỉ là cân nhắc định tính sau khi model đã được khóa.
- Quyết định khóa trước khi mở test.
- Không dùng test metric làm tiêu chí chọn model.

CV stability của model cuối:

|   CV_RMSE_mean |   CV_RMSE_std |   CV_MAE_mean |   CV_MAE_std |   CV_R2_mean |   CV_R2_std |   CV_train_RMSE_mean |
|---------------:|--------------:|--------------:|-------------:|-------------:|------------:|---------------------:|
|        39728.8 |       15890.5 |       16070.7 |      1377.37 |       0.7237 |       0.182 |              19047.6 |

CV std còn khá lớn do dữ liệu nhà đắt/high-leverage observations; vì vậy tài liệu không gọi model là “ổn định tuyệt đối”, mà chỉ đánh giá theo trade-off thực nghiệm.

## 13. Final evaluation

| Metric | Validation | Test |
|---|---:|---:|
| RMSE | 24,855.66 USD | 22,228.60 USD |
| MAE | 15,376.31 USD | 15,452.34 USD |
| R2 | 0.9172 | 0.9076 |
| RMSLE | 0.1202 | 0.1177 |

Bootstrap CI 95%:

- RMSE: 18,167.24 USD - 26,757.93 USD
- MAE: 12,925.41 USD - 18,188.23 USD
- Bootstrap samples: 300

## 14. Explainability và error analysis

Permutation importance:

| Feature      |   Importance_mean |   Importance_std |   Repeats |   Sample_size |
|:-------------|------------------:|-----------------:|----------:|--------------:|
| GrLivArea    |           9910.12 |          1840.31 |        20 |            50 |
| OverallQual  |           8734.33 |          2375.29 |        20 |            50 |
| Neighborhood |           5256.71 |          2250.6  |        20 |            50 |
| GarageCars   |           3076.45 |          1148.8  |        20 |            50 |
| LotArea      |           2269.53 |          1749.56 |        20 |            50 |
| YearBuilt    |           1777.64 |          1522.11 |        20 |            50 |
| KitchenQual  |           1730.04 |           419.12 |        20 |            50 |
| TotalBsmtSF  |           1321.19 |           620.2  |        20 |            50 |
| YearRemodAdd |            762.1  |           571.38 |        20 |            50 |
| GarageArea   |            699.45 |           338.41 |        20 |            50 |
| 2ndFlrSF     |            607.39 |           329.23 |        20 |            50 |
| 1stFlrSF     |            604.13 |           338.36 |        20 |            50 |

Sai số theo price quartile:

| PriceQuartile   |   Count |      MAE |   Median_AE |    MAPE |
|:----------------|--------:|---------:|------------:|--------:|
| Q1 - thấp       |      38 | 10360.4  |     7556.78 | 11.52   |
| Q2              |      35 |  9551.12 |     6455.4  |  6.4911 |
| Q3              |      36 | 14265.9  |    11862    |  7.7748 |
| Q4 - cao        |      37 | 27418.5  |    22806.6  |  9.4601 |

Nhận xét: nhóm Q4 giá cao có MAE lớn nhất, cho thấy model còn khó với phân khúc bất động sản đắt hoặc có đặc điểm hiếm. Permutation importance dùng để hỗ trợ giải thích mô hình, không phải causal inference.

## 15. Cấu trúc dự án

```text
BTL_DuDoanGiaNha_ULTIMATE_Final/
├── app/                 # Streamlit multipage app
├── backend/             # Service layer cho prediction/batch
├── data/                # Train/validation/test và CSV mẫu
├── docs/                # Architecture, deployment, demo, model card...
├── models/              # Canonical artifact + schema + metadata
├── notebooks/           # Detailed và Basic notebooks
├── outputs/             # Figures, tables, summary, audit logs
├── reports/             # DOCX/PDF report
├── scripts/             # Training, build, audit, notebook execution
├── slides/              # PowerPoint final
├── src/house_price/     # Core ML logic
├── team/                # File phân công bị khóa, không sửa
└── tests/               # Pytest suite
```

## 16. Cài đặt

Yêu cầu Python: **>=3.11**.

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## 17. Chạy pipeline, notebook và test

```bash
python scripts/audit_data.py
python scripts/train_full_project.py
python scripts/build_metadata.py
python scripts/execute_notebooks.py
coverage erase
coverage run --source=src/house_price,backend -m pytest
coverage report -m
```

Kết quả kiểm thử canonical gần nhất: **67 passed, source coverage 99.9%** trên phạm vi `src/house_price + backend`. Evidence máy đọc nằm tại `outputs/audit/test_summary.json` và `outputs/audit/coverage.json`.

## 18. Chạy Streamlit

```bash
streamlit run app/Home.py
```

Trong container kiểm định hiện tại, executable `streamlit` không có sẵn nên UI launch chưa được xác minh tại đây. Tuy nhiên package đã khai báo `streamlit>=1.40,<2` trong `requirements.txt`, backend và smoke tests đã được kiểm tra. Khi chạy trên máy thật, cần cài requirements trước rồi launch command trên.

## 19. Reproducibility

Các nguồn tái lập:

- `outputs/summary.json`: nguồn metric canonical.
- `models/model_metadata.json`: metadata artifact.
- `outputs/model_selection_policy.json`: policy chọn model.
- `outputs/tables/data_hashes.csv`: checksum dữ liệu.
- `scripts/train_full_project.py`: orchestration training.
- `scripts/build_report.py` và `scripts/build_slides.py`: rebuild DOCX/PDF/PPTX từ canonical outputs.

## 20. Deployment

Triển khai local:

1. Clone/unzip project.
2. Tạo virtual environment.
3. Cài `requirements.txt`.
4. Kiểm tra `models/house_price_pipeline.joblib` tồn tại.
5. Chạy `streamlit run app/Home.py`.
6. Test quick prediction và batch CSV.

Triển khai Streamlit Cloud cần khai báo đúng entrypoint `app/Home.py`, không upload secrets, không train model trong app.

## 21. Deliverables

- README.md
- DATA_CARD.md
- MODEL_CARD.md
- REPRODUCIBILITY.md
- docs/ARCHITECTURE.md
- docs/DEMO_GUIDE.md
- docs/DEPLOYMENT.md
- DEFENSE_QA.md
- notebooks Detailed + Basic
- reports DOCX/PDF
- slides PPTX
- canonical model artifact
- outputs summary/tables/figures/audit

## 22. Troubleshooting

| Vấn đề | Cách xử lý |
|---|---|
| `streamlit: command not found` | Chạy `pip install -r requirements.txt` trong đúng venv |
| Batch CSV thiếu cột | Dùng `data/house_input_sample.csv` làm template |
| Category lạ | Pipeline dùng `handle_unknown="ignore"`, không crash |
| Metric không khớp docs | Chạy `python scripts/check_project_consistency.py` |
| Notebook stale | Chạy lại `python scripts/train_full_project.py` rồi execute notebooks |
| Report/slide cũ | Chạy `python scripts/build_report.py` và `python scripts/build_slides.py` |

## 23. Limitations và future work

- Dataset thuộc Ames/Kaggle, không đại diện cho mọi thị trường bất động sản.
- Không dùng model cho định giá pháp lý, thẩm định ngân hàng hoặc quyết định tài chính thật.
- Sai số cao hơn ở phân khúc giá cao.
- CV std còn lớn do một số fold chứa căn nhà đắt/high leverage.
- Future work: cập nhật dữ liệu mới, thêm SHAP nếu phù hợp, deploy cloud thật, logging drift, kiểm thử UI bằng Playwright/Selenium.

## 24. Thông tin cần điền trước khi nộp

- Tên nhóm: `[CẦN CUNG CẤP]`
- Giảng viên: `[CẦN CUNG CẤP]`
- Lớp học phần: `[CẦN CUNG CẤP]`
- Thành viên và mã sinh viên: `[CẦN CUNG CẤP]`
- Tỷ lệ đóng góp: `[CẦN CUNG CẤP]`

Không tự bịa thông tin hành chính.


## Architecture refactor verification

The final architecture separates scientific logic from orchestration. `scripts/train_full_project.py` is now an orchestration entry point of about 145 lines with only `load_and_validate_project_data()` and `main()`. Reusable logic lives in `src/house_price`:

- `eda.py`: train/validation EDA only; no test target before model lock.
- `tuning.py`: validation benchmark and RandomizedSearchCV tuning.
- `selection.py`: executable `ModelSelectionPolicy` and `select_final_model()`.
- `diagnostics.py`: final post-lock test diagnostics and error tables.
- `explainability.py`: post-lock permutation importance with 20 repeats.
- `reporting.py`: summary, hashes, feature table, CV stability and artifact output.

Architecture tests in `tests/test_architecture_refactor.py` assert that the training script no longer defines the old large scientific functions and imports the refactored modules instead.
