import pandas as pd
import numpy as np

# 直接加载数据
early_real = pd.read_csv('d:/Desktop/项目论文/建模/早高峰_统一单位.csv')
early_std = pd.read_csv('d:/Desktop/项目论文/建模/特征工程/优化后_早高峰_标准化_utf8.csv')

# 确保列名一致
early_std.columns = [col.strip() for col in early_std.columns]
early_real.columns = [col.strip() for col in early_real.columns]

# 分析碳排放字段的标准化
print('分析碳排放字段的标准化...')
real_col = '碳排放_carbon_emission_kg (kgCO2/KM/d)'

# 取前5个样本进行比较
print('\n前5个样本:')
for i in range(5):
    real_val = early_real[real_col].iloc[i]
    std_val = early_std[real_col].iloc[i]
    print(f'原始值: {real_val:.6f}, 标准化值: {std_val:.6f}')

# 计算原始数据的统计信息
real_mean = early_real[real_col].mean()
real_std = early_real[real_col].std()
real_min = early_real[real_col].min()
real_max = early_real[real_col].max()

print(f'\n原始数据统计:')
print(f'均值: {real_mean:.6f}, 标准差: {real_std:.6f}')
print(f'最小值: {real_min:.6f}, 最大值: {real_max:.6f}')

# 计算标准化数据的统计信息
std_mean = early_std[real_col].mean()
std_std = early_std[real_col].std()
std_min = early_std[real_col].min()
std_max = early_std[real_col].max()

print(f'\n标准化数据统计:')
print(f'均值: {std_mean:.6f}, 标准差: {std_std:.6f}')
print(f'最小值: {std_min:.6f}, 最大值: {std_max:.6f}')

# 尝试Z-score标准化
print('\nZ-score标准化验证:')
for i in range(5):
    real_val = early_real[real_col].iloc[i]
    z_score = (real_val - real_mean) / real_std
    actual_std = early_std[real_col].iloc[i]
    diff = z_score - actual_std
    print(f'Z-score: {z_score:.6f}, 实际标准化: {actual_std:.6f}, 差异: {diff:.6f}')

# 尝试Min-Max标准化
print('\nMin-Max标准化验证:')
for i in range(5):
    real_val = early_real[real_col].iloc[i]
    min_max = (real_val - real_min) / (real_max - real_min)
    actual_std = early_std[real_col].iloc[i]
    diff = min_max - actual_std
    print(f'Min-Max: {min_max:.6f}, 实际标准化: {actual_std:.6f}, 差异: {diff:.6f}')

# 查看两个数据集是否有相同的行数
print(f'\n原始数据行数: {len(early_real)}')
print(f'标准化数据行数: {len(early_std)}')