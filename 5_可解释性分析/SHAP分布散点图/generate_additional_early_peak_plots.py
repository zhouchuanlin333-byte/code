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
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
plt.rcParams['figure.figsize'] = [12, 8]
plt.rcParams['figure.dpi'] = 300

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

# 定义要分析的新增变量（仅早高峰）
target_variables = {
    "办公POI数量 (个)": "办公POI数量",
    "人口密度 (千人/km²)": "人口密度",
    "标准化土地混合熵": "标准化土地混合熵"
}

# 确保输出目录存在
output_dir = "D:/Desktop/项目论文/shap可视化/SHAP分布散点图"
os.makedirs(output_dir, exist_ok=True)
print(f"输出目录已创建或存在: {output_dir}")

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

def load_standardized_data(period):
    """加载标准化数据用于模型训练"""
    if period == "早高峰":
        file_path = "d:/Desktop/项目论文/建模/特征工程/优化后_早高峰_标准化_utf8.csv"
    else:
        file_path = "d:/Desktop/项目论文/建模/特征工程/优化后_晚高峰_标准化_utf8.csv"
    
    df = pd.read_csv(file_path)
    
    # 删除所有包含空值的列（由额外逗号导致）
    df = df.dropna(axis=1, how='all')
    
    # 处理列名中的空格
    df.columns = [col.strip() for col in df.columns]
    
    # 分离特征和目标变量
    X = df.drop('碳排放_carbon_emission_kg (kgCO2/KM/d)', axis=1)
    y = df['碳排放_carbon_emission_kg (kgCO2/KM/d)']
    
    return X, y

def train_xgboost_model(period):
    """训练XGBoost模型并计算SHAP值"""
    print(f"\n--- {period}数据处理 --- ")
    
    # 加载标准化数据
    X, y = load_standardized_data(period)
    
    # 使用全部数据训练模型（不划分训练测试集）
    print(f"{period}数据集大小：{X.shape}")
    
    # 训练XGBoost模型
    model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # 创建SHAP解释器
    explainer = shap.Explainer(model)
    shap_values = explainer(X)
    
    return X, shap_values

def plot_shap_distribution_scatter(period, X, shap_values):
    """绘制SHAP值分布散点图"""
    print(f"\n--- 生成{period}新增变量SHAP分布散点图 ---")
    
    # 获取原始数据
    df_original = load_original_data(period)
    
    for target_var, display_name in target_variables.items():
        if target_var not in X.columns:
            print(f"警告：{target_var} 不在数据中，跳过")
            continue
            
        # 获取特征索引
        feature_idx = list(X.columns).index(target_var)
        
        # 获取SHAP值
        feature_shap_values = shap_values.values[:, feature_idx]
        
        # 获取原始特征值（非标准化）
        original_feature_values = df_original[target_var].values
        
        # 创建图形
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 绘制散点图 - 使用原始特征值作为横坐标
        scatter = ax.scatter(original_feature_values, feature_shap_values, 
                           alpha=0.6, s=20, c=feature_shap_values, 
                           cmap='RdYlBu_r', edgecolors='black', linewidth=0.5)
        
        # 添加颜色条
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('SHAP值', fontsize=12)
        
        # 设置坐标轴标签
        unit = variable_units.get(target_var, "")
        ax.set_xlabel(f'{display_name} ({unit})', fontsize=14, fontweight='bold')
        ax.set_ylabel('SHAP值', fontsize=14, fontweight='bold')
        
        # 设置标题
        ax.set_title(f'{period} - {display_name} SHAP值分布散点图\n'
                    f'(样本数: {len(original_feature_values)}个500m×500m栅格)', 
                    fontsize=16, fontweight='bold', pad=20)
        
        # 添加零线
        ax.axhline(y=0, color='red', linestyle='--', alpha=0.7, linewidth=2)
        # 对于距离类变量，添加零线；对于计数和密度变量，不添加垂直零线
        if "距离" in display_name:
            ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
        elif "密度" in display_name or "熵" in display_name:
            # 对于密度和熵变量，在合理范围内添加参考线
            if "密度" in display_name:
                ax.axvline(x=np.mean(original_feature_values), color='gray', linestyle='--', alpha=0.5, label='平均值')
            elif "熵" in display_name:
                ax.axvline(x=0.7, color='gray', linestyle='--', alpha=0.5, label='中等混合度')
        
        # 添加网格
        ax.grid(True, alpha=0.3)
        
        # 设置刻度标签大小
        ax.tick_params(axis='both', which='major', labelsize=12)
        
        # 添加统计信息
        mean_shap = np.mean(feature_shap_values)
        std_shap = np.std(feature_shap_values)
        stats_text = f'均值: {mean_shap:.4f}\n标准差: {std_shap:.4f}'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                fontsize=11, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图片
        filename = f'{period}_{display_name}_SHAP分布散点图.png'
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"{period} {display_name} SHAP分布散点图已保存：{filepath}")
        
        # 打印统计信息
        print(f"  - 特征值范围: [{np.min(original_feature_values):.3f}, {np.max(original_feature_values):.3f}]")
        print(f"  - SHAP值范围: [{np.min(feature_shap_values):.4f}, {np.max(feature_shap_values):.4f}]")
        print(f"  - SHAP值均值: {mean_shap:.4f}")

def generate_early_peak_additional_plots():
    """生成早高峰新增变量的SHAP分布散点图"""
    period = "早高峰"
    
    try:
        # 训练模型并获取SHAP值
        X, shap_values = train_xgboost_model(period)
        
        # 生成散点图
        plot_shap_distribution_scatter(period, X, shap_values)
        
    except Exception as e:
        print(f"处理{period}数据时出错：{str(e)}")
        return
    
    print(f"\n--- 早高峰新增变量SHAP分布散点图生成完成！---")
    print(f"图片保存路径：{output_dir}")

# 主函数
def main():
    generate_early_peak_additional_plots()

if __name__ == "__main__":
    main()