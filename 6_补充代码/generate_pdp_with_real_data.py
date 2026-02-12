import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.inspection import PartialDependenceDisplay
import matplotlib.pyplot as plt
import os
from scipy import interpolate

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 确保输出目录存在
print("当前工作目录:", os.getcwd())
output_dir = os.path.abspath("SHAP值解释性分析")
print(f"输出目录: {output_dir}")
pdp_real_data_dir = os.path.join(output_dir, "PDP_真实数据刻度")
print(f"PDP真实数据刻度目录: {pdp_real_data_dir}")

# 确保目录存在
for directory in [output_dir, pdp_real_data_dir]:
    if not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"成功创建目录: {directory}")
        except Exception as e:
            print(f"创建目录失败 {directory}: {e}")
    else:
        print(f"目录已存在: {directory}")

# 创建早高峰和晚高峰PDP子目录
early_peak_pdp_dir = os.path.join(pdp_real_data_dir, "早高峰")
late_peak_pdp_dir = os.path.join(pdp_real_data_dir, "晚高峰")
print(f"早高峰PDP目录: {early_peak_pdp_dir}")
print(f"晚高峰PDP目录: {late_peak_pdp_dir}")

for directory in [early_peak_pdp_dir, late_peak_pdp_dir]:
    if not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"成功创建子目录: {directory}")
        except Exception as e:
            print(f"创建子目录失败 {directory}: {e}")
    else:
        print(f"子目录已存在: {directory}")

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

# 读取数据（同时加载标准化和未标准化的数据）
def load_data(time_of_day):
    # 加载标准化数据（用于训练模型和计算PDP）
    if time_of_day == "早高峰":
        std_file_path = "d:/Desktop/项目论文/建模/特征工程/优化后_早高峰_标准化_utf8.csv"
        real_file_path = "d:/Desktop/项目论文/建模/早高峰_统一单位.csv"
    else:
        std_file_path = "d:/Desktop/项目论文/建模/特征工程/优化后_晚高峰_标准化_utf8.csv"
        real_file_path = "d:/Desktop/项目论文/建模/晚高峰1_统一单位.csv"
    
    # 加载标准化数据
    std_df = pd.read_csv(std_file_path)
    print(f"{time_of_day}标准化数据加载完成，形状：{std_df.shape}")
    
    # 处理标准化数据中的额外列
    std_df = std_df.dropna(axis=1, how='all')
    
    # 加载真实数据（用于获取真实刻度范围）
    real_df = pd.read_csv(real_file_path)
    print(f"{time_of_day}真实数据加载完成，形状：{real_df.shape}")
    
    # 确保列名一致
    std_df.columns = [col.strip() for col in std_df.columns]
    real_df.columns = [col.strip() for col in real_df.columns]
    
    # 分离特征和目标变量（使用标准化数据进行模型训练和PDP计算）
    X = std_df.drop('碳排放_carbon_emission_kg (kgCO2/KM/d)', axis=1)
    y = std_df['碳排放_carbon_emission_kg (kgCO2/KM/d)']
    
    return X, y, real_df

# 训练XGBoost模型
def train_model(X_train, y_train):
    print("\n--- 训练XGBoost模型 ---")
    model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model

