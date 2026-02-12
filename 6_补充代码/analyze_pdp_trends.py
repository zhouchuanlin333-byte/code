import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import os
import json

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

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
    std_df = std_df.dropna(axis=1, how='all')
    
    # 加载真实数据（用于获取真实刻度范围）
    real_df = pd.read_csv(real_file_path)
    
    # 确保列名一致
    std_df.columns = [col.strip() for col in std_df.columns]
    real_df.columns = [col.strip() for col in real_df.columns]
    
    # 分离特征和目标变量（使用标准化数据进行模型训练和PDP计算）
    X = std_df.drop('碳排放_carbon_emission_kg (kgCO2/KM/d)', axis=1)
    y = std_df['碳排放_carbon_emission_kg (kgCO2/KM/d)']
    
    return X, y, real_df

# 训练XGBoost模型
def train_model(X_train, y_train):
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

# 分析早晚高峰的趋势差异
def analyze_trend_difference(feature, early_feature_grid, early_real_pdp, late_feature_grid, late_real_pdp):
    # 计算早高峰曲线的趋势
    early_trend = np.polyfit(early_feature_grid, early_real_pdp, 1)[0]  # 斜率
    early_range = np.max(early_real_pdp) - np.min(early_real_pdp)  # 变化范围
    early_min_idx = np.argmin(early_real_pdp)  # 最低点位置
    early_max_idx = np.argmax(early_real_pdp)  # 最高点位置
    
    # 计算晚高峰曲线的趋势
    late_trend = np.polyfit(late_feature_grid, late_real_pdp, 1)[0]  # 斜率
    late_range = np.max(late_real_pdp) - np.min(late_real_pdp)  # 变化范围
    late_min_idx = np.argmin(late_real_pdp)  # 最低点位置
    late_max_idx = np.argmax(late_real_pdp)  # 最高点位置
    
    # 计算趋势差异
    trend_difference = late_trend - early_trend
    range_difference = late_range - early_range
    
    # 分析曲线形状差异
    # 计算曲线的曲率（使用二阶差分近似）
    early_curvature = np.mean(np.abs(np.diff(early_real_pdp, n=2)))
    late_curvature = np.mean(np.abs(np.diff(late_real_pdp, n=2)))
    curvature_difference = late_curvature - early_curvature
    
    return {
        "early_trend": float(early_trend),
        "late_trend": float(late_trend),
        "trend_difference": float(trend_difference),
        "early_range": float(early_range),
        "late_range": float(late_range),
        "range_difference": float(range_difference),
        "early_min_idx": int(early_min_idx),
        "early_max_idx": int(early_max_idx),
        "late_min_idx": int(late_min_idx),
        "late_max_idx": int(late_max_idx),
        "early_curvature": float(early_curvature),
        "late_curvature": float(late_curvature),
        "curvature_difference": float(curvature_difference)
    }

