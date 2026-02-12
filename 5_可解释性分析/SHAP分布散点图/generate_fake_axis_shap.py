import pandas as pd
import numpy as np
import xgboost as xgb
import shap
import matplotlib.pyplot as plt
import os

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

def plot_custom_transportation_shap_scatter():
    """生成虚假坐标轴的早高峰交通设施POI数量SHAP散点图"""
    period = "早高峰"
    target_var = "交通设施POI数量 (个)"
    display_name = "交通设施POI数量"
    output_dir = "D:/Desktop/项目论文/shap可视化/SHAP分布散点图"
    
    print(f"生成{period} {display_name} 虚假坐标轴SHAP散点图...")
    
    # 训练模型并获取SHAP值
    X, shap_values, df_original = train_xgboost_model(period)
    
    # 检查目标变量是否存在
    if target_var not in X.columns:
        print(f"警告：{target_var} 不在数据中")
        return
    
    # 获取目标变量的SHAP值和原始特征值
    feature_idx = list(X.columns).index(target_var)
    feature_shap_values = shap_values.values[:, feature_idx]
    original_feature_values = df_original[target_var].values
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # 绘制散点图 - 保持原始散点分布和颜色，不改变任何形状和颜色
    scatter = ax.scatter(original_feature_values, feature_shap_values, 
                         alpha=0.6, s=20, c=feature_shap_values, 
                         cmap='RdYlBu_r', edgecolors='black', linewidth=0.5)
    
    # 添加颜色条，设置虚假刻度范围
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('SHAP值', fontsize=12)
    cbar.set_ticks(np.arange(-4, 11, 2))  # 从-4到10，刻度为2
    
    # 设置坐标轴标签
    ax.set_xlabel(f'{display_name} (个)', fontsize=14, fontweight='bold')
    ax.set_ylabel('SHAP值', fontsize=14, fontweight='bold')
    
    # 设置虚假坐标轴范围和刻度
    ax.set_xlim(0, 30)  # 横坐标虚假范围：0-30
    ax.set_xticks(np.arange(0, 31, 5))  # 横坐标刻度：0,5,10,15,20,25,30
    ax.set_ylim(-4, 10)  # 纵坐标虚假范围：-4到10
    ax.set_yticks(np.arange(-4, 11, 2))  # 纵坐标刻度：-4,-2,0,2,4,6,8,10
    
    # 设置标题
    ax.set_title(f'{period} - {display_name} SHAP值分布散点图\n'
                f'(样本数: {len(original_feature_values)}个500m×500m栅格)', 
                fontsize=16, fontweight='bold', pad=20)
    
    # 添加零线
    ax.axhline(y=0, color='red', linestyle='--', alpha=0.7, linewidth=2)
    
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
    filename = f'{period}_{display_name}_SHAP分布散点图_虚假坐标轴.png'
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"虚假坐标轴{period} {display_name} SHAP分布散点图已保存：{filepath}")
    
    # 打印统计信息
    print(f"  - 原始特征值范围: [{np.min(original_feature_values):.3f}, {np.max(original_feature_values):.3f}]")
    print(f"  - 原始SHAP值范围: [{np.min(feature_shap_values):.4f}, {np.max(feature_shap_values):.4f}]")
    print(f"  - SHAP值均值: {mean_shap:.4f}")
    print(f"  - SHAP值标准差: {std_shap:.4f}")
    print(f"  - 虚假坐标轴显示: 横坐标0-30(刻度5)，纵坐标-4-10(刻度2)")

if __name__ == "__main__":
    plot_custom_transportation_shap_scatter()