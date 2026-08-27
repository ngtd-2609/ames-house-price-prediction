const pptxgen = require('pptxgenjs');
const fs = require('fs');
const path = require('path');
const root = process.cwd();
const summary = JSON.parse(fs.readFileSync(path.join(root,'outputs/summary.json'),'utf8'));
const testEvidence = JSON.parse(fs.readFileSync(path.join(root,'outputs/audit/test_summary.json'),'utf8'));
const coverageEvidence = JSON.parse(fs.readFileSync(path.join(root,'outputs/audit/coverage.json'),'utf8'));
const coverageDisplay = Number(coverageEvidence.display_coverage).toFixed(1)+'%';
const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'House Price ML Team';
pptx.subject = 'Ultimate Ames House Price Prediction';
pptx.title = 'Dự báo giá nhà bằng Machine Learning';
pptx.company = 'Phenikaa University';
pptx.lang = 'vi-VN';
pptx.theme = { headFontFace:'Aptos Display', bodyFontFace:'Aptos', lang:'vi-VN', themeColors:[{name:'accent1',color:'1F4E79'},{name:'accent2',color:'70AD47'},{name:'accent3',color:'ED7D31'}] };
const W=13.333, H=7.5; let n=1; const total=20;
function fmt(x,d=2){ return Number(x).toLocaleString('en-US',{maximumFractionDigits:d,minimumFractionDigits:d}); }
function img(rel){ return path.join(root, rel); }
function title(slide, t, st){ slide.background={color:'F8FBFD'}; slide.addText(t,{x:0.55,y:0.32,w:12.1,h:0.38,fontFace:'Aptos Display',fontSize:23,bold:true,color:'1F4E79',margin:0}); if(st) slide.addText(st,{x:0.58,y:0.78,w:11.9,h:0.28,fontSize:10.2,color:'666666',margin:0}); slide.addShape(pptx.ShapeType.line,{x:0.55,y:1.12,w:12.1,h:0,line:{color:'D9EAF7',width:1}}); }
function foot(slide){ slide.addText(`${n++} / ${total}`,{x:12.05,y:7.08,w:0.75,h:0.16,fontSize:7.5,color:'888888',align:'right',margin:0}); }
function bullets(slide, arr, x,y,w,h,fs=14){ slide.addText(arr.map(a=>({text:a,options:{bullet:{indent:12},hanging:4}})),{x,y,w,h,fontSize:fs,color:'222222',breakLine:false,fit:'shrink',valign:'mid'}); }
function addImg(slide, rel, x,y,w,h){ if(fs.existsSync(img(rel))) slide.addImage({path:img(rel),x,y,w,h,sizing:{type:'contain',x,y,w,h}}); }
function metric(slide,label,value,x,y,w){ slide.addText(label,{x,y,w,h:0.18,fontSize:8,color:'666666',align:'center',margin:0}); slide.addText(value,{x,y:y+0.22,w,h:0.34,fontSize:17,bold:true,color:'1F4E79',align:'center',margin:0}); }
function notes(slide, body, sources){ slide.addNotes(`${body}\n\n[Sources]\n${sources.map(s=>'- '+s).join('\n')}\n[/Sources]`); }

let s = pptx.addSlide();
s.background={color:'F8FBFD'};
s.addText('Dự báo giá nhà\nbằng Machine Learning',{x:0.75,y:1.08,w:7.2,h:1.35,fontFace:'Aptos Display',fontSize:36,bold:true,color:'1F4E79',margin:0,breakLine:false});
s.addText('Kaggle/Ames Housing • Pipeline end-to-end • '+summary.selected_model,{x:0.78,y:2.75,w:7.6,h:0.3,fontSize:15,color:'444444',margin:0});
s.addText('Giảng viên/Lớp/Nhóm/Thành viên: CẦN CUNG CẤP trước khi nộp',{x:0.78,y:3.25,w:7.8,h:0.3,fontSize:11,color:'AA0000',margin:0});
addImg(s,'outputs/figures/13_deployment_architecture.png',7.2,1.35,5.4,2.25);
s.addText('Thông điệp: nội dung đầy đủ như bản cũ, core kỹ thuật dùng bản mới.',{x:7.4,y:4.05,w:5.0,h:0.7,fontSize:14,bold:true,color:'1F4E79',align:'center'});
foot(s); notes(s,'Mở đầu bằng mục tiêu hợp nhất: giữ chiều sâu học thuật nhưng dùng core kỹ thuật mới nhất.', ['README.md','outputs/summary.json']);