# 绘制PDP依赖图（使用真实数据刻度）
def plot_pdp_visualizations(time_of_day, model, X_test, real_df):
    print(f"\n--- 绘制{time_of_day} PDP可视化图（真实数据刻度） ---")
    
    if time_of_day == "早高峰":
        save_dir = early_peak_pdp_dir
    else:
        save_dir = late_peak_pdp_dir
    
    # 获取碳排放的真实统计信息（用于逆标准化）
    carbon_col = '碳排放_carbon_emission_kg (kgCO2/KM/d)'
    real_carbon_mean = real_df[carbon_col].mean()
    real_carbon_std = real_df[carbon_col].std()
    real_carbon_min = real_df[carbon_col].min()
    real_carbon_max = real_df[carbon_col].max()
    
    print(f"碳排放真实数据统计: 均值={real_carbon_mean:.4f}, 标准差={real_carbon_std:.4f}, 最小值={real_carbon_min:.4f}, 最大值={real_carbon_max:.4f}")
    
    # 对每个特征绘制PDP图
    for feature in X_test.columns:
        try:
            print(f"正在绘制 {time_of_day} - {feature} PDP图...")
            
            # 创建画布 - 1:1布局 (宽:长)
            fig, ax = plt.subplots(figsize=(10, 10))
            
            # 获取特征在真实数据中的统计信息
            feature_real_mean = real_df[feature].mean()
            feature_real_std = real_df[feature].std()
            feature_real_min = real_df[feature].min()
            feature_real_max = real_df[feature].max()
            print(f"  {feature} 真实范围: {feature_real_min:.2f} - {feature_real_max:.2f} {variable_units.get(feature, '')}")
            print(f"  {feature} 真实均值: {feature_real_mean:.2f} {variable_units.get(feature, '')}")
            print(f"  {feature} 真实标准差: {feature_real_std:.2f} {variable_units.get(feature, '')}")
            
            # 使用model.predict生成真正的真实碳排放值的PDP图
            # 首先获取feature的真实值范围
            grid_points = 100  # 增加网格点数量以提高平滑度
            
            # 创建基于真实值的特征网格
            real_feature_grid = np.linspace(feature_real_min, feature_real_max, grid_points)
            
            # 将真实值转换为标准化值用于模型预测
            std_feature_grid = (real_feature_grid - feature_real_mean) / feature_real_std
            
            # 创建包含所有特征的副本
            X_pdp = X_test.copy()
            
            # 固定其他特征为均值
            for col in X_pdp.columns:
                if col != feature:
                    X_pdp[col] = X_pdp[col].mean()
            
            # 预测每个网格点的碳排放值
            pdp_values = []
            for val in std_feature_grid:
                X_pdp[feature] = val
                pred = model.predict(X_pdp)
                pdp_values.append(np.mean(pred))
            
            # 将预测值从标准化值转换为真实的碳排放值
            real_pdp_values = np.array(pdp_values) * real_carbon_std + real_carbon_mean
            
            # 确保碳排放值不小于0（因为碳排放值不可能为负数）
            real_pdp_values = np.maximum(real_pdp_values, 0)
            
            # 使用真实特征值作为x轴坐标
            feature_grid = real_feature_grid
            
            # 不使用平滑处理，直接使用原始数据
            
            # 根据用户要求设置x轴范围和刻度
            x_min = 0  # 横坐标最小值设为0
            x_max = feature_real_max
            custom_ticks = None  # 自定义刻度
            
            # 用户自定义的x轴范围和刻度设置
            if feature == "办公POI数量 (个)":
                x_max = 320
                tick_spacing = 40
            elif feature == "标准化土地混合熵":
                x_max = 1  # 范围不变
                tick_spacing = 0.2  # 保持合理的刻度间隔
            elif feature == "到市中心距离 (km)":
                x_max = 20
                # 自定义刻度：0-15km用3km间隔，15-20km用5km间隔
                custom_ticks = [0, 3, 6, 9, 12, 15, 20]
            elif feature == "到最近公交距离 (km)":
                x_max = 4
                tick_spacing = 0.5
            elif feature == "公交站点数量 (个)":
                x_max = 8
                tick_spacing = 1
            elif feature == "地铁站点数量 (个)":
                x_max = 2
                tick_spacing = 0.4
            elif feature == "居住POI数量 (个)":
                x_max = 240
                tick_spacing = 30
            elif feature == "人口密度 (千人/km²)":
                # 人口密度不变，使用原有设置
                pass
            elif feature == "道路密度 (KM/KM²)":
                # 道路密度不变，使用原有设置
                pass
            else:
                # 其他特征保持原有逻辑
                pass
            
            # 过滤曲线数据，只保留x >= 0的部分
            valid_indices = feature_grid >= 0
            filtered_feature_grid = feature_grid[valid_indices]
            filtered_real_pdp = real_pdp_values[valid_indices]
            
            # 设置x轴范围
            ax.set_xlim(x_min, x_max)
            
            # 找到过滤后曲线的最低点和最高点
            min_idx = np.argmin(filtered_real_pdp)
            max_idx = np.argmax(filtered_real_pdp)
            min_point = (filtered_feature_grid[min_idx], filtered_real_pdp[min_idx])
            max_point = (filtered_feature_grid[max_idx], filtered_real_pdp[max_idx])
            
            # 设置x轴刻度
            if custom_ticks is not None:
                # 使用自定义刻度
                ax.set_xticks(custom_ticks)
            else:
                # 使用自动计算的刻度间隔
                ax.set_xticks(np.arange(np.round(x_min / tick_spacing) * tick_spacing, 
                                      np.round(x_max / tick_spacing) * tick_spacing + tick_spacing, 
                                      tick_spacing))
            
            # 绘制过滤后的PDP曲线（只显示x >= 0的部分）- 使用默认颜色
            ax.plot(filtered_feature_grid, filtered_real_pdp, linewidth=2.5, 
                   label='PDP曲线')
            
            # 设置标题和标签
            ax.set_title(f'{time_of_day} - {feature} 部分依赖图', fontsize=14, fontweight='bold')
            ax.set_xlabel(f'{feature} ({variable_units.get(feature, "")})', fontsize=12)
            ax.set_ylabel('碳排放 (kgCO2/KM/d)', fontsize=12)
            
            # 添加网格线（更细的网格）
            ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)
            
            # 添加图例（只包含PDP曲线）
            ax.legend(fontsize=10, loc='upper right')
            
            # 设置坐标轴刻度的字体大小
            ax.tick_params(axis='both', which='major', labelsize=10)
            
            # 清理文件名，移除特殊字符
            clean_feature = feature.replace(' ', '_').replace('(', '').replace(')', '').replace('/','')
            
            # 创建一个更大的画布，在右侧添加注释空间
            fig.subplots_adjust(right=0.8)
            
            # 添加外部注释（在画布右侧）
            annotations = [
                f'PDP曲线',
                f'最低点: ({min_point[0]:.2f}, {min_point[1]:.4f})',
                f'最高点: ({max_point[0]:.2f}, {max_point[1]:.4f})'
            ]
            
            # 在右侧添加文本注释
            for i, text in enumerate(annotations):
                fig.text(0.82, 0.9 - i*0.05, text, fontsize=10, ha='left')
            
            # 保存图像
            plt.tight_layout()
            plt.savefig(os.path.join(save_dir, f"{time_of_day}_{clean_feature}_pdp_真实刻度.png"), dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"成功绘制 {time_of_day} - {feature} PDP图")
        except Exception as e:
            print(f"绘制 {time_of_day} - {feature} PDP图时出错: {e}")
            import traceback
            traceback.print_exc()
    print(f"{time_of_day} PDP图已保存到: {save_dir}")

