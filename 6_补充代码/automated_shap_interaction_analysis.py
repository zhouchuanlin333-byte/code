import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
import shap
import matplotlib.pyplot as plt
import os
import json

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 定义输出目录
output_dir = "d:/Desktop/项目论文/SHAP值解释性分析/自动化相互作用交互分析"
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
        file_path = "d:/Desktop/项目论文/建模/特征工程/优化后_早高峰_标准化_utf8.csv"
    else:
        file_path = "d:/Desktop/项目论文/建模/特征工程/优化后_晚高峰_标准化_utf8.csv"
    
    df = pd.read_csv(file_path)
    print(f"{time_of_day}数据加载完成，形状：{df.shape}")
    
    # 处理晚高峰数据中的额外列
    df = df.dropna(axis=1, how='all')
    
    # 分离特征和目标变量
    X = df.drop('碳排放_carbon_emission_kg (kgCO2/KM/d)', axis=1)
    y = df['碳排放_carbon_emission_kg (kgCO2/KM/d)']
    
    return X, y

# 训练XGBoost模型并进行SHAP分析
def train_and_analyze(time_of_day, X_train, y_train):
    print(f"\n--- {time_of_day}数据分析 ---")
    
    # 训练XGBoost模型
    model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # 评估模型（使用训练集本身进行评估）
    y_pred = model.predict(X_train)
    mse = np.mean((y_pred - y_train) ** 2)
    print(f"{time_of_day} XGBoost模型训练集MSE: {mse:.5f}")
    
    # 创建SHAP解释器 - 使用训练集数据来生成SHAP值
    print(f"使用训练集({X_train.shape[0]}个样本)生成SHAP值...")
    explainer = shap.Explainer(model)
    shap_values = explainer(X_train)
    
    return model, explainer, shap_values

# 分析变量交互作用并绘制自定义交互图
def analyze_interactions(time_of_day, model, shap_values, X_train):
    # 使用训练集数据来绘制交互图
    print(f"\n--- 分析{time_of_day}变量交互作用 ---")
    
    # 创建时间特定的输出目录
    time_output_dir = os.path.join(output_dir, time_of_day)
    os.makedirs(time_output_dir, exist_ok=True)
    
    # 计算特征间的交互强度
    print(f"计算{time_of_day}特征交互强度...")
    # 直接使用原始XGBoost模型，使用训练集数据计算交互强度
    interaction_values = shap.TreeExplainer(model).shap_interaction_values(X_train)
    
    # 计算平均交互强度（取绝对值）
    mean_interaction = np.abs(interaction_values).mean(axis=0)
    
    # 排除自身交互（对角线）
    np.fill_diagonal(mean_interaction, 0)
    
    # 获取前4组最强交互
    feature_names = X_train.columns.tolist()
    n_features = len(feature_names)
    
    # 生成所有特征对并计算交互强度
    interactions = []
    for i in range(n_features):
        for j in range(i+1, n_features):
            interactions.append((feature_names[i], feature_names[j], mean_interaction[i, j]))
    
    # 按交互强度排序
    interactions.sort(key=lambda x: x[2], reverse=True)
    
    # 保存交互强度数据
    interaction_data = {
        "time_of_day": time_of_day,
        "top_interactions": [{
            "feature1": feat1,
            "feature2": feat2,
            "strength": float(strength)
        } for feat1, feat2, strength in interactions[:4]]
    }
    
    with open(os.path.join(time_output_dir, f"{time_of_day}_interactions.json"), "w", encoding="utf-8") as f:
        json.dump(interaction_data, f, ensure_ascii=False, indent=2)
    
    # 打印前4组最强交互
    print(f"{time_of_day}前4组最强交互变量：")
    for i, (feat1, feat2, strength) in enumerate(interactions[:4]):
        print(f"{i+1}. {feat1} 与 {feat2}，交互强度：{strength:.4f}")
        
        # 绘制自定义交互图（使用训练集数据）
        plot_custom_interaction(time_of_day, i+1, feat1, feat2, shap_values.values, X_train, time_output_dir)
    
    # 特别绘制到最近公交距离与办公POI数量的交互图（无论是否在前4）
    plot_specific_interaction(time_of_day, "到最近公交距离 (km)", "办公POI数量 (个)", shap_values.values, X_train, time_output_dir)
    
    print(f"{time_of_day}变量交互作用图已保存到：{time_output_dir}")

# 绘制自定义交互图 - 使用shap.dependence_plot生成与用户要求相同颜色的交互图
def plot_custom_interaction(time_of_day, index, feat1, feat2, shap_values, X_train, output_dir):
    print(f"绘制{time_of_day} {feat1}与{feat2}的交互图...")
    
    # 使用shap.dependence_plot生成与用户要求相同颜色的交互图
    shap.dependence_plot(
        feat1, shap_values, X_train, 
        interaction_index=feat2, show=False
    )
    
    # 清理文件名
    clean_feat1 = feat1.replace(' ', '_').replace('(', '').replace(')', '').replace('/','')
    clean_feat2 = feat2.replace(' ', '_').replace('(', '').replace(')', '').replace('/','')
    
    # 保存图像
    save_path = os.path.join(output_dir, f"{time_of_day}_interactive_{index}_{clean_feat1}_vs_{clean_feat2}.png")
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 交互图已保存：{save_path}")

# 绘制特定的'到最近公交距离'与'办公POI数量'交互图（使用shap.dependence_plot，与用户要求的颜色一致）
def plot_specific_interaction(time_of_day, feat1, feat2, shap_values, X_train, output_dir):
    print(f"绘制{time_of_day} {feat1}与{feat2}的特定交互图（使用shap.dependence_plot）...")
    
    # 使用shap.dependence_plot生成与用户要求相同颜色的交互图
    # 正确的用法：第一个参数是主特征，interaction_index指定交互特征
    shap.dependence_plot(
        feat1, shap_values, X_train, 
        interaction_index=feat2, show=False
    )
    
    # 保存图像
    clean_feat1 = feat1.replace(' ', '_').replace('(', '').replace(')', '').replace('/','')
    clean_feat2 = feat2.replace(' ', '_').replace('(', '').replace(')', '').replace('/','')
    save_path = os.path.join(output_dir, f"{time_of_day}_specific_interaction_{clean_feat1}_vs_{clean_feat2}_shap_style.png")
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 特定交互图（使用shap.dependence_plot，与用户要求颜色一致）已保存：{save_path}")

# 主函数
def main():
    print("="*60)
    print("基于SHAP值的自动化交互作用分析（仅使用训练集）")
    print("="*60)
    
    # 处理早高峰数据 - 使用整个数据集作为训练集
    X_early, y_early = load_data("早高峰")
    print(f"早高峰训练集大小：{X_early.shape}")
    
    # 处理晚高峰数据 - 使用整个数据集作为训练集
    X_late, y_late = load_data("晚高峰")
    print(f"晚高峰训练集大小：{X_late.shape}")
    
    # 训练模型并分析早高峰数据
    model_early, explainer_early, shap_values_early = train_and_analyze("早高峰", X_early, y_early)
    analyze_interactions("早高峰", model_early, shap_values_early, X_early)
    
    # 训练模型并分析晚高峰数据
    model_late, explainer_late, shap_values_late = train_and_analyze("晚高峰", X_late, y_late)
    analyze_interactions("晚高峰", model_late, shap_values_late, X_late)
    
    print("\n" + "="*60)
    print("分析完成！所有结果已保存到：")
    print(output_dir)
    print("="*60)

if __name__ == "__main__":
    main()