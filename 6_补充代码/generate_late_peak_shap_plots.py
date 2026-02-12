import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import shap
import matplotlib.pyplot as plt
import seaborn as sns
import os
from matplotlib.colors import LinearSegmentedColormap
import warnings
warnings.filterwarnings('ignore')

# 设置字体：中文用宋体，英文数字用新罗马，大小统一为小四（12pt）
plt.rcParams['font.sans-serif'] = ['SimSun']  # 中文宋体
plt.rcParams['font.serif'] = ['Times New Roman']  # 英文新罗马
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
plt.rcParams['font.family'] = ['sans-serif', 'serif']  # 混合字体设置
plt.rcParams['font.size'] = 12  # 全局字体大小设为小四（12pt）

# 设置输出目录
output_dir = "D:/Desktop/项目论文/SHAP值解释性分析/PDP_真实数据刻度/基于SHAP生成单一变量的阈值分析图"
os.makedirs(output_dir, exist_ok=True)

# 创建晚高峰子目录
late_peak_dir = os.path.join(output_dir, "晚高峰")
os.makedirs(late_peak_dir, exist_ok=True)

# 定义变量名和单位（原始单位）
variable_units = {
    "人口密度": "千人/km²",
    "办公POI数量": "个",
    "休闲POI数量": "个",
    "居住POI数量": "个",
    "交通设施POI数量": "个",
    "公共服务POI数量": "个",
    "道路密度": "km/km²",
    "地铁站点数量": "个",
    "公交站点数量": "个",
    "标准化土地混合熵": "无单位",
    "到市中心距离": "km",
    "到最近公交距离": "km"
}

# 定义特征名称映射
feature_name_mapping = {
    "办公POI数量": "就业办公POI数量",
    "居住POI数量": "商品住宅POI数量",
    "标准化土地混合熵": "标准化土地混合度"
}

# 自定义色系（参考晚高峰碳排放地图色系）
late_peak_color = '#1E88E5'   # 深蓝色系

# 读取晚高峰数据
def load_late_peak_data():
    file_path = "d:/Desktop/项目论文/建模/特征工程/优化后_晚高峰_标准化_utf8.csv"
    df = pd.read_csv(file_path)
    print(f"晚高峰数据加载完成，形状：{df.shape}")
    
    # 处理晚高峰数据中的额外列
    df = df.dropna(axis=1, how='all')
    
    # 分离特征和目标变量
    X = df.drop('碳排放_carbon_emission_kg (kgCO2/KM/d)', axis=1)
    y = df['碳排放_carbon_emission_kg (kgCO2/KM/d)']
    
    return X, y

# 训练模型并计算SHAP值
def train_late_peak_model(X_train, y_train, X_test, y_test):
    print(f"\n--- 晚高峰模型训练与SHAP计算 ---")
    
    # 训练XGBoost模型
    model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # 评估模型
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"晚高峰 XGBoost模型测试集MSE: {mse:.5f}")
    
    # 创建SHAP解释器并计算SHAP值
    explainer = shap.Explainer(model)
    shap_values = explainer(X_test)
    
    return model, explainer, shap_values, X_test, y_test

# 生成SHAP分布图
def generate_late_peak_shap_distribution_plots(shap_values, X_test, y_test):
    print(f"\n--- 生成晚高峰SHAP分布图 ---")
    
    save_dir = late_peak_dir
    color = late_peak_color
    
    # 为每个特征生成SHAP分布图
    for i, feature in enumerate(X_test.columns):
        plt.figure(figsize=(12, 8))
        
        # 获取该特征的SHAP值和特征值
        feature_shap_values = shap_values.values[:, i]
        feature_values = X_test.iloc[:, i].values
        
        # 创建散点图
        plt.scatter(feature_values, feature_shap_values, 
                   alpha=0.6, s=20, color=color, edgecolors='black', linewidth=0.5)
        
        # 添加趋势线（使用更稳健的方法）
        try:
            # 检查数据有效性
            if len(np.unique(feature_values)) > 1 and len(np.unique(feature_shap_values)) > 1:
                # 使用robust线性回归
                from sklearn.linear_model import LinearRegression
                X_reshaped = feature_values.reshape(-1, 1)
                lr = LinearRegression()
                lr.fit(X_reshaped, feature_shap_values)
                trend_line = lr.predict(X_reshaped)
                
                # 按特征值排序后绘制平滑的趋势线
                sort_idx = np.argsort(feature_values)
                plt.plot(feature_values[sort_idx], trend_line[sort_idx], "r--", alpha=0.8, linewidth=2)
        except Exception as e:
            print(f"警告：无法为特征 {feature} 绘制趋势线: {e}")
            # 如果趋势线绘制失败，跳过趋势线
        
        # 设置标题和标签
        feature_display_name = feature_name_mapping.get(feature, feature)
        plt.title(f'晚高峰 - {feature_display_name} SHAP分布图', fontsize=16, fontweight='bold')
        plt.xlabel(f'{feature_display_name} ({variable_units.get(feature, "")})', fontsize=14)
        plt.ylabel('SHAP值 (对碳排放的影响)', fontsize=14)
        
        # 添加网格
        plt.grid(True, alpha=0.3)
        
        # 添加统计信息
        correlation = np.corrcoef(feature_values, feature_shap_values)[0, 1]
        plt.text(0.05, 0.95, f'相关系数: {correlation:.3f}', 
                transform=plt.gca().transAxes, fontsize=12,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图片
        clean_feature = feature.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '')
        plt.savefig(os.path.join(save_dir, f"晚高峰_{clean_feature}_SHAP分布图.png"), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"已生成: 晚高峰_{clean_feature}_SHAP分布图.png")

