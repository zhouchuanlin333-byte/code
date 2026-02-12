import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 文件路径
population_csv_path = "d:\Desktop\项目论文\人口数据\人口分布密度\gridid_population_density.csv"
fishnet_shp_path = "d:\Desktop\项目论文\西安市渔网\西安市500米渔网\带编号完整渔网网格.shp"

print("读取数据...")
# 读取数据
population_data = pd.read_csv(population_csv_path)
fishnet_data = gpd.read_file(fishnet_shp_path)

# 显示渔网数据的前几行，查看字段结构
print("\n渔网数据前5行:")
print(fishnet_data.head())
print("\n渔网数据字段:", fishnet_data.columns.tolist())

# 检查是否存在grid_id字段，如果不存在则找出对应的ID字段
id_field = None
for col in fishnet_data.columns:
    if 'id' in col.lower():
        id_field = col
        print(f"找到可能的ID字段: {id_field}")
        break

if id_field is None:
    print("警告: 未找到明确的ID字段，尝试使用索引")
    id_field = fishnet_data.columns[0]
    print(f"使用字段: {id_field}")

# 重命名ID字段以确保可以合并
if id_field != 'grid_id':
    fishnet_data = fishnet_data.rename(columns={id_field: 'grid_id'})
    print(f"已将字段 '{id_field}' 重命名为 'grid_id'")

# 确保grid_id是整数类型
fishnet_data['grid_id'] = fishnet_data['grid_id'].astype(int)
population_data['grid_id'] = population_data['grid_id'].astype(int)

# 合并数据
print("\n合并数据...")
merged_data = fishnet_data.merge(population_data, on='grid_id', how='left')
merged_data['population_density'] = merged_data['population_density'].fillna(0)

print(f"\n合并后的数据量: {len(merged_data)} 个网格")
print(f"有效人口数据网格数: {(merged_data['population_density'] > 0).sum()}")

# 找出高人口密度网格
print("\n人口密度分布情况:")
density_bins = [(0, 5000), (5000, 10000), (10000, 20000), (20000, float('inf'))]
for min_d, max_d in density_bins:
    if max_d == float('inf'):
        count = len(merged_data[merged_data['population_density'] >= min_d])
        print(f">= {min_d} 人/平方公里: {count} 个网格")
    else:
        count = len(merged_data[(merged_data['population_density'] >= min_d) & 
                               (merged_data['population_density'] < max_d)])
        print(f"{min_d}-{max_d} 人/平方公里: {count} 个网格")

# 保存验证数据
validation_data = merged_data[['grid_id', 'population_density']].copy()
validation_data.to_csv("d:\Desktop\项目论文\人口数据\人口分布密度\validation_data.csv", index=False)
print("\n验证数据已保存至: validation_data.csv")

# 创建简单的可视化
print("\n创建简单可视化...")
fig, ax = plt.subplots(1, 1, figsize=(14, 12))

# 绘制所有网格
merged_data.plot(ax=ax, color='lightgrey', linewidth=0.1, edgecolor='white')

# 根据人口密度分级着色
density_levels = [0, 5000, 10000, 20000, float('inf')]
colors = ['lightgrey', 'yellow', 'orange', 'red']

for i in range(len(density_levels) - 1):
    min_d, max_d = density_levels[i], density_levels[i+1]
    if max_d == float('inf'):
        subset = merged_data[merged_data['population_density'] >= min_d]
    else:
        subset = merged_data[(merged_data['population_density'] >= min_d) & 
                            (merged_data['population_density'] < max_d)]
    
    if not subset.empty:
        subset.plot(ax=ax, color=colors[i], linewidth=0.1, edgecolor='white')

# 设置标题
ax.set_title('西安市人口密度分布验证', fontsize=16)
ax.set_xlabel('经度', fontsize=14)
ax.set_ylabel('纬度', fontsize=14)

# 添加简单的图例
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='lightgrey', edgecolor='white', label='0-5000 人/平方公里'),
    Patch(facecolor='yellow', edgecolor='white', label='5000-10000 人/平方公里'),
    Patch(facecolor='orange', edgecolor='white', label='10000-20000 人/平方公里'),
    Patch(facecolor='red', edgecolor='white', label='>20000 人/平方公里')
]
ax.legend(handles=legend_elements, loc='lower right')

plt.tight_layout()
plt.savefig("d:\Desktop\项目论文\人口数据\人口分布密度\density_validation.png", dpi=300, bbox_inches='tight')
print("验证图已保存至: density_validation.png")

print("\n验证完成！")