s=pptx.addSlide(); title(s,'1. Mục tiêu và phạm vi','Không chỉ tối ưu metric mà xây dựng project ML hoàn chỉnh.');
bullets(s,['Dự báo SalePrice từ 79 thuộc tính raw của Kaggle/Ames.','Kiểm soát leakage và khóa model trước khi mở test.','So sánh nhiều mô hình hồi quy trong cùng pipeline.','Đóng gói artifact, backend, Streamlit và tài liệu bảo vệ.'],0.75,1.5,5.8,3.8,16);
metric(s,'Test RMSE',fmt(summary.test_metrics.RMSE)+' USD',7.0,1.6,2.6); metric(s,'Test MAE',fmt(summary.test_metrics.MAE)+' USD',9.9,1.6,2.6); metric(s,'Test R²',summary.test_metrics.R2.toFixed(4),8.4,2.75,2.6);
foot(s); notes(s,'Nhấn mạnh đồ án có đủ research notebook, code package, artifact, app demo, report và slide.', ['README.md','reports/Bao_cao_Du_bao_Gia_nha_Hoan_chinh.docx']);

s=pptx.addSlide(); title(s,'2. Dataset provenance','Phân biệt Kaggle House Prices với Ames Housing gốc.');
bullets(s,[`Tổng số dòng: ${summary.dataset.total_rows}.`,`Train: ${summary.dataset.train_shape[0]}, Validation: ${summary.dataset.validation_shape[0]}, Test: ${summary.dataset.test_shape[0]}.`,`Raw input features: ${summary.dataset.input_features_raw}.`,`Không đổi split để làm metric đẹp hơn.`],0.75,1.55,4.65,3.5,16);
addImg(s,'outputs/figures/06_split_distribution_check.png',5.55,1.35,6.9,4.7);
foot(s); notes(s,'Giải thích dataset là Kaggle competition version dựa trên Ames; split hiện tại được giữ cố định.', ['DATA_CARD.md','outputs/tables/data_hashes.csv','outputs/summary.json']);

s=pptx.addSlide(); title(s,'3. Data integrity','Kiểm tra dữ liệu trước khi modeling.');
bullets(s,['ID duy nhất và không dùng làm feature.','Target không bị đưa vào X.','MSSubClass xử lý như categorical.','Semantic absence như NA/None được bảo toàn khi có nghĩa domain.'],0.85,1.65,5.2,3.35,16);
addImg(s,'outputs/figures/02_missingness_top20.png',6.45,1.35,5.9,4.75);
foot(s); notes(s,'Missingness không chỉ là dữ liệu thiếu; nhiều cột biểu thị không có tiện ích.', ['outputs/tables/missingness_top20.csv','DATA_CARD.md']);

s=pptx.addSlide(); title(s,'4. EDA target','SalePrice lệch phải nên log-target là hợp lý.');
addImg(s,'outputs/figures/01_target_distribution.png',0.75,1.35,7.1,4.8);
metric(s,'Raw skew',summary.target_stats.skewness.toFixed(3),8.4,1.65,3.4); metric(s,'Log1p skew',summary.target_stats.log1p_skewness.toFixed(3),8.4,2.65,3.4);
s.addText('Target transformer dùng log1p khi fit và expm1 khi predict.',{x:8.4,y:3.75,w:3.55,h:0.8,fontSize:14,bold:true,color:'1F4E79',align:'center'});
foot(s); notes(s,'Không nói log-target là hướng phát triển vì kỹ thuật này đã được dùng trong pipeline.', ['outputs/figures/01_target_distribution.png','outputs/summary.json']);

s=pptx.addSlide(); title(s,'5. EDA features','Correlation dùng để hiểu dữ liệu, không diễn giải nhân quả.');
addImg(s,'outputs/figures/03_top_numeric_correlations.png',0.75,1.35,5.7,4.75);
addImg(s,'outputs/figures/05_categorical_relationships.png',6.65,1.35,5.8,4.75);
foot(s); notes(s,'Nêu OverallQual, GrLivArea, Neighborhood nổi bật nhưng tránh kết luận causal.', ['outputs/tables/numeric_correlations.csv','outputs/figures/05_categorical_relationships.png']);

