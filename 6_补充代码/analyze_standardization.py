import pandas as pd
import numpy as np

# 分析标准化方法
def analyze_standardization():
    # 加载原始数据和标准化数据
    early_real = pd.read_csv('d:/Desktop/项目论文/建模/早高峰_统一单位.csv')
    early_std = pd.read_csv('d:/Desktop/项目论文/建模/特征工程/优化后_早高峰_标准化_utf8.csv')

        # 确保列名一致
    early_std.columns = [col.strip() for col in early_std.columns]
    early_real.columns = [col.strip() for col in early_real.columns]

    # 分析碳排放字段的标准化
    print('分析碳排放字段的标准化...')
    real_col = '碳排放_carbon_emission_kg (kgCO2/KM/d)'
    
    # 取前10个样本进行比较
    real_sample = early_real[[real_col]].head(10)
    std_sample = early_std[[real_col]].head(10)
    
    print('\n前10个样本的原始值:')
    print(real_sample.values.flatten())
    print('\n前10个样本的标准化值:')
    print(std_sample.values.flatten())
    
    # 计算可能的标准化参数
    # 尝试Z-score标准化
    real_mean = early_real[real_col].mean()
    real_std = early_real[real_col].std()
    print(f'\n原始数据均值: {real_mean:.6f}, 标准差: {real_std:.6f}')
    
    # 计算Z-score
    z_score = (real_sample - real_mean) / real_std
    print('\n计算的Z-score值:')
    print(z_score.values.flatten())
    
    # 比较Z-score和实际标准化值
    diff = z_score - std_sample
    print('\nZ-score与实际标准化值的差异:')
    print(diff.values.flatten())
    
    # 尝试Min-Max标准化
    real_min = early_real[real_col].min()
    real_max = early_real[real_col].max()
    min_max = (real_sample - real_min) / (real_max - real_min)
    print('\n计算的Min-Max标准化值:')
    print(min_max.values.flatten())
    
    diff_minmax = min_max - std_sample
    print('\nMin-Max与实际标准化值的差异:')
    print(diff_minmax.values.flatten())
    
    # 计算标准化数据的统计信息
    std_mean = early_std[real_col].mean()
    std_std = early_std[real_col].std()
    print(f'\n标准化数据均值: {std_mean:.6f}, 标准差: {std_std:.6f}')

# 执行分析
analyze_standardization()