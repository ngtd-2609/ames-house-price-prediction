# DEFENSE_QA.md - Câu hỏi phản biện và trả lời

## Dataset

### 1. Dataset đến từ đâu?

Dữ liệu project là Kaggle House Prices - Advanced Regression Techniques, được xây dựng từ Ames Housing. Bản project dùng ba split CSV nội bộ với tổng 1,460 dòng.

### 2. Vì sao là 1,460 dòng?

Đây là kích thước train.csv của Kaggle House Prices. Project chia lại thành 1,168 train, 146 validation và 146 test.

### 3. Ames Housing gốc và Kaggle khác nhau thế nào?

Ames Housing gốc rộng hơn; Kaggle cung cấp competition version phổ biến với 79 explanatory variables, Id và SalePrice. Project cần gọi đúng provenance để tránh mô tả sai.

### 4. Vì sao không đổi split?

Không đổi split để tránh cherry-pick metric. Split hiện tại được giữ cố định và checksum được ghi trong data_hashes.csv.

### 5. Vì sao giữ NA/None?

Trong các cột như GarageType hoặc PoolQC, NA có thể nghĩa là không có gara/hồ bơi. Nếu pandas tự chuyển thành NaN sẽ làm mất nghĩa domain.

## Leakage

### 6. Leakage là gì?

Leakage là việc thông tin không được phép, đặc biệt từ validation/test hoặc target, lọt vào quá trình fit/chọn model làm metric ảo tốt hơn.

### 7. Làm sao chứng minh test chưa được dùng để chọn model?

Quy trình ghi trong summary/model_selection_policy: benchmark và tuning dựa trên train/validation; test metrics chỉ được tính sau model lock.

### 8. Preprocessing fit ở đâu?

Imputer, scaler, encoder và estimator nằm trong sklearn Pipeline và fit trong quá trình train, không fit riêng trên validation/test.

### 9. Tại sao không fit scaler trên validation?

Validation đóng vai trò mô phỏng dữ liệu chưa thấy để chọn model. Fit scaler trên validation sẽ đưa phân phối validation vào pipeline và tạo leakage.

### 10. Id có được dùng làm feature không?

Không. Id bị loại khỏi X vì là định danh, không có ý nghĩa dự báo và có thể gây học giả tạo.

## Feature engineering

### 11. Vì sao có HouseAge?

Tuổi nhà tại thời điểm bán phản ánh mức cũ/mới của tài sản tốt hơn YearBuilt đơn lẻ trong một số quan hệ tuyến tính.

### 12. Vì sao TotalSF quan trọng?

TotalSF gộp diện tích tầng hầm, tầng 1 và tầng 2, đại diện tổng diện tích sử dụng chính.

### 13. Vì sao MoSold sin/cos?

Tháng bán là biến chu kỳ; tháng 12 và tháng 1 gần nhau. sin/cos biểu diễn chu kỳ tốt hơn số 1-12 thô.

### 14. Vì sao MSSubClass là categorical?

MSSubClass là mã loại nhà. Khoảng cách số học giữa các mã không có nghĩa liên tục, nên xử lý categorical hợp lý hơn.

### 15. Feature engineering có dùng target không?

Không. Các feature được tạo từ raw input từng dòng và không dùng SalePrice.

## Model

### 16. Model cuối là gì?

Model cuối theo summary.json là ElasticNet với params {'regressor__model__l1_ratio': 0.2, 'regressor__model__alpha': 0.001}.

### 17. Vì sao chọn model cuối?

Model được chọn bằng executable policy trước khi mở test: primary metric là validation RMSE; Ridge chỉ thắng trong tolerance 2% nếu CV RMSE mean không tệ hơn. CV std/overfit/deployability có thể được phân tích để thảo luận, nhưng không được mô tả như tiêu chí executable nếu code không dùng chúng.

### 18. Vì sao không chọn Ridge nếu ElasticNet tốt hơn?

Nếu final là ElasticNet, lý do là ElasticNet có validation RMSE tốt nhất và đáp ứng policy hiện tại; Ridge vẫn là benchmark quan trọng nhưng không được chọn cuối.

### 19. Vì sao không dùng Random Forest?

Random Forest có MAE tốt nhưng validation RMSE và overfit gap không tốt bằng final model trong protocol hiện tại.

### 20. Vì sao không dùng XGBoost?

XGBoost không nằm trong dependency pin chính thức; thêm model ngoài sklearn chỉ để cải thiện metric sẽ tăng rủi ro tái lập.

### 21. Overfitting được đánh giá thế nào?

Dựa trên train RMSE, validation RMSE, RMSE gap và CV behavior. Tree ensemble có train error quá thấp thường bị nghi overfit.

## Metrics and CV

### 22. RMSE là gì?

RMSE là căn bậc hai trung bình bình phương sai số, nhạy với lỗi lớn nên phù hợp khi sai số lớn cần bị phạt mạnh.

### 23. MAE khác RMSE thế nào?

