import pandas as pd
import numpy as np

# 定义要标准化的文件路径
morning_file = 'd:/Desktop/项目论文/建模/早高峰_统一单位.csv'
evening_file = 'd:/Desktop/项目论文/建模/晚高峰1_统一单位.csv'
morning_output = 'd:/Desktop/项目论文/建模/早高峰_标准化.csv'
evening_output = 'd:/Desktop/项目论文/建模/晚高峰_标准化.csv'

print("开始读取数据文件...")
# 读取CSV文件
morning_df = pd.read_csv(morning_file)
evening_df = pd.read_csv(evening_file)

print(f"早高峰数据形状: {morning_df.shape}")
print(f"晚高峰数据形状: {evening_df.shape}")

# 获取所有列名，除了grid_id需要保留原始值
all_columns = morning_df.columns.tolist()
feature_columns = [col for col in all_columns if col != 'grid_id']

print(f"需要标准化的特征数量: {len(feature_columns)}")
print(f"特征列表: {feature_columns}")

# 创建标准化函数
def z_score_standardize(df, feature_cols):
    """对指定的特征列进行z-score标准化"""
    standardized_df = df.copy()
    
    # 记录标准化前后的统计信息
    stats_before = []
    stats_after = []
    
    for col in feature_cols:
        # 计算原始统计信息
        mean_before = df[col].mean()
        std_before = df[col].std()
        min_before = df[col].min()
        max_before = df[col].max()
        stats_before.append({
            'feature': col,
            'mean_before': mean_before,
            'std_before': std_before,
            'min_before': min_before,
            'max_before': max_before
        })
        
        # 进行z-score标准化
        # 避免除以零的情况
        if std_before > 0:
            standardized_df[col] = (df[col] - mean_before) / std_before
        else:
            standardized_df[col] = df[col] - mean_before
        
        # 计算标准化后的统计信息
        mean_after = standardized_df[col].mean()
        std_after = standardized_df[col].std()
        min_after = standardized_df[col].min()
        max_after = standardized_df[col].max()
        stats_after.append({
            'feature': col,
            'mean_after': mean_after,
            'std_after': std_after,
            'min_after': min_after,
            'max_after': max_after
        })
    
    return standardized_df, pd.DataFrame(stats_before), pd.DataFrame(stats_after)

print("开始对早高峰数据进行标准化处理...")
# 对早高峰数据进行标准化
morning_standardized, morning_stats_before, morning_stats_after = z_score_standardize(morning_df, feature_columns)

print("开始对晚高峰数据进行标准化处理...")
# 对晚高峰数据进行标准化
evening_standardized, evening_stats_before, evening_stats_after = z_score_standardize(evening_df, feature_columns)

# 保存标准化后的数据
morning_standardized.to_csv(morning_output, index=False)
evening_standardized.to_csv(evening_output, index=False)

print(f"早高峰标准化数据已保存至: {morning_output}")
print(f"晚高峰标准化数据已保存至: {evening_output}")

# 显示标准化前后的统计信息对比
print("\n早高峰数据标准化前后统计信息对比:")
morning_comparison = pd.merge(
    morning_stats_before, 
    morning_stats_after, 
    on='feature'
)
print(morning_comparison)

print("\n晚高峰数据标准化前后统计信息对比:")
evening_comparison = pd.merge(
    evening_stats_before, 
    evening_stats_after, 
    on='feature'
)
print(evening_comparison)

# 验证标准化结果
print("\n验证标准化结果:")
print("早高峰标准化后各特征的均值:")
print(morning_standardized[feature_columns].mean().round(6))
print("\n早高峰标准化后各特征的标准差:")
print(morning_standardized[feature_columns].std().round(6))

print("\n晚高峰标准化后各特征的均值:")
print(evening_standardized[feature_columns].mean().round(6))
print("\n晚高峰标准化后各特征的标准差:")
print(evening_standardized[feature_columns].std().round(6))

print("\n标准化处理完成！")
