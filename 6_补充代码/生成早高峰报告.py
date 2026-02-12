import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import shap
import matplotlib.pyplot as plt
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 确保输出目录存在
output_dir = "d:/Desktop/项目论文/SHAP值解释性分析"
os.makedirs(output_dir, exist_ok=True)
print(f"输出目录已创建或存在: {output_dir}")

# 定义变量名和单位（原始单位）
variable_units = {
    "人口密度 (千人/km²)": "千人/km²",
    "办公POI数量 (个)": "个",
    "居住POI数量 (个)": "个",
    "道路密度 (KM/KM²)": "KM/KM²",
    "地铁站点数量 (个)": "个",
    "公交站点数量 (个)": "个",
    "标准化土地混合熵": "无单位",
    "到市中心距离 (km)": "km",
    "到最近公交距离 (km)": "km"
}

# 读取早高峰数据
def load_early_peak_data():
    file_path = "d:/Desktop/项目论文/建模/特征工程/优化后_早高峰_标准化_utf8.csv"
    df = pd.read_csv(file_path)
    print(f"早高峰数据加载完成，形状：{df.shape}")
    print(f"早高峰数据列名：{list(df.columns)}")
    
    # 删除所有包含空值的列（由额外逗号导致）
    df = df.dropna(axis=1, how='all')
    
    print(f"早高峰数据清理后形状：{df.shape}")
    print(f"早高峰数据清理后列名：{list(df.columns)}")
    
    # 处理列名中的空格
    df.columns = [col.strip() for col in df.columns]
    
    # 分离特征和目标变量
    X = df.drop('碳排放_carbon_emission_kg (kgCO2/KM/d)', axis=1)
    y = df['碳排放_carbon_emission_kg (kgCO2/KM/d)']
    
    return X, y

# 训练XGBoost模型并生成重要度报告
def generate_early_peak_report():
    print(f"\n--- 早高峰数据处理 --- ")
    
    # 加载数据
    X, y = load_early_peak_data()
    
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    print(f"早高峰训练集大小：{X_train.shape}，测试集大小：{X_test.shape}")
    
    # 训练XGBoost模型
    model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # 创建SHAP解释器
    explainer = shap.Explainer(model)
    shap_values = explainer(X_test)
    
    print(f"\n--- 生成早高峰变量重要度报告 --- ")
    
    # 计算SHAP特征重要度（平均绝对SHAP值）
    shap_importance = np.abs(shap_values.values).mean(axis=0)
    
    # 计算特征总重要度
    total_importance = shap_importance.sum()
    
    # 计算重要度占比
    importance_percentage = (shap_importance / total_importance) * 100
    
    # 计算正负向反馈（平均SHAP值的符号）
    mean_shap_values = shap_values.values.mean(axis=0)
    feedback = np.where(mean_shap_values > 0, '正向', '负向')
    
    # 创建重要度DataFrame
    importance_df = pd.DataFrame({
        '特征名': X_test.columns,
        'SHAP重要度': shap_importance,
        '重要度占比(%)': importance_percentage,
        '正负向反馈': feedback,
        '单位': [variable_units.get(feature, "") for feature in X_test.columns]
    })
    
    # 按重要度排序
    importance_df = importance_df.sort_values(by='SHAP重要度', ascending=False)
    
    # 保存为CSV文件
    report_path = os.path.join(output_dir, "早高峰_变量重要度报告.csv")
    importance_df.to_csv(report_path, index=False, encoding='utf-8-sig')
    
    print(f"早高峰变量重要度报告已生成：")
    print(importance_df)
    print(f"报告保存路径：{report_path}")
    
    return importance_df

# 主函数
def main():
    generate_early_peak_report()
    print("\n--- 早高峰报告生成完成！---")

if __name__ == "__main__":
    main()