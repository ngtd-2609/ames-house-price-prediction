from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd
import streamlit as st
APP_DIR=Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path: sys.path.insert(0,str(APP_DIR))
from components.ui import page_header  # noqa:E402
from services.model_service import load_assets  # noqa:E402
st.set_page_config(page_title='Thông tin mô hình',page_icon='📊',layout='wide')
page_header('📊 Thông tin mô hình','Tất cả số liệu đọc trực tiếp từ outputs/summary.json.')
_,_,s=load_assets()
st.subheader('Giao thức thực nghiệm')
st.markdown('- Train 80%: fit, CV và tuning; validation 10%: so sánh quyết định; test 10%: đánh giá sau khi khóa model.\n- `Id` và `SalePrice` không đi vào X. `NA`/`None` có nghĩa nghiệp vụ được bảo toàn.\n- Artifact: **AmesFeatureEngineer → median/scaling + constant `Missing`/one-hot → log-target Ridge**.')
st.subheader('Validation / Test'); st.dataframe(pd.DataFrame([{'Split':'Validation',**s['validation_metrics']},{'Split':'Test',**s['test_metrics']}]),use_container_width=True,hide_index=True)
st.subheader('Độ ổn định cross-validation'); st.dataframe(pd.DataFrame([s['selected_model_cv_stability']]),use_container_width=True,hide_index=True)
st.caption('CV RMSE có độ lệch chuẩn lớn do một số căn nhà giá rất cao tạo high-leverage fold; vì vậy dự án báo cả MAE/RMSLE và phân tích lỗi, không chỉ một metric.')
st.subheader('So sánh validation'); st.dataframe(pd.DataFrame(s['ranked_models']),use_container_width=True,hide_index=True)
st.subheader('Permutation importance (diagnostic)'); imp=pd.DataFrame(s['top_features']).head(12); st.bar_chart(imp.set_index('Feature')['Importance_mean']); st.caption('Importance đo trên subset test diagnostic sau khi model đã khóa; không dùng để chọn model và có thể phụ thuộc tương quan giữa feature.')
st.subheader('Giới hạn'); st.warning('Ames là dữ liệu lịch sử tại một địa phương; chưa có lãi suất, biến vĩ mô, pháp lý hoặc tọa độ chi tiết. Sai số tuyệt đối tăng ở một số nhà giá cao.')
