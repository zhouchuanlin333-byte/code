import pandas as pd
import numpy as np

# 读取数据
file_path = "西安市主城区人口密度_500m网格.csv"
df = pd.read_csv(file_path)

print("=== 500米网格人口密度数据分析 ===")
print(f"总数据行数: {len(df)}")

# 人口密度统计
pop_density = df['population_density']
print(f"\n人口密度统计:")
print(f"  最小值: {pop_density.min():.2f} 人/km²")
print(f"  最大值: {pop_density.max():.2f} 人/km²")
print(f"  平均值: {pop_density.mean():.2f} 人/km²")
print(f"  中位数: {pop_density.median():.2f} 人/km²")

# 高密度区域分析
high_density_thresholds = [5000, 10000, 20000, 50000]
print(f"\n高密度区域分布:")
for threshold in high_density_thresholds:
    count = (pop_density > threshold).sum()
    percent = count / len(df) * 100
    print(f"  >{threshold}人/km²: {count}个网格 ({percent:.2f}%)")

# 查看最高密度的10个网格
print(f"\n前10个最高密度网格:")
top_10 = df.nlargest(10, 'population_density')[['grid_id_500m', 'grid_id_1km', 'population_density', 'minx', 'miny']]
print(top_10)

# 密度分布区间统计
print(f"\n人口密度区间分布:")
bins = [0, 1000, 2000, 5000, 10000, 50000, float('inf')]
labels = ['0-1000', '1000-2000', '2000-5000', '5000-10000', '10000-50000', '50000+']
df['density_range'] = pd.cut(df['population_density'], bins=bins, labels=labels)
density_counts = df['density_range'].value_counts().sort_index()
for range_name, count in density_counts.items():
    percent = count / len(df) * 100
    print(f"  {range_name}: {count}个网格 ({percent:.2f}%)")

# 检查是否存在密度异常的网格（异常高或异常低）
Q1 = pop_density.quantile(0.25)
Q3 = pop_density.quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

outliers = pop_density[(pop_density < lower_bound) | (pop_density > upper_bound)]
print(f"\n异常值统计:")
print(f"  异常值数量: {len(outliers)}")
print(f"  异常值比例: {len(outliers)/len(df)*100:.2f}%")
if len(outliers) > 0:
    print(f"  异常值密度范围: {outliers.min():.2f} - {outliers.max():.2f} 人/km²")

# 分析1km网格对应的4个500米网格是否有密度差异
print(f"\n1km网格内部密度一致性分析:")
# 随机选择10个1km网格进行检查
sample_grid_ids = df['grid_id_1km'].unique()[:10]
for grid_id in sample_grid_ids:
    sub_df = df[df['grid_id_1km'] == grid_id]
    density_std = sub_df['population_density'].std()
    print(f"  1km网格 {grid_id}: 标准差 = {density_std:.2f}")
    
print(f"\n分析完成！")