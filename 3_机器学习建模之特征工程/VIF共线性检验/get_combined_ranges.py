import pandas as pd
import numpy as np

# 设置文件路径
FIXED_EARLY_FILE = '修复后_早高峰_标准化_utf8.csv'
FIXED_LATE_FILE = '修复后_晚高峰_标准化_utf8.csv'

# 读取修复后的标准化数据
try:
    early_data = pd.read_csv(FIXED_EARLY_FILE, encoding='utf-8')
    late_data = pd.read_csv(FIXED_LATE_FILE, encoding='utf-8')
    
    print("=== 数据读取成功 ===")
    print(f"早高峰数据维度: {early_data.shape}")
    print(f"晚高峰数据维度: {late_data.shape}")
    print(f"特征列表: {early_data.columns.tolist()}")
    print()
    
    # 合并两个数据集
    combined_data = pd.concat([early_data, late_data], axis=0, ignore_index=True)
    print(f"合并后数据维度: {combined_data.shape}")
    print()
    
    # 1. 获取所有特征的整体取值范围（最大值和最小值）
    all_features_max = combined_data.max().max()
    all_features_min = combined_data.min().min()
    
    # 2. 获取碳排放数据的标准化范围
    carbon_column = '碳排放_carbon_emission_kg (kgCO2/KM/d)'
    early_carbon_max = early_data[carbon_column].max()
    early_carbon_min = early_data[carbon_column].min()
    late_carbon_max = late_data[carbon_column].max()
    late_carbon_min = late_data[carbon_column].min()
    carbon_overall_max = max(early_carbon_max, late_carbon_max)
    carbon_overall_min = min(early_carbon_min, late_carbon_min)
    
    # 输出结果
    print("=== 标准化数据取值范围统计 ===")
    print("\n1. 所有特征的整体取值范围（合并数据集）:")
    print(f"   最小值: {all_features_min:.6f}")
    print(f"   最大值: {all_features_max:.6f}")
    
    print("\n2. 碳排放特征的标准化范围:")
    print(f"   早高峰:")
    print(f"     最小值: {early_carbon_min:.6f}")
    print(f"     最大值: {early_carbon_max:.6f}")
    print(f"   晚高峰:")
    print(f"     最小值: {late_carbon_min:.6f}")
    print(f"     最大值: {late_carbon_max:.6f}")
    print(f"   整体（合并两个时段）:")
    print(f"     最小值: {carbon_overall_min:.6f}")
    print(f"     最大值: {carbon_overall_max:.6f}")
    
    print("\n=== 统计完成 ===")
    
except Exception as e:
    print(f"数据处理过程中发生错误: {e}")
    import traceback
    traceback.print_exc()