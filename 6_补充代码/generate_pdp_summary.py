#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成早晚高峰所有特征的PDP曲线汇总图
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import re
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 特征名称映射
translation_map = {
    "population_density (people/km²)": "人口密度 (people/km²)",
    "office_poi_count (个)": "办公POI数量 (个)",
    "residential_poi_count (个)": "居住POI数量 (个)",
    "road_density (km/km²)": "道路密度 (km/km²)",
    "subway_station_count (个)": "地铁站点数量 (个)",
    "bus_station_count (个)": "公交站点数量 (个)",
    "normalized_land_mixed_entropy": "标准化土地混合熵",
    "distance_to_center (km)": "到市中心距离 (km)",
    "distance_to_nearest_bus (km)": "到最近公交距离 (km)"
}

# 变量单位映射
variable_units = {
    "人口密度 (千人/km²)": "千人/km²",
    "办公POI数量 (个)": "个",
    "居住POI数量 (个)": "个",
    "道路密度 (KM/KM²)": "KM/KM²",
    "地铁站点数量 (个)": "个",
    "公交站点数量 (个)": "个",
    "标准化土地混合熵": "",
    "到市中心距离 (km)": "km",
    "到最近公交距离 (km)": "km"
}

# 加载数据
def load_data(time_of_day):
    """加载指定时间段的数据"""
    if time_of_day == "早高峰":
        data_file = os.path.join("网格集成碳排放与建成环境", "早高峰_统一单位.csv")
    else:
        data_file = os.path.join("网格集成碳排放与建成环境", "晚高峰_统一单位.csv")
    
    # 读取数据
    df = pd.read_csv(data_file)
    
    # 获取实际数据集中的特征列
    available_features = list(df.columns)
    print(f"数据集中的可用特征: {available_features}")
    
    # 特征选择（排除非特征列）
    features = [
        "人口密度 (千人/km²)",
        "办公POI数量 (个)",
        "居住POI数量 (个)",
        "道路密度 (KM/KM²)",
        "地铁站点数量 (个)",
        "公交站点数量 (个)",
        "标准化土地混合熵",
        "到市中心距离 (km)",
        "到最近公交距离 (km)"
    ]
    
    # 过滤掉不存在的特征
    features = [f for f in features if f in available_features]
    print(f"过滤后的特征列表: {features}")
    
    # 检查过滤后的特征数量
    if len(features) < 9:
        print(f"警告: 只有 {len(features)} 个特征可用，可能缺少某些特征")
    
    # 提取特征和标签
    X = df[features]
    y = df["碳排放_carbon_emission_kg (kgCO2/KM/d)"]
    
    return X, y, df

# 训练模型
def train_model(X_train, y_train):
    """训练随机森林回归模型"""
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    return model

# 获取PDP数据
def get_pdp_data(model, X_test, real_df, feature):
    """获取指定特征的PDP数据"""
    print(f"  获取特征 {feature} 的统计信息...")
    # 获取特征在真实数据中的统计信息
    feature_real_mean = real_df[feature].mean()
    feature_real_std = real_df[feature].std()
    feature_real_min = real_df[feature].min()
    feature_real_max = real_df[feature].max()
    print(f"  特征统计: 均值={feature_real_mean:.4f}, 标准差={feature_real_std:.4f}, 最小值={feature_real_min:.4f}, 最大值={feature_real_max:.4f}")
    
    # 创建基于真实值的特征网格
    grid_points = 100
    print(f"  创建特征网格，共 {grid_points} 个点...")
    real_feature_grid = np.linspace(feature_real_min, feature_real_max, grid_points)
    
    # 将真实值转换为标准化值用于模型预测
    print(f"  将真实值转换为标准化值...")
    std_feature_grid = (real_feature_grid - feature_real_mean) / feature_real_std
    
    # 创建包含所有特征的副本
    print(f"  创建特征数据副本...")
    X_pdp = X_test.copy()
    
    # 固定其他特征为均值
    print(f"  固定其他特征为均值...")
    for col in X_pdp.columns:
        if col != feature:
            X_pdp[col] = X_pdp[col].mean()
    
    # 预测每个网格点的碳排放值
    print(f"  预测每个网格点的碳排放值...")
    pdp_values = []
    for val in std_feature_grid:
        X_pdp[feature] = val
        pred = model.predict(X_pdp)
        pdp_values.append(np.mean(pred))
    
    # 获取真实的碳排放值的统计信息（用于将预测值转换回真实值）
    print(f"  获取碳排放统计信息...")
    real_carbon_mean = real_df["碳排放_carbon_emission_kg (kgCO2/KM/d)"].mean()
    real_carbon_std = real_df["碳排放_carbon_emission_kg (kgCO2/KM/d)"].std()
    print(f"  碳排放统计: 均值={real_carbon_mean:.4f}, 标准差={real_carbon_std:.4f}")
    
    # 将预测值从标准化值转换为真实的碳排放值
    print(f"  将预测值转换为真实碳排放值...")
    real_pdp_values = np.array(pdp_values) * real_carbon_std + real_carbon_mean
    
    # 使用真实特征值作为x轴坐标
    feature_grid = real_feature_grid
    
    # 根据用户要求设置x轴范围
    x_min = 0  # 横坐标最小值设为0
    x_max = feature_real_max
    custom_ticks = None  # 自定义刻度
    tick_spacing = 1  # 默认刻度间隔
    
    # 用户自定义的x轴范围和刻度设置
    if feature == "办公POI数量 (个)":
        x_max = 320
        tick_spacing = 40
    elif feature == "标准化土地混合熵":
        x_max = 1
        tick_spacing = 0.2
    elif feature == "到市中心距离 (km)":
        x_max = 20
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
    
    # 过滤曲线数据，只保留x >= 0的部分
    print(f"  过滤曲线数据...")
    valid_indices = feature_grid >= 0
    filtered_feature_grid = feature_grid[valid_indices]
    filtered_real_pdp = real_pdp_values[valid_indices]
    print(f"  过滤后的数据点数量: {len(filtered_feature_grid)}")
    
    return filtered_feature_grid, filtered_real_pdp, x_min, x_max, custom_ticks, tick_spacing

