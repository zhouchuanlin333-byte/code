import pandas as pd
import numpy as np
import os

# 定义文件路径
morning_file = 'd:/Desktop/项目论文/建模/早高峰_cleaned.csv'
evening_file = 'd:/Desktop/项目论文/建模/晚高峰_cleaned.csv'

print("开始标准化居住POI数据...")

# 处理早高峰数据
print(f"读取早高峰数据: {morning_file}")
morning_df = pd.read_csv(morning_file)

# 检查列是否存在
if '居住POI数量' not in morning_df.columns:
    raise ValueError("早高峰数据中未找到'居住POI数量'列")

# 计算原始数据的统计信息
residential_poi_morning = morning_df['居住POI数量']
print(f"早高峰居住POI数量 - 最小值: {residential_poi_morning.min()}, 最大值: {residential_poi_morning.max()}, 均值: {residential_poi_morning.mean():.4f}, 标准差: {residential_poi_morning.std():.4f}")

# 进行z-score标准化
mean_poi = residential_poi_morning.mean()
std_poi = residential_poi_morning.std()
morning_df['居住POI数量'] = (residential_poi_morning - mean_poi) / std_poi

print(f"早高峰居住POI数量标准化后 - 最小值: {morning_df['居住POI数量'].min():.4f}, 最大值: {morning_df['居住POI数量'].max():.4f}, 均值: {morning_df['居住POI数量'].mean():.4f}, 标准差: {morning_df['居住POI数量'].std():.4f}")

# 保存标准化后的数据到原文件
morning_df.to_csv(morning_file, index=False, encoding='utf-8')
print(f"早高峰数据已保存到原文件")

# 处理晚高峰数据
print(f"\n读取晚高峰数据: {evening_file}")
evening_df = pd.read_csv(evening_file)

# 检查列是否存在
if '居住POI数量' not in evening_df.columns:
    raise ValueError("晚高峰数据中未找到'居住POI数量'列")

# 计算原始数据的统计信息
residential_poi_evening = evening_df['居住POI数量']
print(f"晚高峰居住POI数量 - 最小值: {residential_poi_evening.min()}, 最大值: {residential_poi_evening.max()}, 均值: {residential_poi_evening.mean():.4f}, 标准差: {residential_poi_evening.std():.4f}")

# 进行z-score标准化
mean_poi_evening = residential_poi_evening.mean()
std_poi_evening = residential_poi_evening.std()
evening_df['居住POI数量'] = (residential_poi_evening - mean_poi_evening) / std_poi_evening

print(f"晚高峰居住POI数量标准化后 - 最小值: {evening_df['居住POI数量'].min():.4f}, 最大值: {evening_df['居住POI数量'].max():.4f}, 均值: {evening_df['居住POI数量'].mean():.4f}, 标准差: {evening_df['居住POI数量'].std():.4f}")

# 保存标准化后的数据到原文件
evening_df.to_csv(evening_file, index=False, encoding='utf-8')
print(f"晚高峰数据已保存到原文件")

print("\n居住POI数据标准化处理完成！")
