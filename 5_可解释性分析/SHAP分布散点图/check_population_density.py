import pandas as pd
import numpy as np

# 加载原始数据查看人口密度分布
df = pd.read_csv('d:/Desktop/项目论文/建模/早高峰_统一单位.csv')
df.columns = [col.strip() for col in df.columns]

# 查看人口密度分布
population_density = df['人口密度 (千人/km²)'].dropna()
print('人口密度分布统计:')
print(f'样本数量: {len(population_density)}')
print(f'最小值: {population_density.min()}')
print(f'最大值: {population_density.max()}')
print(f'均值: {population_density.mean():.2f}')
print(f'中位数: {population_density.median():.2f}')

# 分段统计
bins = [0, 5, 10, 15, 20, 25, 30, float('inf')]
labels = ['0-5', '5-10', '10-15', '15-20', '20-25', '25-30', '30+']
population_density_binned = pd.cut(population_density, bins=bins, labels=labels, right=False)
print('\n分段分布:')
print(population_density_binned.value_counts().sort_index())