# 生成汇总PDP图
def generate_summary_pdp():
    """生成所有特征的PDP曲线汇总图"""
    # 创建保存目录
    save_dir = "PDP曲线汇总图"
    os.makedirs(save_dir, exist_ok=True)
    
    # 加载早晚高峰数据
    print("加载早高峰数据...")
    X_early, y_early, real_early_df = load_data("早高峰")
    X_early_train, X_early_test, y_early_train, y_early_test = train_test_split(X_early, y_early, test_size=0.3, random_state=42)
    
    print("加载晚高峰数据...")
    X_late, y_late, real_late_df = load_data("晚高峰")
    X_late_train, X_late_test, y_late_train, y_late_test = train_test_split(X_late, y_late, test_size=0.3, random_state=42)
    
    # 训练模型
    print("训练早高峰模型...")
    model_early = train_model(X_early_train, y_early_train)
    
    print("训练晚高峰模型...")
    model_late = train_model(X_late_train, y_late_train)
    
    # 获取所有特征
    features = X_early.columns.tolist()
    
    # 为每个特征创建汇总图
    for i, feature in enumerate(features, 1):
        print(f"\n=== 开始处理特征 {i}/{len(features)}: {feature} ===")
        
        try:
            # 清理文件名
            clean_feature = feature.strip()
            clean_feature = re.sub(r'[()/\\]', '', clean_feature)  # 移除括号和斜杠
            clean_feature = re.sub(r'\s+', '_', clean_feature)     # 将空格替换为下划线
            clean_feature = clean_feature.replace('²', '2')        # 替换上标2
            print(f"文件名: {clean_feature}_pdp_汇总.png")
            
            # 获取早高峰PDP数据
            print(f"计算早高峰 {feature} 的PDP值...")
            early_x, early_y, x_min, x_max, custom_ticks, tick_spacing = get_pdp_data(model_early, X_early_test, real_early_df, feature)
            print(f"早高峰PDP值范围: {min(early_y):.4f} 到 {max(early_y):.4f}")
            
            # 获取晚高峰PDP数据
            print(f"计算晚高峰 {feature} 的PDP值...")
            late_x, late_y, _, _, _, _ = get_pdp_data(model_late, X_late_test, real_late_df, feature)
            print(f"晚高峰PDP值范围: {min(late_y):.4f} 到 {max(late_y):.4f}")
            
            # 创建画布（1:1比例）
            fig, ax = plt.subplots(figsize=(10, 10))
            
            # 绘制早高峰PDP曲线
            print(f"绘制早高峰 {feature} PDP曲线...")
            ax.plot(early_x, early_y, linewidth=2.5, color='blue', label='早高峰')
            
            # 绘制晚高峰PDP曲线
            print(f"绘制晚高峰 {feature} PDP曲线...")
            ax.plot(late_x, late_y, linewidth=2.5, color='red', label='晚高峰')
            
            # 设置x轴范围
            ax.set_xlim(x_min, x_max)
            
            # 设置x轴刻度
            if custom_ticks is not None:
                ax.set_xticks(custom_ticks)
            else:
                ax.set_xticks(np.arange(np.round(x_min / tick_spacing) * tick_spacing, 
                                      np.round(x_max / tick_spacing) * tick_spacing + tick_spacing, 
                                      tick_spacing))
            
            # 设置标题和标签
            ax.set_title(f'{feature} PDP曲线（早高峰 vs 晚高峰）', fontsize=14, fontweight='bold')
            ax.set_xlabel(f'{feature} ({variable_units.get(feature, "")})', fontsize=12)
            ax.set_ylabel('碳排放 (kgCO2/KM/d)', fontsize=12)
            
            # 添加网格线
            ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)
            
            # 添加图例
            ax.legend(fontsize=10, loc='upper right')
            
            # 设置坐标轴刻度的字体大小
            ax.tick_params(axis='both', which='major', labelsize=10)
            
            # 保存图像
            plt.tight_layout()
            print(f"保存图像到: {os.path.join(save_dir, f'{clean_feature}_pdp_汇总.png')}")
            plt.savefig(os.path.join(save_dir, f"{clean_feature}_pdp_汇总.png"), dpi=300, bbox_inches='tight')
            plt.close()  # 关闭画布，释放内存
            
            # 清理变量，优化内存
            del early_x, early_y, late_x, late_y
            
            print(f"✅ 成功生成 {feature} 的PDP曲线汇总图")
        except Exception as e:
            print(f"❌ 生成 {feature} 的PDP曲线汇总图时出错: {e}")
            import traceback
            traceback.print_exc()
            
            # 检查特征是否存在于数据集中
            if feature not in X_early_test.columns:
                print(f"  ❌ 特征 '{feature}' 不存在于早高峰数据集中")
                print(f"  早高峰数据集的特征列表: {list(X_early_test.columns)}")
            if feature not in X_late_test.columns:
                print(f"  ❌ 特征 '{feature}' 不存在于晚高峰数据集中")
                print(f"  晚高峰数据集的特征列表: {list(X_late_test.columns)}")
            
            # 关闭画布，释放内存
            try:
                plt.close('all')
            except:
                pass
            continue
    
    print(f"所有PDP曲线汇总图已保存到: {save_dir}")

# 主函数
def main():
    generate_summary_pdp()

if __name__ == "__main__":
    main()