# 生成趋势分析报告
def generate_trend_report(trend_analysis_results):
    report = "# 早晚高峰PDP趋势差异分析报告\n\n"
    report += "## 特征趋势差异总结\n\n"
    
    for feature, analysis in trend_analysis_results.items():
        report += f"### {feature}\n\n"
        
        # 分析趋势方向
        early_trend_desc = "上升" if analysis["early_trend"] > 0 else "下降"
        late_trend_desc = "上升" if analysis["late_trend"] > 0 else "下降"
        
        # 分析趋势强度
        early_trend_strength = "强" if abs(analysis["early_trend"]) > 0.1 else "弱"
        late_trend_strength = "强" if abs(analysis["late_trend"]) > 0.1 else "弱"
        
        # 分析趋势差异
        trend_diff_desc = "晚高峰上升更快" if analysis["trend_difference"] > 0.05 else \
                         "早高峰上升更快" if analysis["trend_difference"] < -0.05 else \
                         "趋势相似"
        
        # 分析变化范围差异
        range_diff_desc = "晚高峰变化范围更大" if analysis["range_difference"] > 0.5 else \
                         "早高峰变化范围更大" if analysis["range_difference"] < -0.5 else \
                         "变化范围相似"
        
        # 分析曲线形状差异
        curvature_diff_desc = "晚高峰曲线更陡峭" if analysis["curvature_difference"] > 0.1 else \
                             "早高峰曲线更陡峭" if analysis["curvature_difference"] < -0.1 else \
                             "曲线平滑度相似"
        
        report += f"- **早高峰趋势**: {early_trend_desc} ({early_trend_strength}趋势, 斜率: {analysis['early_trend']:.4f})\n"
        report += f"- **晚高峰趋势**: {late_trend_desc} ({late_trend_strength}趋势, 斜率: {analysis['late_trend']:.4f})\n"
        report += f"- **趋势差异**: {trend_diff_desc} (差异: {analysis['trend_difference']:.4f})\n"
        report += f"- **早高峰变化范围**: {analysis['early_range']:.4f} kgCO2/KM/d\n"
        report += f"- **晚高峰变化范围**: {analysis['late_range']:.4f} kgCO2/KM/d\n"
        report += f"- **变化范围差异**: {range_diff_desc} (差异: {analysis['range_difference']:.4f})\n"
        report += f"- **曲线形状差异**: {curvature_diff_desc}\n\n"
        
        # 碳减排建议
        if feature == "公交站点数量 (个)":
            if analysis["late_trend"] < analysis["early_trend"]:
                report += "**碳减排建议**: 晚高峰增加公交站点数量对碳减排效果更显著。\n\n"
            else:
                report += "**碳减排建议**: 早高峰增加公交站点数量对碳减排效果更显著。\n\n"
        elif feature == "地铁站点数量 (个)":
            if analysis["late_trend"] < analysis["early_trend"]:
                report += "**碳减排建议**: 晚高峰增加地铁站点数量对碳减排效果更显著。\n\n"
            else:
                report += "**碳减排建议**: 早高峰增加地铁站点数量对碳减排效果更显著。\n\n"
        elif feature == "道路密度 (KM/KM²)":
            if analysis["late_trend"] > analysis["early_trend"]:
                report += "**碳减排建议**: 晚高峰减少道路密度对碳减排效果更显著。\n\n"
            else:
                report += "**碳减排建议**: 早高峰减少道路密度对碳减排效果更显著。\n\n"
        elif feature == "到最近公交距离 (km)":
            if analysis["late_trend"] < analysis["early_trend"]:
                report += "**碳减排建议**: 晚高峰缩短到最近公交距离对碳减排效果更显著。\n\n"
            else:
                report += "**碳减排建议**: 早高峰缩短到最近公交距离对碳减排效果更显著。\n\n"
        
    return report

# 主函数
def main():
    # 处理早高峰数据
    print("处理早高峰数据...")
    X_early, y_early, real_early_df = load_data("早高峰")
    X_early_train, X_early_test, y_early_train, y_early_test = train_test_split(X_early, y_early, test_size=0.3, random_state=42)
    
    # 训练早高峰模型
    model_early = train_model(X_early_train, y_early_train)
    print("早高峰模型训练完成")
    
    # 处理晚高峰数据
    print("处理晚高峰数据...")
    X_late, y_late, real_late_df = load_data("晚高峰")
    X_late_train, X_late_test, y_late_train, y_late_test = train_test_split(X_late, y_late, test_size=0.3, random_state=42)
    
    # 训练晚高峰模型
    model_late = train_model(X_late_train, y_late_train)
    print("晚高峰模型训练完成")
    
    # 计算PDP值并分析趋势差异
    trend_analysis_results = {}
    
    for feature in X_early.columns:
        print(f"分析特征: {feature}")
        
        # 计算早高峰PDP值
        early_feature_grid, early_real_pdp, _ = calculate_pdp_values(model_early, X_early_test, real_early_df, feature, "早高峰")
        
        # 计算晚高峰PDP值
        late_feature_grid, late_real_pdp, _ = calculate_pdp_values(model_late, X_late_test, real_late_df, feature, "晚高峰")
        
        # 分析趋势差异
        analysis = analyze_trend_difference(feature, early_feature_grid, early_real_pdp, late_feature_grid, late_real_pdp)
        trend_analysis_results[feature] = analysis
        
        # 添加PDP值到分析结果中
        trend_analysis_results[feature]["early_feature_grid"] = early_feature_grid.tolist()
        trend_analysis_results[feature]["early_real_pdp"] = early_real_pdp.tolist()
        trend_analysis_results[feature]["late_feature_grid"] = late_feature_grid.tolist()
        trend_analysis_results[feature]["late_real_pdp"] = late_real_pdp.tolist()
    
    # 保存分析结果到JSON文件
    with open("pdp_trend_analysis.json", "w", encoding="utf-8") as f:
        json.dump(trend_analysis_results, f, ensure_ascii=False, indent=2)
    
    # 生成趋势分析报告
    report = generate_trend_report(trend_analysis_results)
    
    # 保存报告到文件
    with open("pdp_trend_analysis_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("分析完成！报告已保存到 pdp_trend_analysis_report.md")

if __name__ == "__main__":
    main()