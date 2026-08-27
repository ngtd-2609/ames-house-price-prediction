# Backend

`service.py` là ranh giới backend phục vụ dự báo đơn và hàng loạt. Nó tải artifact trong `models/` và gọi lõi Machine Learning tại `src/house_price`. Backend không chứa widget Streamlit và không fit lại model khi nhận request.

Trong phiên bản môn học, Streamlit gọi trực tiếp service Python. Nếu phát triển thành hệ thống nhiều client, có thể bọc các hàm này bằng FastAPI mà không đổi pipeline.
