import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
import shap
import matplotlib.pyplot as plt
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 定义输出目录
output_dir = "D:/Desktop/项目论文/SHAP值解释性分析/自动化相互作用交互分析"
os.makedirs(output_dir, exist_ok=True)

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

# 读取数据
def load_data(time_of_day):
    if time_of_day == "早高峰":
        data = pd.read_csv(r"D:/Desktop/项目论文/建模/早高峰_标准化_utf8.csv")
    else:
        data = pd.read_csv(r"D:/Desktop/项目论文/建模/晚高峰_标准化_utf8.csv")
    
    # 移除可能的索引列
    if 'Unnamed: 0' in data.columns:
        data = data.drop(['Unnamed: 0'], axis=1)
    
    # 定义特征和目标变量
    X = data.drop(['碳排放_carbon_emission_kg (kgCO2/KM/d)'], axis=1)
    y = data['碳排放_carbon_emission_kg (kgCO2/KM/d)']
    
    return X, y

# 训练XGBoost模型并进行SHAP分析
def train_and_analyze(time_of_day, X_train, y_train, X_test, y_test):
    print(f"\n--- {time_of_day}数据分析 ---")
    
    # 训练XGBoost模型
    model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # 评估模型
    y_pred = model.predict(X_test)
    mse = np.mean((y_pred - y_test) ** 2)
    print(f"{time_of_day} XGBoost模型测试集MSE: {mse:.5f}")
    
    # 创建SHAP解释器 - 使用所有数据来生成SHAP值，增加图中的点数
    print(f"使用所有数据({X_train.shape[0] + X_test.shape[0]}个样本)生成SHAP值...")
    X_all = pd.concat([X_train, X_test])
    explainer = shap.Explainer(model)
    shap_values = explainer(X_all)
    
    return model, explainer, shap_values, X_all

# 绘制道路密度和居住POI的交互作用图
def plot_road_density_residential_interaction(time_of_day, model, shap_values, X_all, output_dir):
    print(f"\n--- 绘制{time_of_day}道路密度与居住POI的交互作用图 ---")
    
    # 创建时间特定的输出目录
    time_output_dir = os.path.join(output_dir, time_of_day)
    os.makedirs(time_output_dir, exist_ok=True)
    
    # 定义要分析的两个特征
    feat1 = "道路密度 (KM/KM²)"
    feat2 = "居住POI数量 (个)"
    
    # 检查特征是否存在
    if feat1 not in X_all.columns or feat2 not in X_all.columns:
        print(f"错误：{feat1} 或 {feat2} 不在特征列表中")
        print(f"可用特征：{X_all.columns.tolist()}")
        return
    
    # 绘制交互图 - 使用shap.dependence_plot
    print(f"绘制{time_of_day} {feat1}与{feat2}的交互作用图...")
    
    shap.dependence_plot(
        feat1, shap_values.values, X_all, 
        interaction_index=feat2, show=False
    )
    
    # 设置标题和标签
    plt.title(f'{time_of_day} - {feat1} 与 {feat2} 交互作用分析')
    plt.xlabel(f'{feat1} ({variable_units.get(feat1, "")})')
    plt.ylabel(f'SHAP值 (影响程度)')
    
    # 清理文件名
    clean_feat1 = feat1.replace(' ', '_').replace('(', '').replace(')', '').replace('/','')
    clean_feat2 = feat2.replace(' ', '_').replace('(', '').replace(')', '').replace('/','')
    
    # 保存图像
    save_path = os.path.join(time_output_dir, f"{time_of_day}_road_density_vs_residential_poi_interaction.png")
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ {time_of_day}交互图已保存：{save_path}")

# 主函数
def main():
    print("="*60)
    print("道路密度与居住POI交互作用分析")
    print("="*60)
    
    # 处理早高峰数据
    X_early, y_early = load_data("早高峰")
    X_early_train, X_early_test, y_early_train, y_early_test = train_test_split(X_early, y_early, test_size=0.3, random_state=42)
    print(f"早高峰训练集大小：{X_early_train.shape}，测试集大小：{X_early_test.shape}")
    
    # 处理晚高峰数据
    X_late, y_late = load_data("晚高峰")
    X_late_train, X_late_test, y_late_train, y_late_test = train_test_split(X_late, y_late, test_size=0.3, random_state=42)
    print(f"晚高峰训练集大小：{X_late_train.shape}，测试集大小：{X_late_test.shape}")
    
    # 训练模型并分析早高峰数据
    model_early, explainer_early, shap_values_early, X_early_all = train_and_analyze("早高峰", X_early_train, y_early_train, X_early_test, y_early_test)
    plot_road_density_residential_interaction("早高峰", model_early, shap_values_early, X_early_all, output_dir)
    
    # 训练模型并分析晚高峰数据
    model_late, explainer_late, shap_values_late, X_late_all = train_and_analyze("晚高峰", X_late_train, y_late_train, X_late_test, y_late_test)
    plot_road_density_residential_interaction("晚高峰", model_late, shap_values_late, X_late_all, output_dir)
    
    print("\n" + "="*60)
    print("分析完成！所有结果已保存到：")
    print(output_dir)
    print("="*60)

if __name__ == "__main__":
    main()