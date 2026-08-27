import numpy as np
from sklearn.linear_model import Ridge
from house_price.data import load_house_data,split_xy
from house_price.modeling import build_end_to_end_estimator,model_definitions,tuning_space
from house_price.preprocessing import build_preprocessor

def raw(n=30):
    tr=load_house_data('house_train_80.csv'); X,y=split_xy(tr.head(n)); return X,y

def test_model_catalog_contains_required_families():
    names=set(model_definitions()); required={'LinearRegression','Ridge','ElasticNet','KNeighborsRegressor','DecisionTreeRegressor','RandomForestRegressor','ExtraTreesRegressor','GradientBoostingRegressor','HistGradientBoostingRegressor'}; assert required.issubset(names)

def test_ridge_tuning_space_has_multiple_alphas(): assert len(tuning_space('Ridge')['regressor__model__alpha'])>=10

def test_preprocessor_separates_numeric_and_category():
    X,_=raw(); pre,num,cat=build_preprocessor(X); assert num and cat and 'MSSubClass' in cat and pre is not None

def test_end_to_end_estimator_contains_feature_engineering_and_predicts_raw():
    X,y=raw(); model=build_end_to_end_estimator(X,Ridge(alpha=5.0)); model.fit(X,y); p=model.predict(X.head(3)); assert len(p)==3 and np.isfinite(p).all()
