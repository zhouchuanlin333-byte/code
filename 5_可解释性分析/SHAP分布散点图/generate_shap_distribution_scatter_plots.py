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
import matplotlib.font_manager as fm

# 创建字体属性
chinese_font = fm.FontProperties(family='SimSun')
english_font = fm.FontProperties(family='Times New Roman')

# 添加字体到matplotlib
plt.rcParams['font.sans-serif'] = ['SimSun', 'SimHei']  # 中文宋体，备用黑体
plt.rcParams['font.serif'] = ['Times New Roman']  # 英文新罗马
plt.rcParams['font.family'] = 'sans-serif'  # 默认使用sans-serif
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
plt.rcParams['figure.figsize'] = [8, 8]  # 1:1比例
plt.rcParams['figure.dpi'] = 300
plt.rcParams['text.usetex'] = False  # 禁用LaTeX
plt.rcParams['axes.formatter.use_mathtext'] = False  # 禁用mathtext支持

# 定义变量名和单位（原始单位）
variable_units = {
    "人口密度 (千人/km²)": "千人/km²",
    "办公POI数量 (个)": "个",
    "居住POI数量 (个)": "个",
    "休闲POI数量 (个)": "个",
    "公共服务POI数量 (个)": "个",
    "交通设施POI数量 (个)": "个",
    "道路密度 (KM/KM²)": "KM/KM²",
    "地铁站点数量 (个)": "个",
    "公交站点数量 (个)": "个",
    "标准化土地混合熵": "无单位",
    "到市中心距离 (km)": "km",
    "到最近公交距离 (km)": "km"
}

# 定义要分析的变量
target_variables = {
    "居住POI数量 (个)": "商品住宅POI数量",
    "休闲POI数量 (个)": "休闲POI数量",
    "公共服务POI数量 (个)": "公共服务POI数量",
    "交通设施POI数量 (个)": "交通设施POI数量",
    "到市中心距离 (km)": "到市中心距离", 
    "到最近公交距离 (km)": "到最近公交距离",
    "办公POI数量 (个)": "就业办公POI数量",
    "人口密度 (千人/km²)": "人口密度",
    "标准化土地混合熵": "标准化土地混合度",
    "道路密度 (KM/KM²)": "道路密度"
}

# 定义每个变量的自定义刻度
custom_ticks = {
    "商品住宅POI数量": [0, 100, 200, 300, 400, 500],
    "到市中心距离": [0, 5, 10, 15, 20, 25, 30],
    "就业办公POI数量": [0, 50, 100, 150, 200, 250, 300, 350],
    "到最近公交距离": [0, 2.5, 5.0, 7.5, 10, 12.5, 15, 17.5],
    "道路密度": [0, 50, 100, 150, 200, 250],
    "标准化土地混合度": [0, 0.2, 0.4, 0.6, 0.8, 1.0]
}

# 确保输出目录存在
output_dir = "D:/Desktop/项目论文/灰白图"
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

