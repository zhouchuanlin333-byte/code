import pandas as pd
import numpy as np
from statsmodels.stats.outliers_influence import variance_inflation_factor
import os

# 确保特征工程目录存在
save_dir = r'd:\Desktop\项目论文\建模\特征工程'
os.makedirs(save_dir, exist_ok=True)

# 读取数据文件
def load_data():
    print("正在读取数据文件...")
    morning_file = r'd:\Desktop\项目论文\建模\早高峰_标准化_utf8.csv'
    evening_file = r'd:\Desktop\项目论文\建模\晚高峰_标准化_utf8.csv'
    
    morning_df = pd.read_csv(morning_file)
    evening_df = pd.read_csv(evening_file)
    
    print(f"早高峰数据形状: {morning_df.shape}")
    print(f"晚高峰数据形状: {evening_df.shape}")
    
    return morning_df, evening_df

# 选择特征列进行共线性分析
def select_features(df):
    # 从列名可以看到12个特征列（排除grid_id和目标变量）
    feature_columns = [
        '人口密度 (千人/km²)', 
        '休闲POI数量 (个)', 
        '办公POI数量 (个)', 
        '公共服务POI数量 (个)', 
        '交通设施POI数量 (个)', 
        '居住POI数量 (个)', 
        '道路密度 (KM/KM²)', 
        '地铁站点数量 (个)', 
        '公交站点数量 (个)', 
        '标准化土地混合熵', 
        '到市中心距离 (km)', 
        '到最近公交距离 (km)'
    ]
    
    # 验证所选特征列是否存在
    available_columns = [col for col in feature_columns if col in df.columns]
    missing_columns = [col for col in feature_columns if col not in df.columns]
    
    if missing_columns:
        print(f"警告: 以下特征列不存在: {missing_columns}")
    
    return df[available_columns].copy()

# 计算方差膨胀因子(VIF)
def calculate_vif(features_df):
    print("正在计算方差膨胀因子(VIF)...")
    
    # 计算VIF
    vif_data = pd.DataFrame()
    vif_data['特征'] = features_df.columns
    vif_data['VIF值'] = [variance_inflation_factor(features_df.values, i) 
                        for i in range(features_df.shape[1])]
    
    # 标记VIF值大于10的特征
    vif_data['是否存在共线性问题'] = vif_data['VIF值'] > 10
    
    return vif_data

# 处理缺失值和异常值
def preprocess_data(features_df):
    # 处理缺失值
    if features_df.isnull().sum().sum() > 0:
        print(f"发现缺失值，总数: {features_df.isnull().sum().sum()}")
        features_df = features_df.fillna(features_df.mean())
    
    # 检查并处理无穷大值
    if np.isinf(features_df).sum().sum() > 0:
        print(f"发现无穷大值，总数: {np.isinf(features_df).sum().sum()}")
        # 替换无穷大值为NaN，然后填充
        features_df = features_df.replace([np.inf, -np.inf], np.nan)
        features_df = features_df.fillna(features_df.mean())
    
    return features_df

# 保存结果
def save_results(vif_data, time_period):
    result_file = os.path.join(save_dir, f'{time_period}_vif分析结果.csv')
    vif_data.to_csv(result_file, index=False, encoding='utf-8-sig')
    print(f"{time_period}VIF分析结果已保存到: {result_file}")
    
    # 保存标记了高VIF特征的文本报告
    report_file = os.path.join(save_dir, f'{time_period}_共线性分析报告.txt')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"{time_period}特征共线性分析报告\n")
        f.write("=" * 50 + "\n\n")
        f.write("方差膨胀因子(VIF)分析结果:\n")
        
        for _, row in vif_data.iterrows():
            status = "❌ 存在严重共线性" if row['是否存在共线性问题'] else "✅ 正常"
            f.write(f"{row['特征']}: {row['VIF值']:.4f} {status}\n")
        
        f.write("\n" + "=" * 50 + "\n")
        f.write("共线性判断标准:\n")
        f.write("- VIF < 5: 不存在明显共线性\n")
        f.write("- 5 ≤ VIF < 10: 存在中等共线性\n")
        f.write("- VIF ≥ 10: 存在严重共线性，建议移除该特征\n")
        
        high_vif_features = vif_data[vif_data['是否存在共线性问题']]['特征'].tolist()
        f.write("\n" + "=" * 50 + "\n")
        if high_vif_features:
            f.write(f"⚠️  存在严重共线性的特征 (VIF > 10):\n")
            for feature in high_vif_features:
                f.write(f"  - {feature}\n")
        else:
            f.write("✅ 未发现严重共线性特征 (VIF > 10)\n")
    
    print(f"{time_period}共线性分析报告已保存到: {report_file}")

# 主函数
def main():
    print("开始特征共线性分析...")
    
    # 加载数据
    morning_df, evening_df = load_data()
    
    # 分析早高峰数据
    print("\n===== 分析早高峰数据 =====")
    morning_features = select_features(morning_df)
    morning_features = preprocess_data(morning_features)
    morning_vif = calculate_vif(morning_features)
    print("早高峰VIF分析结果:")
    print(morning_vif)
    save_results(morning_vif, "早高峰")
    
    # 分析晚高峰数据
    print("\n===== 分析晚高峰数据 =====")
    evening_features = select_features(evening_df)
    evening_features = preprocess_data(evening_features)
    evening_vif = calculate_vif(evening_features)
    print("晚高峰VIF分析结果:")
    print(evening_vif)
    save_results(evening_vif, "晚高峰")
    
    # 汇总分析
    print("\n===== 共线性分析汇总 =====")
    morning_high_vif = morning_vif[morning_vif['是否存在共线性问题']].shape[0]
    evening_high_vif = evening_vif[evening_vif['是否存在共线性问题']].shape[0]
    
    print(f"早高峰存在严重共线性的特征数量 (VIF > 10): {morning_high_vif}")
    print(f"晚高峰存在严重共线性的特征数量 (VIF > 10): {evening_high_vif}")
    
    print("\n共线性分析完成！所有结果已保存到特征工程目录。")

if __name__ == "__main__":
    main()