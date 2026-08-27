# Frontend

Frontend Streamlit nằm tại `app/` vì Streamlit yêu cầu `Home.py` và thư mục `pages/` theo quy ước multipage. Thư mục này đánh dấu ranh giới giao diện: form nhập nhanh, form 79 biến, upload/download CSV và trang thông tin mô hình.

Frontend chỉ gọi `backend.service`; không chứa feature engineering, preprocessing hay huấn luyện.
