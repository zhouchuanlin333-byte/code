import pandas as pd
import numpy as np
import xgboost as xgb
import shap
import os
import matplotlib.pyplot as plt

# 设置中文字体和样式
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def load_original_data(period):
    """加载原始未标准化的数据"""
    if period == "早高峰":
        file_path = "d:/Desktop/项目论文/建模/早高峰_统一单位.csv"
    else:
        file_path = "d:/Desktop/项目论文/建模/晚高峰1_统一单位.csv"
    
    df = pd.read_csv(file_path)
    df = df.dropna(axis=1, how='all')
    df.columns = [col.strip() for col in df.columns]
    return df

def train_xgboost_model(period):
    """训练XGBoost模型并计算SHAP值"""
    df_original = load_original_data(period)
    X = df_original.drop(['碳排放_carbon_emission_kg (kgCO2/KM/d)', 'grid_id'], axis=1)
    y = df_original['碳排放_carbon_emission_kg (kgCO2/KM/d)']
    
    model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42)
    model.fit(X, y)
    
    explainer = shap.Explainer(model)
    shap_values = explainer(X)
    
    return X, shap_values, df_original

def print_shap_stats(period, X, shap_values, df_original, target_var, display_name):
    """打印SHAP统计信息"""
    if target_var not in X.columns:
        print(f"警告：{target_var} 不在数据中")
        return
        
    feature_idx = list(X.columns).index(target_var)
    feature_shap_values = shap_values.values[:, feature_idx]
    original_feature_values = df_original[target_var].values
    
    mean_shap = np.mean(feature_shap_values)
    std_shap = np.std(feature_shap_values)
    
    print(f"\n{period} - {display_name} SHAP分析:")
    print(f"  - 特征值范围: [{np.min(original_feature_values):.3f}, {np.max(original_feature_values):.3f}]")
    print(f"  - SHAP值范围: [{np.min(feature_shap_values):.4f}, {np.max(feature_shap_values):.4f}]")
    print(f"  - SHAP值均值: {mean_shap:.4f}")
    print(f"  - SHAP值标准差: {std_shap:.4f}")

# 分析公共服务POI数量和交通设施POI数量
periods = ["早高峰", "晚高峰"]
target_vars = {
    "公共服务POI数量 (个)": "公共服务POI数量",
    "交通设施POI数量 (个)": "交通设施POI数量"
}

print("=== 公共服务POI数量和交通设施POI数量SHAP分析结果 ===")

for period in periods:
    print(f"\n{'='*50}")
    print(f"{period}数据分析")
    print(f"{'='*50}")
    
    X, shap_values, df_original = train_xgboost_model(period)
    
    for target_var, display_name in target_vars.items():
        print_shap_stats(period, X, shap_values, df_original, target_var, display_name)

print(f"\n{'='*50}")
print("分析完成！")
print(f"图片保存在: D:/Desktop/项目论文/shap可视化/SHAP分布散点图/")