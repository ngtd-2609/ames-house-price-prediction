# OLD_VS_FINAL_CONTENT_AUDIT.md

## Summary

Bản cuối dùng bản BTL cũ làm chuẩn về độ đầy đủ tài liệu, đồng thời dùng bản kỹ thuật mới làm chuẩn về core ML, metric, model artifact và testing. Không copy nguyên văn các claim cũ về Ridge/metric/hash nếu không khớp canonical outputs.

| Hạng mục | Bản cũ đóng góp | Bản mới đóng góp | Quyết định cuối |
|---|---|---|---|
| README | Cấu trúc dài, workflow, app, deployment, troubleshooting | Metric/model/leakage mới | Khôi phục README chi tiết và thay bằng ElasticNet/metric mới |
| Report | Khung 30-40 trang, đủ chương học thuật | Core metric, figures, selection mới | Rebuild report chi tiết từ canonical outputs |
| PowerPoint | Flow 18-20 slide tốt hơn | Figures/metric/model mới | Rebuild 20 slide, không còn deck 8 slide |
| Demo guide | Timeline demo và Q&A | Trạng thái app/backend mới | Viết lại demo 10 phút theo ElasticNet |
| Deployment | Checklist local/cloud | Python >=3.11 và artifact mới | Viết lại deployment đầy đủ, không claim cloud PASS |
| Model card | Có ý tưởng mô tả model | ElasticNet, hash, metrics mới | Một canonical model card đồng bộ root/docs |
| Data card | Bản mới có nhưng quá ngắn | Data hashes, split, semantic missing | Mở rộng data card đầy đủ |
| Defense QA | Bản mới có file nhưng answers lặp | Evidence mới | Viết lại 42 câu trả lời riêng biệt |
| Testing | Bản cũ ít test hơn | Evidence cũ đã được loại khỏi canonical audit | Chỉ giữ evidence final có cấu trúc |
| Streamlit | Có cấu trúc app | Schema/UI labels mới | Ghi rõ backend OK, container thiếu streamlit executable |

## Removed from old content

- Claim model cuối là Ridge nếu canonical output là ElasticNet.
- Metric cũ, hash cũ, test count cũ.
- Các feature không tồn tại trong code.
- Tuyên bố Streamlit PASS nếu chưa launch thật trong môi trường kiểm định.

## Preserved/improved

- Flow README dài và dễ dùng.
- Báo cáo nhiều chương, có EDA, modeling, deployment, testing, limitation.
- Deck thuyết trình đủ 20 slide.
- Demo guide, deployment guide và Q&A bảo vệ.
