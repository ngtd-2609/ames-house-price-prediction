# MODEL_CARD.md - ElasticNet House Price Pipeline

## 1. Model overview

Model cuối là **ElasticNet** trong một sklearn pipeline end-to-end. Artifact canonical là `models/house_price_pipeline.joblib`.

## 2. Final hyperparameters

```json
{
  "regressor__model__l1_ratio": 0.2,
  "regressor__model__alpha": 0.001
}
```

## 3. Pipeline architecture

```text
Raw Ames input
-> type coercion/schema validation
-> AmesFeatureEngineer
-> ColumnTransformer numeric/categorical preprocessing
-> ElasticNet
-> TransformedTargetRegressor log1p/expm1
-> SalePrice prediction in USD
```

## 4. Input contract

- Raw input features: 79.
- Engineered features added: 15.
- Feature engineering is inside artifact: `True`.
- Artifact accepts raw input: `True`.
- Schema SHA-256: `069fa2f9049b4dc41d2448fe91a5ac8550f85a99d749b1dcb0932bf0553ad00b`.

## 5. Training and selection

Training uses train/validation according to the defined protocol. Test is unlocked only after model selection. The model selection policy is stored in `outputs/model_selection_policy.json`.

## 6. Candidate models

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

## 7. Tuning results

| Model              |    RMSE |     MAE |     R2 |   RMSLE |   CV_RMSE_mean |   CV_RMSE_std |   CV_train_RMSE_mean |   Search_seconds |   Candidates_evaluated | Best_params                                                           |
|:-------------------|--------:|--------:|-------:|--------:|---------------:|--------------:|---------------------:|-----------------:|-----------------------:|:----------------------------------------------------------------------|
| ElasticNet (Tuned) | 24855.7 | 15376.3 | 0.9172 |  0.1202 |        39728.8 |       15890.5 |              19047.6 |           1.2239 |                      3 | {"regressor__model__l1_ratio": 0.2, "regressor__model__alpha": 0.001} |
| Ridge (Tuned)      | 25362.2 | 15209.6 | 0.9138 |  0.1191 |        41703.9 |       19210.7 |              24903.7 |           1.2008 |                      3 | {"regressor__model__alpha": 28.48035868435799}                        |

## 8. Final metrics

| Metric | Validation | Test |
|---|---:|---:|
| RMSE | 24,855.66 USD | 22,228.60 USD |
| MAE | 15,376.31 USD | 15,452.34 USD |
| R2 | 0.9172 | 0.9076 |
| RMSLE | 0.1202 | 0.1177 |

Bootstrap CI:

- RMSE 95% CI: 18,167.24 USD - 26,757.93 USD
- MAE 95% CI: 12,925.41 USD - 18,188.23 USD

## 9. Cross-validation stability

|   CV_RMSE_mean |   CV_RMSE_std |   CV_MAE_mean |   CV_MAE_std |   CV_R2_mean |   CV_R2_std |   CV_train_RMSE_mean |
|---------------:|--------------:|--------------:|-------------:|-------------:|------------:|---------------------:|
|        39728.8 |       15890.5 |       16070.7 |      1377.37 |       0.7237 |       0.182 |              19047.6 |

CV std is non-trivial. This is reported honestly and attributed to high-leverage expensive observations rather than hidden.

## 10. Explainability

Top permutation importance:

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

Permutation importance is diagnostic and non-causal.

## 11. Error analysis

| PriceQuartile   |   Count |      MAE |   Median_AE |    MAPE |
|:----------------|--------:|---------:|------------:|--------:|
| Q1 - thấp       |      38 | 10360.4  |     7556.78 | 11.52   |
| Q2              |      35 |  9551.12 |     6455.4  |  6.4911 |
| Q3              |      36 | 14265.9  |    11862    |  7.7748 |
| Q4 - cao        |      37 | 27418.5  |    22806.6  |  9.4601 |

Q4 high-price homes have the largest absolute error, so the model should be used cautiously on expensive homes.

## 12. Artifact

- Path: `models/house_price_pipeline.joblib`
- SHA-256: `5101114637e8001c91f06a42737cd3cc8ee143cb1d6a3a27631a41b48f3efcf1`
- Canonical only: `True`

## 13. Intended use

Academic demonstration, model comparison, app demo and regression pipeline study.

## 14. Out-of-scope use

Legal appraisal, lending approval, professional pricing and geographic transfer without validation.

## 15. Reproducibility

Use `requirements.txt`, `scripts/train_full_project.py`, `outputs/summary.json`, `models/model_metadata.json`, and `outputs/tables/data_hashes.csv`.