s=pptx.addSlide(); title(s,'6. Leakage protocol','Test chỉ được mở sau khi model đã khóa.');
bullets(s,['Train/validation dùng cho EDA, benchmark, CV và tuning.','Model selection dựa trên policy, không dùng test metric.','MODEL LOCK ghi model, params, lý do và timestamp.','Test dùng cho final metrics, residual và explainability sau lock.'],0.75,1.45,5.7,3.8,16);
s.addText('Train/Val → Model development → MODEL LOCK → Test unlock → Final evaluation',{x:6.6,y:2.0,w:5.7,h:1.4,fontSize:20,bold:true,color:'70AD47',align:'center',valign:'mid'});
foot(s); notes(s,'Đây là slide then chốt nếu giảng viên hỏi leakage.', ['outputs/model_selection_policy.json','FINAL_AUDIT_REPORT.md']);

s=pptx.addSlide(); title(s,'7. Feature engineering','Chỉ trình bày feature thật sự có trong code.');
bullets(s,['Age: HouseAge, RemodAge, GarageAge.','Area: TotalSF, TotalPorchSF, TotalOutdoorSF.','Flags: HasGarage, HasBsmt, HasFireplace, HasPool, Has2ndFloor, HasMasVnr.','Seasonality: MoSold_sin, MoSold_cos.'],0.85,1.45,5.7,3.8,16);
addImg(s,'outputs/figures/13_deployment_architecture.png',6.6,1.85,5.5,2.2);
s.addText('Không dùng claim cũ: IsRemodeled, TotalRooms, GarageAreaPerCar...', {x:6.7,y:4.45,w:5.25,h:0.7,fontSize:13,bold:true,color:'AA0000',align:'center'});
foot(s); notes(s,'Giải thích feature engineering là row-wise và nằm trong artifact.', ['outputs/tables/feature_engineering.csv','src/house_price/features.py']);

s=pptx.addSlide(); title(s,'8. Preprocessing pipeline','Numeric và categorical được xử lý trong sklearn Pipeline.');
bullets(s,['Numeric: median imputation + scaling.','Categorical: true missing → Missing; semantic NA được giữ.','OneHotEncoder handle_unknown="ignore".','Target: log1p/expm1 qua transformed target strategy.'],0.85,1.55,5.3,3.55,16);
s.addText('Raw input → AmesFeatureEngineer → ColumnTransformer → '+summary.selected_model+' → USD prediction',{x:6.35,y:2.2,w:5.9,h:1.25,fontSize:20,bold:true,color:'1F4E79',align:'center',valign:'mid'});
foot(s); notes(s,'Nhấn mạnh app không tự fit scaler/encoder và không train lại model.', ['src/house_price/preprocessing.py','src/house_price/artifacts.py']);

s=pptx.addSlide(); title(s,'9. Candidate models','Benchmark rộng nhưng vẫn có kiểm soát.');
addImg(s,'outputs/figures/07_validation_model_comparison.png',0.75,1.35,7.4,4.6);
bullets(s,['DummyRegressor giữ vai trò baseline.','Linear, Ridge, ElasticNet, KNN, Tree và Ensembles được so sánh.','Không thêm model ngoài sklearn chỉ để làm bảng dài.'],8.45,1.8,3.75,2.7,15);
foot(s); notes(s,'Nêu so sánh công bằng: cùng split, preprocessing và metrics.', ['outputs/tables/validation_model_comparison.csv']);