# 主函数
def main():
    # 处理早高峰数据
    print("\n" + "="*50)
    print("处理早高峰数据")
    print("="*50)
    X_early, y_early, real_early_df = load_data("早高峰")
    X_early_train, X_early_test, y_early_train, y_early_test = train_test_split(X_early, y_early, test_size=0.3, random_state=42)
    print(f"早高峰训练集大小：{X_early_train.shape}，测试集大小：{X_early_test.shape}")
    
    # 训练早高峰模型
    model_early = train_model(X_early_train, y_early_train)
    
    # 绘制早高峰PDP图
    plot_pdp_visualizations("早高峰", model_early, X_early_test, real_early_df)
    
    # 处理晚高峰数据
    print("\n" + "="*50)
    print("处理晚高峰数据")
    print("="*50)
    X_late, y_late, real_late_df = load_data("晚高峰")
    X_late_train, X_late_test, y_late_train, y_late_test = train_test_split(X_late, y_late, test_size=0.3, random_state=42)
    print(f"晚高峰训练集大小：{X_late_train.shape}，测试集大小：{X_late_test.shape}")
    
    # 训练晚高峰模型
    model_late = train_model(X_late_train, y_late_train)
    
    # 绘制晚高峰PDP图
    plot_pdp_visualizations("晚高峰", model_late, X_late_test, real_late_df)
    
    print(f"\n--- 所有PDP图绘制完成！---")
    print(f"PDP图（真实数据刻度）保存在：{pdp_real_data_dir}")

if __name__ == "__main__":
    main()