# DATA_CARD.md - Kaggle/Ames House Price Dataset

## 1. Dataset summary

Project sử dụng 1,460 dòng từ Kaggle House Prices - Advanced Regression Techniques, một phiên bản competition dựa trên Ames Housing dataset. Dữ liệu gồm `Id`, 79 explanatory variables và target `SalePrice`.

## 2. Provenance

- Original domain: Ames, Iowa residential housing.
- Public competition version: Kaggle House Prices - Advanced Regression Techniques.
- Academic source context: Ames Housing dataset by Dean De Cock.
- Project version: ba file CSV đã chia sẵn trong thư mục `data/`.

## 3. Current split

| File | Rows/Columns | SHA-256 |
|---|---:|---|
| `data/house_train_80.csv` | [1168, 81] | `6af30124e1522a6b42806ebbfba4c88d938ed06b8fec98f9f8dbf3566a638c7a` |
| `data/house_validation_10.csv` | [146, 81] | `58828c452645ee3181c4035881ef3f0ff792fa8d4f01107e62778606807bd8c8` |
| `data/house_test_10.csv` | [146, 81] | `a0f077b3f09007424a3f819b2669c02aee3d2312be117b00451b3b686bdf4cfc` |


## 4. Target

`SalePrice` là giá bán nhà, đơn vị USD. Target lệch phải; skewness raw = 1.888, sau log1p = 0.168.

## 5. Feature categories

- Lot and location: `MSZoning`, `LotArea`, `Neighborhood`, `Condition1`, `Condition2`.
- Building quality and condition: `OverallQual`, `OverallCond`, `YearBuilt`, `YearRemodAdd`.
- Area and rooms: `GrLivArea`, `TotalBsmtSF`, `1stFlrSF`, `2ndFlrSF`, `TotRmsAbvGrd`.
- Basement, garage, exterior, utilities and sale information.

## 6. Missing values and semantic absence

Một số giá trị như `NA` trong các cột `Alley`, `GarageType`, `PoolQC` có thể biểu thị “không có tiện ích”, không phải lỗi thu thập. Loader giữ semantic absence thay vì để pandas tự chuyển thành NaN sai nghĩa.

Missing/absence top columns:

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

## 7. Integrity checks

- ID uniqueness được kiểm tra trong test/data audit.
- Không tự thay đổi split để cải thiện metric.
- Target không được đưa vào feature matrix.
- `MSSubClass` xử lý như categorical.

## 8. Intended use

- Học tập Machine Learning.
- Demo end-to-end regression pipeline.
- So sánh mô hình và error analysis.

## 9. Out-of-scope use

- Không dùng để thẩm định pháp lý.
- Không dùng cho ngân hàng hoặc giao dịch thật.
- Không áp dụng trực tiếp cho thị trường Việt Nam nếu chưa hiệu chỉnh dữ liệu.

## 10. Limitations and bias

Dữ liệu thuộc Ames/Iowa, số lượng mẫu chỉ 1,460 và có phân khúc giá cao khó dự báo hơn. Model có thể chịu distribution shift nếu dùng ở địa phương/thời gian khác.