# 生成SHAP值与目标值的关系图
def generate_late_peak_shap_target_relationship_plots(shap_values, X_test, y_test):
    print(f"\n--- 生成晚高峰SHAP值与目标值关系图 ---")
    
    save_dir = late_peak_dir
    color = late_peak_color
    
    # 为每个特征生成SHAP值与目标值的关系图
    for i, feature in enumerate(X_test.columns):
        plt.figure(figsize=(12, 8))
        
        # 获取该特征的SHAP值和特征值
        feature_shap_values = shap_values.values[:, i]
        feature_values = X_test.iloc[:, i].values
        
        # 创建子图
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # 左图：SHAP值与特征值的关系
        scatter1 = ax1.scatter(feature_values, feature_shap_values, 
                              c=y_test, alpha=0.6, s=20, cmap='viridis')
        ax1.set_xlabel(f'{feature_name_mapping.get(feature, feature)} ({variable_units.get(feature, "")})')
        ax1.set_ylabel('SHAP值 (对碳排放的影响)')
        ax1.set_title(f'晚高峰 - {feature_name_mapping.get(feature, feature)} SHAP分析')
        ax1.grid(True, alpha=0.3)
        plt.colorbar(scatter1, ax=ax1, label='碳排放 (kgCO2/KM/d)')
        
        # 右图：特征值与目标值的关系
        scatter2 = ax2.scatter(feature_values, y_test, 
                              c=feature_shap_values, alpha=0.6, s=20, cmap='RdBu_r')
        ax2.set_xlabel(f'{feature_name_mapping.get(feature, feature)} ({variable_units.get(feature, "")})')
        ax2.set_ylabel('碳排放 (kgCO2/KM/d)')
        ax2.set_title(f'晚高峰 - {feature_name_mapping.get(feature, feature)} 与碳排放关系')
        ax2.grid(True, alpha=0.3)
        plt.colorbar(scatter2, ax=ax2, label='SHAP值')
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图片
        clean_feature = feature.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '')
        plt.savefig(os.path.join(save_dir, f"晚高峰_{clean_feature}_SHAP目标值关系图.png"), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"已生成: 晚高峰_{clean_feature}_SHAP目标值关系图.png")

