from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st
APP_DIR=Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path: sys.path.insert(0,str(APP_DIR))
from components.ui import money,page_header  # noqa:E402
from services.model_service import load_assets  # noqa:E402
st.set_page_config(page_title='Dự báo giá nhà',page_icon='🏠',layout='wide')
_,_,summary=load_assets(); metrics=summary['test_metrics']; model_name=summary['selected_model']
page_header('🏠 Hệ thống dự báo giá nhà Ames',f'Demo Machine Learning end-to-end: raw input → feature engineering → preprocessing → {model_name} → SalePrice.')
c1,c2,c3,c4=st.columns(4); c1.metric('Mô hình',f"{summary['selected_model']} tuned"); c2.metric('Test RMSE',money(metrics['RMSE'])); c3.metric('Test MAE',money(metrics['MAE'])); c4.metric('Test R²',f"{metrics['R2']:.4f}")
st.markdown('''### Cách sử dụng
1. **Dự báo một căn nhà**: Quick Input hoặc Full Input.
2. **Dự báo hàng loạt**: dùng CSV mẫu đủ 79 feature và tải kết quả.
3. **Thông tin mô hình**: xem protocol, metric, CV, error analysis và giới hạn.''')
st.success(f'Artifact đã lưu là pipeline end-to-end: feature engineering + preprocessing + log-target {model_name}. Ứng dụng chỉ load và predict, không retrain.')
st.warning('Mô hình phục vụ học tập trên Ames Housing lịch sử, không phải công cụ thẩm định bất động sản chính thức.')
