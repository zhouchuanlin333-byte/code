import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 确保输出目录存在
print("当前工作目录:", os.getcwd())
output_dir = os.path.abspath("SHAP值解释性分析")
pdp_real_data_dir = os.path.join(output_dir, "PDP_真实数据刻度")
merge_output_dir = os.path.join(pdp_real_data_dir, "早晚高峰合并")

# 确保目录存在
for directory in [output_dir, pdp_real_data_dir, merge_output_dir]:
    if not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"成功创建目录: {directory}")
        except Exception as e:
            print(f"创建目录失败 {directory}: {e}")
    else:
        print(f"目录已存在: {directory}")

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

# 计算PDP值
def calculate_pdp_values(model, X_test, real_df, feature, time_of_day):
    # 获取碳排放的真实统计信息（用于逆标准化）
    carbon_col = '碳排放_carbon_emission_kg (kgCO2/KM/d)'
    real_carbon_mean = real_df[carbon_col].mean()
    real_carbon_std = real_df[carbon_col].std()
    
    # 获取特征在真实数据中的统计信息
    feature_real_mean = real_df[feature].mean()
    feature_real_std = real_df[feature].std()
    feature_real_min = real_df[feature].min()
    feature_real_max = real_df[feature].max()
    
    print(f"{time_of_day} - {feature} 真实范围: {feature_real_min:.2f} - {feature_real_max:.2f} {variable_units.get(feature, '')}")
    
    # 创建基于真实值的特征网格
    grid_points = 100  # 增加网格点数量以提高平滑度
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
    
    # 过滤曲线数据，只保留x >= 0的部分
    valid_indices = feature_grid >= 0
    filtered_feature_grid = feature_grid[valid_indices]
    filtered_real_pdp = real_pdp_values[valid_indices]
    
    return filtered_feature_grid, filtered_real_pdp, feature_real_max

# 合并绘制早晚高峰的PDP曲线
def merge_pdp_curves(early_feature_data, late_feature_data, feature, feature_real_max):
    print(f"\n--- 合并绘制 {feature} 早晚高峰PDP曲线 ---")
    
    # 根据用户要求设置x轴范围和刻度
    x_min = 0  # 横坐标最小值设为0
    x_max = feature_real_max
    custom_ticks = None  # 自定义刻度
    tick_spacing = None
    
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
    
    # 创建画布 - 设置为1:1比例
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # 绘制早高峰曲线 - 使用用户提供的颜色，去掉标记点
    early_feature_grid, early_real_pdp = early_feature_data
    ax.plot(early_feature_grid, early_real_pdp, linewidth=2.5, color='#FFB7B7', 
           label='早高峰')
    
    # 绘制晚高峰曲线 - 使用用户提供的颜色，去掉标记点
    late_feature_grid, late_real_pdp = late_feature_data
    ax.plot(late_feature_grid, late_real_pdp, linewidth=2.5, color='#98BDCA', 
           label='晚高峰')
    
    # 设置标题和标签
    ax.set_title(f'{feature} 早晚高峰部分依赖图', fontsize=16, fontweight='bold')
    ax.set_xlabel(f'{feature} ({variable_units.get(feature, "")})', fontsize=14)
    ax.set_ylabel('碳减排量 (kg)', fontsize=14)
    
    # 设置坐标轴刻度的字体大小，去掉刻度标记
    ax.tick_params(axis='both', which='major', labelsize=12, tick1On=False, tick2On=False)
    
    # 设置x轴范围和刻度
    ax.set_xlim(x_min, x_max)
    if custom_ticks is not None:
        # 使用自定义刻度
        ax.set_xticks(custom_ticks)
    elif tick_spacing is not None:
        # 使用自动计算的刻度间隔
        ax.set_xticks(np.arange(np.round(x_min / tick_spacing) * tick_spacing, 
                              np.round(x_max / tick_spacing) * tick_spacing + tick_spacing, 
                              tick_spacing))
    
    # 添加网格线
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)
    
    # 添加图例
    ax.legend(fontsize=12, loc='best')
    
    # 计算早高峰曲线的最低点和最高点
    early_min_idx = np.argmin(early_real_pdp)
    early_max_idx = np.argmax(early_real_pdp)
    early_min_point = (early_feature_grid[early_min_idx], early_real_pdp[early_min_idx])
    early_max_point = (early_feature_grid[early_max_idx], early_real_pdp[early_max_idx])
    
    # 计算晚高峰曲线的最低点和最高点
    late_min_idx = np.argmin(late_real_pdp)
    late_max_idx = np.argmax(late_real_pdp)
    late_min_point = (late_feature_grid[late_min_idx], late_real_pdp[late_min_idx])
    late_max_point = (late_feature_grid[late_max_idx], late_real_pdp[late_max_idx])
    
    # 在图像右侧添加统一的关键点注释
    annotation_text = f"早高峰关键点：\n"\
                    f"最低点：({early_min_point[0]:.2f}, {early_min_point[1]:.4f})\n"\
                    f"最高点：({early_max_point[0]:.2f}, {early_max_point[1]:.4f})\n\n"\
                    f"晚高峰关键点：\n"\
                    f"最低点：({late_min_point[0]:.2f}, {late_min_point[1]:.4f})\n"\
                    f"最高点：({late_max_point[0]:.2f}, {late_max_point[1]:.4f})"
    
    # 在图像内添加关键点注释
    ax.text(0.7, 0.7, annotation_text, transform=ax.transAxes, fontsize=12, 
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
    
    # 清理文件名，移除特殊字符
    clean_feature = feature.replace(' ', '_').replace('(', '').replace(')', '').replace('/','')
    
    # 保存图像
    plt.tight_layout()
    plt.savefig(os.path.join(merge_output_dir, f"{clean_feature}_pdp_合并.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"成功绘制 {feature} 早晚高峰PDP合并图")

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
    print("早高峰模型训练完成")
    
    # 处理晚高峰数据
    print("\n" + "="*50)
    print("处理晚高峰数据")
    print("="*50)
    X_late, y_late, real_late_df = load_data("晚高峰")
    X_late_train, X_late_test, y_late_train, y_late_test = train_test_split(X_late, y_late, test_size=0.3, random_state=42)
    print(f"晚高峰训练集大小：{X_late_train.shape}，测试集大小：{X_late_test.shape}")
    
    # 训练晚高峰模型
    model_late = train_model(X_late_train, y_late_train)
    print("晚高峰模型训练完成")
    
    # 计算PDP值并合并绘制
    for feature in X_early.columns:
        print(f"\n--- 处理特征: {feature} ---")
        
        # 计算早高峰PDP值
        early_feature_grid, early_real_pdp, early_real_max = calculate_pdp_values(model_early, X_early_test, real_early_df, feature, "早高峰")
        
        # 计算晚高峰PDP值
        late_feature_grid, late_real_pdp, late_real_max = calculate_pdp_values(model_late, X_late_test, real_late_df, feature, "晚高峰")
        
        # 合并绘制
        merge_pdp_curves((early_feature_grid, early_real_pdp), (late_feature_grid, late_real_pdp), feature, max(early_real_max, late_real_max))
    
    print(f"\n--- 所有PDP合并图绘制完成！---")
    print(f"PDP合并图保存在：{merge_output_dir}")

if __name__ == "__main__":
    main()