s=pptx.addSlide(); title(s,'10. Tuning và model selection','Quyết định cuối cùng trước khi mở test.');
metric(s,'Final model',summary.selected_model,0.8,1.6,3.2); metric(s,'Val RMSE',fmt(summary.validation_metrics.RMSE)+' USD',4.1,1.6,3.2); metric(s,'CV RMSE mean',fmt(summary.selected_model_cv_stability.CV_RMSE_mean)+' USD',7.4,1.6,3.2);
s.addText('Params: '+JSON.stringify(summary.selected_params),{x:1.1,y:3.1,w:11.0,h:0.55,fontSize:16,bold:true,color:'1F4E79',align:'center'});
bullets(s,['Test không nằm trong rule chọn model.','Executable rule: validation RMSE + Ridge tolerance/CV tie-break.','Deployability chỉ là cân nhắc định tính sau selection, không phải tiêu chí code.'],2.2,4.05,8.8,1.45,15);
foot(s); notes(s,'Giải thích vì sao final là ElasticNet trong bản này, không giữ claim Ridge cũ.', ['outputs/tables/tuning_results.csv','outputs/model_selection_policy.json']);

s=pptx.addSlide(); title(s,'11. Test evaluation','Đánh giá cuối trên test sau model lock.');
metric(s,'RMSE',fmt(summary.test_metrics.RMSE)+' USD',0.75,1.5,2.9); metric(s,'MAE',fmt(summary.test_metrics.MAE)+' USD',3.85,1.5,2.9); metric(s,'R²',summary.test_metrics.R2.toFixed(4),6.95,1.5,2.9); metric(s,'RMSLE',summary.test_metrics.RMSLE.toFixed(4),10.05,1.5,2.4);
addImg(s,'outputs/figures/08_actual_vs_predicted.png',1.05,2.85,5.3,3.4); addImg(s,'outputs/figures/09_residual_vs_predicted.png',6.9,2.85,5.3,3.4);
foot(s); notes(s,'Nhấn mạnh không quay lại tuning sau khi thấy test metric.', ['outputs/summary.json','outputs/tables/test_metrics.csv']);

s=pptx.addSlide(); title(s,'12. Error by segment','Sai số cao hơn ở nhóm nhà giá cao.');
addImg(s,'outputs/figures/11_error_by_price_quartile.png',0.8,1.35,5.5,4.7);
addImg(s,'outputs/figures/10_residual_distribution.png',6.75,1.35,5.5,4.7);
foot(s); notes(s,'Nêu rõ Q4 có MAE lớn nhất, đây là limitation quan trọng khi bảo vệ.', ['outputs/tables/error_by_price_quartile.csv','outputs/figures/10_residual_distribution.png']);

s=pptx.addSlide(); title(s,'13. Explainability','Permutation importance sau model lock.');
addImg(s,'outputs/figures/12_permutation_importance.png',0.8,1.25,7.2,5.1);
bullets(s,['Top features giúp giải thích model behavior.','Có nhiều repeats nên có std thật.','Không phải causal effect.'],8.45,2.0,3.65,2.5,16);
foot(s); notes(s,'Giải thích phương pháp permutation: xáo trộn một feature và đo suy giảm performance.', ['outputs/tables/permutation_importance.csv','outputs/figures/12_permutation_importance.png']);

s=pptx.addSlide(); title(s,'14. Artifact và backend','Artifact cuối nhận raw input, không cần gọi FE thủ công.');
bullets(s,[`Artifact: ${summary.artifact.path}.`,`Model hash: ${summary.artifact.model_sha256.slice(0,16)}...`,`contains_feature_engineering = ${summary.artifact.contains_feature_engineering}.`,`end_to_end_raw_input = ${summary.artifact.end_to_end_raw_input}.`],0.85,1.5,5.55,3.6,15);
addImg(s,'outputs/figures/13_deployment_architecture.png',6.55,1.75,5.6,2.35);
foot(s); notes(s,'Nhấn mạnh backend/app dùng cùng artifact với training, không duplication pipeline.', ['models/model_metadata.json','src/house_price/artifacts.py']);

s=pptx.addSlide(); title(s,'15. Streamlit product','Quick, full, batch và model information.');
bullets(s,['Quick Input: nhập biến quan trọng và dùng default từ schema.','Full Input: 79 biến theo semantic groups.','Batch CSV: upload nhiều căn nhà và download prediction.','Model Information: metric, hash, limitation từ canonical source.'],0.85,1.55,5.7,3.7,16);
s.addText('Container audit: streamlit executable unavailable; không claim PASS giả.',{x:6.9,y:2.25,w:4.9,h:1.1,fontSize:18,bold:true,color:'AA0000',align:'center',valign:'mid'});
foot(s); notes(s,'Nếu demo thật, chạy streamlit run app/Home.py sau khi pip install requirements.', ['docs/DEMO_GUIDE.md','docs/DEPLOYMENT.md']);

