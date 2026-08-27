from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st
APP_DIR=Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path: sys.path.insert(0,str(APP_DIR))
from components.ui import money,page_header  # noqa:E402
from services.model_service import load_assets,predict_one  # noqa:E402

st.set_page_config(page_title='Dự báo một căn nhà',page_icon='🔎',layout='wide')
page_header('🔎 Dự báo một căn nhà','Quick Input để demo; Full Input dùng toàn bộ schema huấn luyện.')
_,schema,_=load_assets(); field_map={f['name']:f for f in schema['fields']}

def field_input(field:dict,key_prefix:str):
    name=field['name']; label=field.get('label',name); unit=field.get('unit'); code=f"{name}"; help_text=field.get('description',label)+(f' ({unit})' if unit else '')+f' | mã kỹ thuật: {code}'
    if field['kind']=='category':
        options=field['options']; labels=field.get('option_labels',{})
        display=[f'{opt} — {labels.get(opt,opt)}' if labels.get(opt,opt)!=opt else opt for opt in options]
        idx=options.index(field['default']) if field['default'] in options else 0
        chosen=st.selectbox(label,display,index=idx,key=f'{key_prefix}_{name}',help=help_text)
        return options[display.index(chosen)]
    default=float(field['default']); lo=float(field['min']); hi=float(field['max']); integer_like=all(float(field[x]).is_integer() for x in ('min','max','default'))
    if integer_like: return st.number_input(label,min_value=int(lo),max_value=int(hi),value=int(default),step=1,key=f'{key_prefix}_{name}',help=help_text)
    return st.number_input(label,min_value=lo,max_value=hi,value=default,key=f'{key_prefix}_{name}',help=help_text)

quick_fields=['OverallQual','GrLivArea','Neighborhood','GarageCars','LotArea','TotalBsmtSF','1stFlrSF','YearBuilt','YearRemodAdd','FullBath','TotRmsAbvGrd','KitchenQual','ExterQual','GarageArea','Fireplaces']
defaults={f['name']:f['default'] for f in schema['fields']}
tab_quick,tab_full=st.tabs(['Quick Input','Full Input'])
with tab_quick:
    st.write('15 biến quan trọng được nhập trực tiếp; các biến còn lại dùng default tính **chỉ từ train** để phục vụ demo.')
    with st.form('quick_form'):
        cols=st.columns(3); values=defaults.copy()
        for i,name in enumerate(quick_fields):
            with cols[i%3]: values[name]=field_input(field_map[name],'quick')
        submitted=st.form_submit_button('Dự báo giá',use_container_width=True)
    if submitted:
        try:
            predicted=predict_one(values); st.success(f'Giá bán ước lượng: **{money(predicted)}**')
            st.caption('Đây là ước lượng học thuật trên Ames Housing; sai số có thể lớn hơn ở các trường hợp hiếm hoặc ngoài miền dữ liệu.')
        except Exception as exc: st.error(f'Không thể dự báo: {exc}')
with tab_full:
    st.warning('Biểu mẫu có 79 biến. Giá trị số được giới hạn theo miền quan sát trong train; category mới trong batch vẫn được encoder xử lý an toàn.')
    with st.form('full_form'):
        values={}; group_names=['General','Location/Lot','Building','Exterior','Basement','Rooms','Garage','Amenities','Sale information','Other']
        groups=[(g,[f for f in schema['fields'] if f.get('group','Other')==g]) for g in group_names]
        groups=[g for g in groups if g[1]]
        for gi,(group_name,group) in enumerate(groups,1):
            with st.expander(group_name,expanded=gi==1):
                cols=st.columns(2)
                for i,field in enumerate(group):
                    with cols[i%2]: values[field['name']]=field_input(field,'full')
        submitted_full=st.form_submit_button('Dự báo từ 79 biến',use_container_width=True)
    if submitted_full:
        try: st.success(f'Giá bán ước lượng: **{money(predict_one(values))}**')
        except Exception as exc: st.error(f'Không thể dự báo: {exc}')
