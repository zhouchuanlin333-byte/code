import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import shap
import matplotlib.pyplot as plt
import os
import seaborn as sns

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
    
    # 删除所有包含空值的列（由额外逗号导致）
    df = df.dropna(axis=1, how='all')
    
    # 处理列名中的空格
    df.columns = [col.strip() for col in df.columns]
    
    return df

def train_xgboost_model(period):
    """训练XGBoost模型并计算SHAP值"""
    print(f"\n--- {period}数据处理 --- ")
    
    # 加载原始数据（包含休闲POI数量）
    df_original = load_original_data(period)
    
    # 分离特征和目标变量
    X = df_original.drop(['碳排放_carbon_emission_kg (kgCO2/KM/d)', 'grid_id'], axis=1)
    y = df_original['碳排放_carbon_emission_kg (kgCO2/KM/d)']
    
    # 使用全部数据训练模型（不划分训练测试集）
    print(f"{period}数据集大小：{X.shape}")
    print(f"特征列：{list(X.columns)}")
    
    # 训练XGBoost模型
    model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # 创建SHAP解释器
    explainer = shap.Explainer(model)
    shap_values = explainer(X)
    
    return X, shap_values

# 测试早高峰数据
period = "早高峰"
X, shap_values = train_xgboost_model(period)