s=pptx.addSlide(); title(s,'16. Testing','Evidence chạy thật từ pytest.');
metric(s,'Pytest',testEvidence.tests_passed+' passed',1.0,1.7,3.2); metric(s,'Source coverage',coverageDisplay,5.0,1.7,3.2); metric(s,'Warning',testEvidence.warnings+' abnormal warnings',9.0,1.7,3.2);
bullets(s,['Coverage scope: src/house_price + backend.','tuning.py/reporting.py/artifacts.py/backend đều có test hành vi thật.','Consistency checker đọc evidence JSON, model hash, notebook, DOCX/PPTX và docs.'],2.1,3.3,9.0,2.0,16);
foot(s); notes(s,'Không bịa test count: dùng log pytest/coverage mới nhất sau refactor.', ['outputs/audit/test_summary.json','outputs/audit/coverage.json','QUALITY_AUDIT.md']);

s=pptx.addSlide(); title(s,'17. Reproducibility','Không chỉ tái tạo model, mà còn tài liệu.');
bullets(s,['requirements.txt + Python >=3.11.','scripts/train_full_project.py tạo outputs/model/artifact.','scripts/build_report.py build DOCX/PDF thật.','scripts/build_slides.py build PPTX thật.','outputs/summary.json là single source of truth.'],0.85,1.45,5.8,4.1,15);
s.addText('Consistency goal: không còn README → ElasticNet nhưng MODEL_CARD → Ridge.',{x:6.75,y:2.35,w:5.2,h:1.25,fontSize:18,bold:true,color:'70AD47',align:'center',valign:'mid'});
foot(s); notes(s,'Đây là điểm sửa lớn so với bản 96-100 bị rút ngắn và lệch docs.', ['REPRODUCIBILITY.md','OLD_VS_FINAL_CONTENT_AUDIT.md']);

s=pptx.addSlide(); title(s,'18. Limitations','Nói thật limitation để bảo vệ chắc hơn.');
bullets(s,['Dữ liệu ở Ames/Iowa, không áp dụng trực tiếp cho Việt Nam.','Test chỉ 146 dòng; high-price homes khó dự báo hơn.','CV std còn đáng kể.','Không dùng model cho định giá pháp lý/ngân hàng.','Cần cloud deploy thật và UI testing nếu phát triển tiếp.'],0.95,1.5,11.2,3.5,17);
foot(s); notes(s,'Khi kết luận, nhấn mạnh tính học thuật/demo và không phóng đại khả năng dùng thực tế.', ['MODEL_CARD.md','FINAL_AUDIT_REPORT.md']);

s=pptx.addSlide(); title(s,'19. Kết luận và Q&A','Bản cuối kết hợp nội dung đầy đủ và core kỹ thuật mới.');
s.addText('Final model: '+summary.selected_model,{x:0.85,y:1.55,w:3.8,h:0.45,fontSize:22,bold:true,color:'1F4E79',align:'center'});
s.addText('Test RMSE: '+fmt(summary.test_metrics.RMSE)+' USD',{x:4.75,y:1.55,w:3.8,h:0.45,fontSize:22,bold:true,color:'1F4E79',align:'center'});
s.addText('R²: '+summary.test_metrics.R2.toFixed(4),{x:8.65,y:1.55,w:3.0,h:0.45,fontSize:22,bold:true,color:'1F4E79',align:'center'});
bullets(s,['Đúng khoa học: model lock trước test.','Đúng kỹ thuật: artifact end-to-end và tests.','Đầy đủ học thuật: README/report/slide/docs đã mở rộng lại.','Còn cần điền thông tin hành chính trước khi nộp.'],1.3,3.1,10.5,2.25,17);
foot(s); notes(s,'Kết thúc bằng thông điệp: không chạy theo metric giả, ưu tiên correctness, reproducibility và defense readiness.', ['README.md','DEFENSE_QA.md','FINAL_AUDIT_REPORT.md']);

pptx.writeFile({ fileName: path.join(root,'slides','Slide_Du_bao_gia_nha_Hoan_chinh.pptx') });