# 生成综合SHAP分析图
def generate_late_peak_comprehensive_shap_analysis(shap_values, X_test, y_test):
    print(f"\n--- 生成晚高峰综合SHAP分析图 ---")
    
    save_dir = late_peak_dir
    color = late_peak_color
    
    # 计算特征重要性
    shap_importance = np.abs(shap_values.values).mean(axis=0)
    sorted_indices = np.argsort(shap_importance)[::-1]
    
    # 选择前6个重要特征进行详细分析
    top_features = X_test.columns[sorted_indices[:6]]
    
    # 创建大图包含多个子图
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()
    
    for idx, feature in enumerate(top_features):
        ax = axes[idx]
        
        # 获取该特征的SHAP值和特征值
        feature_shap_values = shap_values.values[:, X_test.columns.get_loc(feature)]
        feature_values = X_test[feature].values
        
        # 创建散点图
        scatter = ax.scatter(feature_values, feature_shap_values, 
                           alpha=0.6, s=15, color=color, edgecolors='black', linewidth=0.3)
        
        # 添加趋势线
        try:
            if len(np.unique(feature_values)) > 1 and len(np.unique(feature_shap_values)) > 1:
                from sklearn.linear_model import LinearRegression
                X_reshaped = feature_values.reshape(-1, 1)
                lr = LinearRegression()
                lr.fit(X_reshaped, feature_shap_values)
                trend_line = lr.predict(X_reshaped)
                sort_idx = np.argsort(feature_values)
                ax.plot(feature_values[sort_idx], trend_line[sort_idx], "r--", alpha=0.8, linewidth=1.5)
        except:
            pass
        
        # 设置标题和标签
        feature_display_name = feature_name_mapping.get(feature, feature)
        ax.set_title(f'{feature_display_name}', fontsize=12, fontweight='bold')
        ax.set_xlabel(f'{feature_display_name} ({variable_units.get(feature, "")})', fontsize=10)
        ax.set_ylabel('SHAP值', fontsize=10)
        
        # 添加网格
        ax.grid(True, alpha=0.3)
        
        # 添加统计信息
        correlation = np.corrcoef(feature_values, feature_shap_values)[0, 1]
        ax.text(0.05, 0.95, f'r={correlation:.3f}', 
               transform=ax.transAxes, fontsize=9,
               bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8))
    
    # 设置总标题
    fig.suptitle('晚高峰 - 主要特征SHAP分布综合分析', fontsize=16, fontweight='bold')
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig(os.path.join(save_dir, f"晚高峰_综合SHAP分析图.png"), 
               dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"已生成: 晚高峰_综合SHAP分析图.png")

# 生成SHAP值分布直方图
def generate_late_peak_shap_distribution_histograms(shap_values, X_test):
    print(f"\n--- 生成晚高峰SHAP值分布直方图 ---")
    
    save_dir = late_peak_dir
    color = late_peak_color
    
    # 计算特征重要性并排序
    shap_importance = np.abs(shap_values.values).mean(axis=0)
    sorted_indices = np.argsort(shap_importance)[::-1]
    
    # 选择前9个重要特征
    top_features = X_test.columns[sorted_indices[:9]]
    
    # 创建3x3的子图布局
    fig, axes = plt.subplots(3, 3, figsize=(15, 12))
    axes = axes.flatten()
    
    for idx, feature in enumerate(top_features):
        ax = axes[idx]
        
        # 获取该特征的SHAP值
        feature_shap_values = shap_values.values[:, X_test.columns.get_loc(feature)]
        
        # 绘制直方图
        ax.hist(feature_shap_values, bins=30, alpha=0.7, color=color, edgecolor='black', linewidth=0.5)
        
        # 添加垂直线表示均值
        mean_shap = np.mean(feature_shap_values)
        ax.axvline(mean_shap, color='red', linestyle='--', linewidth=2, label=f'均值: {mean_shap:.3f}')
        
        # 设置标题和标签
        feature_display_name = feature_name_mapping.get(feature, feature)
        ax.set_title(f'{feature_display_name}', fontsize=10, fontweight='bold')
        ax.set_xlabel('SHAP值', fontsize=9)
        ax.set_ylabel('频次', fontsize=9)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    
    # 设置总标题
    fig.suptitle('晚高峰 - 主要特征SHAP值分布直方图', fontsize=14, fontweight='bold')
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig(os.path.join(save_dir, f"晚高峰_SHAP值分布直方图.png"), 
               dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"已生成: 晚高峰_SHAP值分布直方图.png")

# 主函数
def main():
    print("=== 生成晚高峰SHAP分布图 ===")
    print(f"输出目录: {output_dir}")
    
    # 处理晚高峰数据
    print("\n" + "="*50)
    print("处理晚高峰数据")
    print("="*50)
    
    X_late, y_late = load_late_peak_data()
    X_late_train, X_late_test, y_late_train, y_late_test = train_test_split(
        X_late, y_late, test_size=0.3, random_state=42)
    
    model_late, explainer_late, shap_values_late, X_late_test, y_late_test = \
        train_late_peak_model(X_late_train, y_late_train, X_late_test, y_late_test)
    
    # 生成晚高峰SHAP分析图
    generate_late_peak_shap_distribution_plots(shap_values_late, X_late_test, y_late_test)
    generate_late_peak_shap_target_relationship_plots(shap_values_late, X_late_test, y_late_test)
    generate_late_peak_comprehensive_shap_analysis(shap_values_late, X_late_test, y_late_test)
    generate_late_peak_shap_distribution_histograms(shap_values_late, X_late_test)
    
    print("\n" + "="*50)
    print("晚高峰SHAP分布图生成完成！")
    print(f"结果保存在: {late_peak_dir}")
    print("="*50)

if __name__ == "__main__":
    main()