MAE là sai số tuyệt đối trung bình, dễ diễn giải hơn và ít bị chi phối bởi outlier hơn RMSE.

### 24. R2 diễn giải thế nào?

R2 đo tỷ lệ phương sai target được giải thích bởi model trên tập đánh giá, không có nghĩa từng dự báo đúng theo phần trăm đó.

### 25. RMSLE dùng để làm gì?

RMSLE đo sai số theo tỷ lệ trên thang log, hữu ích khi giá nhà lệch phải và sai số tương đối quan trọng.

### 26. Vì sao dùng nhiều metric?

Một metric không phản ánh đủ: RMSE phạt outlier, MAE dễ hiểu, R2 đo giải thích phương sai, RMSLE xem sai số tương đối.

### 27. Vì sao CV std lớn?

Một số fold chứa nhà rất đắt/high leverage làm RMSE fold biến động. Project báo cáo thay vì giấu variance này.

### 28. Fold xấu có làm model sai không?

Không nhất thiết, nhưng nó cảnh báo dataset nhỏ và phân phối giá cao khó dự báo. Đây là limitation quan trọng.

## Explainability

### 29. Permutation importance hoạt động thế nào?

Nó xáo trộn từng feature và đo mức giảm performance; giảm nhiều nghĩa model phụ thuộc feature đó nhiều hơn trong dữ liệu đánh giá.

### 30. Vì sao cần nhiều repeats?

Một lần xáo trộn có nhiễu cao. Nhiều repeats giúp tính mean/std để importance đáng tin hơn.

### 31. Importance có phải causal không?

Không. Feature quan trọng với model không chứng minh nguyên nhân trong thế giới thực, đặc biệt khi các feature tương quan.

### 32. Top feature hiện là gì?

Top features trong bảng hiện gồm GrLivArea, OverallQual, Neighborhood, GarageCars, LotArea.

## Deployment

### 33. Artifact nhận raw input như thế nào?

Artifact bao gồm feature engineering và preprocessing nên backend chỉ cần truyền raw Ames-style DataFrame theo schema.

### 34. Unknown category xử lý ra sao?

OneHotEncoder dùng handle_unknown=ignore nên category mới không làm crash pipeline.

### 35. Missing column thì sao?

Backend batch phải báo lỗi thân thiện nếu thiếu required columns; single prediction dùng defaults từ schema khi phù hợp.

### 36. Extra column thì sao?

Backend không đưa extra columns vào model; batch output có thể giữ cột dư theo policy để người dùng đối chiếu.

### 37. Streamlit có retrain không?

Không. App chỉ load artifact đã train; retraining thuộc scripts/train_full_project.py.

### 38. Nếu Streamlit không chạy trong container thì sao?

Không được claim PASS. Ghi rõ thiếu executable và hướng dẫn cài requirements trên môi trường thật.

## Limitations

### 39. Model dùng ở Việt Nam được không?

Không nên dùng trực tiếp vì dữ liệu thuộc Ames/Iowa. Cần dữ liệu địa phương và kiểm định lại.

### 40. Dùng để định giá ngân hàng được không?

Không. Đây là đồ án học thuật/demo, không thay thế thẩm định chuyên nghiệp hoặc quyết định tín dụng.

### 41. Distribution shift là gì?

Là khi dữ liệu triển khai khác train data về địa lý, thời gian hoặc thị trường, làm performance suy giảm.

### 42. Hướng phát triển tiếp theo?

Có thể thêm dữ liệu mới, kiểm thử UI tự động, drift monitoring, SHAP, cloud deployment thật và logging predictions.



## Architecture refactor Q&A

### Vì sao phải refactor train_full_project.py?
Trước refactor, training script chứa trực tiếp EDA, tuning, final evaluation và explainability. Điều đó làm giảm tính tái sử dụng và khiến claim single source of truth chưa thuyết phục. Sau refactor, script chỉ điều phối, còn logic nằm trong `src/house_price` và được test riêng.

### Single source of truth nghĩa là gì trong project này?
Nghĩa là feature engineering, preprocessing, selection policy, diagnostics và artifact behavior không được copy rải rác trong notebook hay app. Notebook và scripts gọi lại module trong `src/house_price`; backend chỉ load canonical artifact.

### Làm sao chứng minh training script chỉ còn orchestration?
Mở `scripts/train_full_project.py`: file chỉ có `load_and_validate_project_data()` và `main()`. Test `test_training_script_is_orchestration_only_after_refactor` parse AST để đảm bảo không còn các hàm cũ như `create_eda`, `tune_candidates` hoặc `final_evaluation` trong script.

### Vì sao source coverage 99.7% không đồng nghĩa không có bug?
Coverage chỉ đo dòng code đã chạy, không đo chất lượng assertion. Vì vậy project bổ sung test có ý nghĩa: selection policy, leakage order, artifact raw input, diagnostics, consistency and backend errors. Coverage cao là bằng chứng hỗ trợ, không phải sự đảm bảo tuyệt đối.
