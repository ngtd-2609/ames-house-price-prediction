from __future__ import annotations
import io,sys
from pathlib import Path
import pandas as pd
import streamlit as st
APP_DIR=Path(__file__).resolve().parents[1]; PROJECT_ROOT=APP_DIR.parent
if str(APP_DIR) not in sys.path: sys.path.insert(0,str(APP_DIR))
from components.ui import page_header  # noqa:E402
from services.model_service import load_assets,predict_batch  # noqa:E402

st.set_page_config(page_title='Dự báo hàng loạt',page_icon='📄',layout='wide')
page_header('📄 Dự báo hàng loạt','CSV phải có đủ 79 input feature; cột dư được giữ lại nhưng không đưa vào model.')
_,schema,_=load_assets(); required=[f['name'] for f in schema['fields']]
sample_path=PROJECT_ROOT/'data'/'house_input_sample.csv'
with sample_path.open('rb') as file: st.download_button('Tải CSV mẫu (không có SalePrice)',file.read(),sample_path.name,'text/csv')
uploaded=st.file_uploader('Chọn tệp CSV',type=['csv'])
if uploaded is not None:
    try:
        frame=pd.read_csv(uploaded,keep_default_na=False)
        missing=sorted(set(required)-set(frame.columns)); extra=sorted(set(frame.columns)-set(required)-{'Id','SalePrice'})
        c1,c2,c3=st.columns(3); c1.metric('Số dòng',len(frame)); c2.metric('Cột thiếu',len(missing)); c3.metric('Cột dư',len(extra))
        if not len(frame): st.error('CSV không có dòng dữ liệu.')
        if missing: st.error('Thiếu cột bắt buộc: '+', '.join(missing[:20])+(' ...' if len(missing)>20 else ''))
        if 'SalePrice' in frame.columns: st.warning('SalePrice sẽ bị loại trước khi dự báo để tránh dùng target làm input.')
        if extra: st.info('Cột dư được giữ ở output nhưng không đi vào model: '+', '.join(extra[:20]))
        if st.button('Chạy dự báo',type='primary',disabled=bool(missing) or frame.empty):
            result=predict_batch(frame); st.dataframe(result.head(20),width='stretch')
            buffer=io.StringIO(); result.to_csv(buffer,index=False)
            st.download_button('Tải kết quả',buffer.getvalue(),'house_predictions.csv','text/csv')
    except Exception as exc:
        st.error(f'Không thể xử lý CSV: {exc}')