def plot_shap_distribution_scatter(period, X, shap_values):
    """绘制SHAP值分布散点图"""
    print(f"\n--- 生成{period}SHAP分布散点图 ---")
    
    # 获取原始数据
    df_original = load_original_data(period)
    
    # 只处理用户指定的6个早高峰变量
    selected_vars = {
        "标准化土地混合熵": "标准化土地混合度",
        "到市中心距离 (km)": "到市中心距离",
        "到最近公交距离 (km)": "到最近公交距离",
        "道路密度 (KM/KM²)": "道路密度",
        "办公POI数量 (个)": "就业办公POI数量",
        "居住POI数量 (个)": "商品住宅POI数量"
    }
    
    for target_var, display_name in selected_vars.items():
        if target_var not in X.columns:
            print(f"警告：{target_var} 不在数据中，跳过")
            continue
            
        # 获取特征索引
        feature_idx = list(X.columns).index(target_var)
        
        # 获取SHAP值
        feature_shap_values = shap_values.values[:, feature_idx]
        
        # 获取原始特征值（非标准化）
        original_feature_values = df_original[target_var].values
        
        # 处理NaN值 - 只保留非NaN的数据点
        valid_mask = ~(np.isnan(original_feature_values) | np.isnan(feature_shap_values))
        valid_feature_values = original_feature_values[valid_mask]
        valid_shap_values = feature_shap_values[valid_mask]
        
        # 创建图形 - 使用正方形尺寸确保1:1视觉比例
        fig, ax = plt.subplots(figsize=(8, 7))
        
        # 创建自定义颜色映射 - 基于用户提供的原始颜色块，确保负值为蓝色
        from matplotlib.colors import ListedColormap, LinearSegmentedColormap, TwoSlopeNorm
        
        # 创建从灰到黑的颜色映射
        gray_colors = ['#888888', '#707070', '#585858', '#404040', '#303030', '#202020', '#181818', '#101010', '#080808']
        
        # 计算SHAP值的范围
        shap_min, shap_max = np.min(valid_shap_values), np.max(valid_shap_values)
        
        # 创建以0为中心的颜色映射，使用灰度颜色
        if shap_min < 0 and shap_max > 0:
            # 有正负值的情况 - 确保颜色条中0为分界点
            
            # 特殊处理早高峰到最近公交距离，确保0到-5范围显示足够的灰度
            if period == '早高峰' and target_var == '到最近公交距离':
                # 为早高峰到最近公交距离设置特殊的灰度映射
                colors_negative = gray_colors[3:7]  # 使用中间灰度
                colors_positive = gray_colors[:7]  # 使用较浅到深的灰度
                all_colors = colors_negative + colors_positive
                custom_cmap = ListedColormap(all_colors)
                # 使用TwoSlopeNorm确保0是分界点
                norm = TwoSlopeNorm(vmin=shap_min, vcenter=0, vmax=shap_max)
            else:
                # 其他变量使用统一的灰度映射逻辑
                colors_negative = gray_colors[4:7]  # 负值使用较深灰度
                colors_positive = gray_colors[:8]  # 正值使用完整灰度梯度
                all_colors = colors_negative + colors_positive
                custom_cmap = ListedColormap(all_colors)
                # 使用TwoSlopeNorm确保0是分界点
                norm = TwoSlopeNorm(vmin=shap_min, vcenter=0, vmax=shap_max)
        elif shap_max <= 0:
            # 全部为负值，使用灰度渐变
            all_colors = gray_colors[3:8]  # 使用中间到深的灰度
            # 根据值的范围扩展颜色
            if shap_max < -10:  # 很大的负值范围
                all_colors = all_colors * 2  # 重复颜色以获得更多渐变
            custom_cmap = ListedColormap(all_colors)
            norm = None  # 使用默认归一化
        else:
            # 全部为正值，使用灰度渐变
            all_colors = gray_colors[:9]  # 使用完整灰度梯度
            # 根据值的范围扩展颜色
            if shap_max > 20:  # 很大的正值范围
                all_colors = all_colors * 2  # 重复颜色以获得更多渐变
            custom_cmap = ListedColormap(all_colors)
            norm = None  # 使用默认归一化
        
        # 绘制散点图 - 使用有效特征值作为横坐标
        if norm is not None:
            scatter = ax.scatter(valid_feature_values, valid_shap_values, 
                               alpha=0.6, s=20, c=valid_shap_values, 
                               cmap=custom_cmap, norm=norm, edgecolors='black', linewidth=0.5)
        else:
            scatter = ax.scatter(valid_feature_values, valid_shap_values, 
                               alpha=0.6, s=20, c=valid_shap_values, 
                               cmap=custom_cmap, edgecolors='black', linewidth=0.5)
        

        
        # 设置横坐标标签，添加相应单位
        if display_name == "标准化土地混合度":
            xlabel = f'{display_name}'  # 不添加单位
        elif display_name == "商品住宅POI数量":
            xlabel = f'{display_name}/个'
        elif display_name == "就业办公POI数量":
            xlabel = f'{display_name}/个'
        elif display_name == "到最近公交距离":
            xlabel = f'{display_name}/km'
        elif display_name == "到市中心距离":
            xlabel = f'{display_name}/km'
        elif display_name == "道路密度":
            xlabel = f'{display_name}/(km/km⁻²)'
        else:
            xlabel = f'{display_name}'  # 默认不添加单位
        
        # 设置坐标轴标签
        if display_name == "道路密度":
            # 对于道路密度，使用mathtext显示整个单位部分
            # 先获取当前字体设置，然后临时启用mathtext支持
            original_use_mathtext = plt.rcParams['axes.formatter.use_mathtext']
            plt.rcParams['axes.formatter.use_mathtext'] = True
            
            # 创建完整的x轴标签
            full_label = f'{display_name}/(km/km$^{{-2}}$)'
            
            # 使用set_xlabel设置完整标签，中文字符使用SimSun，数学部分使用Times New Roman
            ax.set_xlabel(full_label, fontsize=27, fontweight='bold', fontproperties=chinese_font)
            
            # 恢复原来的mathtext设置
            plt.rcParams['axes.formatter.use_mathtext'] = original_use_mathtext
        else:
            ax.set_xlabel(xlabel, fontsize=27, fontweight='bold', fontproperties=chinese_font)
        ax.set_ylabel('SHAP值', fontsize=27, fontweight='bold', fontproperties=chinese_font)
        
        # 去掉标题
        # ax.set_title(f'{period} - {display_name} SHAP值分布散点图\n'
        #             f'(有效样本数: {len(valid_feature_values)}个500m×500m栅格)', 
        #             fontsize=32, fontweight='bold', pad=20)
        
        # 添加零线
        ax.axhline(y=0, color='gray', linestyle='--', alpha=0.7, linewidth=2)
        # 对于距离类变量，添加零线；对于计数变量，不添加垂直零线
        if "距离" in display_name:
            ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
        
        # 移除网格
        ax.grid(False)
        
        # 设置刻度标签大小和间距
        ax.tick_params(axis='x', which='major', labelsize=27)
        ax.tick_params(axis='y', which='both', labelsize=27)
        
        # 自动调整Y轴范围，减少空白区域
        y_min, y_max = np.min(valid_shap_values), np.max(valid_shap_values)
        y_range = y_max - y_min
        
        # 针对特定图表使用不同的边距
        if display_name in ["标准化土地混合度", "到市中心距离", "到最近公交距离"]:
            y_margin = y_range * 0.05  # 这三个保持5%的边距
        else:
            y_margin = y_range * 0.02  # 其他图表使用2%的边距，更紧凑
        
        ax.set_ylim(y_min - y_margin, y_max + y_margin)
        
        # 设置自定义刻度
        if display_name in custom_ticks:
            ax.set_xticks(custom_ticks[display_name])
        
        # 删除统计信息
        # mean_shap = np.mean(valid_shap_values)
        # std_shap = np.std(valid_shap_values)
        # stats_text = f'均值: {mean_shap:.4f}\n标准差: {std_shap:.4f}'
        # ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
        #         fontsize=22, verticalalignment='top',
        #         bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图片
        filename = f'{period}_{display_name}_SHAP分布散点图.png'
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"{period} {display_name} SHAP分布散点图已保存：{filepath}")
        
        # 打印统计信息
        print(f"  - 特征值范围: [{np.min(valid_feature_values):.3f}, {np.max(valid_feature_values):.3f}]")
        print(f"  - SHAP值范围: [{np.min(valid_shap_values):.4f}, {np.max(valid_shap_values):.4f}]")
        # print(f"  - SHAP值均值: {mean_shap:.4f}")
        print(f"  - 有效样本数: {len(valid_feature_values)} (总样本数: {len(original_feature_values)})")

def generate_all_shap_scatter_plots():
    """生成所有SHAP分布散点图"""
    periods = ["早高峰"]  # 只处理早高峰
    
    for period in periods:
        try:
            # 训练模型并获取SHAP值
            X, shap_values = train_xgboost_model(period)
            
            # 生成散点图
            plot_shap_distribution_scatter(period, X, shap_values)
            
        except Exception as e:
            print(f"处理{period}数据时出错：{str(e)}")
            continue
    
    print(f"\n--- 所有SHAP分布散点图生成完成！---")
    print(f"图片保存路径：{output_dir}")

# 主函数
def main():
    generate_all_shap_scatter_plots()

if __name__ == "__main__":
    main()