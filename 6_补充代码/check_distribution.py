import pandas as pd
import numpy as np

# 加载原始数据
df = pd.read_csv('d:/Desktop/项目论文/建模/早高峰_统一单位.csv')
df.columns = [col.strip() for col in df.columns]

# 获取人口密度数据
population_density = df['人口密度 (千人/km²)'].values
population_density = population_density[~pd.isna(population_density)]

print('人口密度数据分布分析：')
print(f'总样本数: {len(population_density)}')
print(f'最小值: {np.min(population_density):.3f}')
print(f'最大值: {np.max(population_density):.3f}')
print(f'均值: {np.mean(population_density):.3f}')

# 分析各区间的样本数
intervals = [(0, 5), (5, 10), (10, 15), (15, 20), (20, 25), (25, 30)]
for start, end in intervals:
    count = np.sum((population_density >= start) & (population_density < end))
    percentage = count / len(population_density) * 100
    print(f'{start}~{end}区间: {count}个样本 ({percentage:.1f}%)')

# 超过30的样本
over_30 = np.sum(population_density >= 30)
print(f'30以上: {over_30}个样本 ({over_30/len(population_density)*100:.1f}%)')

# 检查你之前提到的居住POI数量分布
residential_poi = df['居住POI数量 (个)'].values
residential_poi = residential_poi[~pd.isna(residential_poi)]

print('\n居住POI数量分布对比：')
print(f'总样本数: {len(residential_poi)}')
print(f'最小值: {np.min(residential_poi)}')
print(f'最大值: {np.max(residential_poi)}')
print(f'均值: {np.mean(residential_poi):.1f}')

# 分析居住POI数量的区间分布
residential_intervals = [(0, 5), (5, 10), (10, 15), (15, 20), (20, 25), (25, 30)]
for start, end in residential_intervals:
    count = np.sum((residential_poi >= start) & (residential_poi < end))
    percentage = count / len(residential_poi) * 100
    print(f'{start}~{end}区间: {count}个样本 ({percentage:.1f}%)')

over_30_residential = np.sum(residential_poi >= 30)
print(f'30以上: {over_30_residential}个样本 ({over_30_residential/len(residential_poi)*100:.1f}%)')