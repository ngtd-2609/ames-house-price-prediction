# Deployment Guide

## 1. Local deployment

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app/Home.py
```

Entry point: `app/Home.py`.

## 2. Required artifacts

- `models/house_price_pipeline.joblib`
- `models/input_schema.json`
- `models/model_metadata.json`
- `outputs/summary.json`

The app reads a pre-trained artifact. It must not retrain the model during serving.

## 3. Smoke test checklist

- App starts without traceback.
- Model artifact loads.
- Quick prediction returns a positive finite USD value.
- Full input form uses schema labels, defaults and min/max.
- Batch CSV download includes `PredictedSalePrice`.
- Model Information reads canonical metrics.

## 4. Streamlit Community Cloud

- Repository must include `requirements.txt`.
- Main file path: `app/Home.py`.
- No API keys or secrets are required.
- Ensure `models/house_price_pipeline.joblib` is committed or otherwise provided.

## 5. Common problems

| Problem | Cause | Fix |
|---|---|---|
| `streamlit: command not found` | Streamlit not installed | `pip install -r requirements.txt` |
| Missing artifact | Model file absent | Run training or restore `models/house_price_pipeline.joblib` |
| Unknown category | New categorical value | Pipeline uses `handle_unknown=ignore` |
| Missing required column in batch | CSV not matching schema | Use `data/house_input_sample.csv` |
| Version mismatch | Different Python/sklearn | Use Python >=3.11 and pinned requirements |

## 6. Current environment note

In the current container, Streamlit executable was unavailable, so UI launch is not marked PASS. This is documented rather than hidden.


## Current canonical model

Final model: **ElasticNet**. Metrics and artifact hash are read from `outputs/summary.json` and `models/model_metadata.json`.
