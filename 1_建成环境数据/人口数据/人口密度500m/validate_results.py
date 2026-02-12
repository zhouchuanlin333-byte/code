import pandas as pd
import numpy as np

# 读取CSV文件
df = pd.read_csv('西安市主城区人口密度_1km网格.csv')

# 显示文件头部
print("文件头部:")
print(df.head())
print("\n" + "="*50 + "\n")

# 基本统计信息
print(f'总行数: {len(df)}')
print(f'\n人口统计:')
print(f'  平均值: {df["total_population"].mean():.2f}')
print(f'  最大值: {df["total_population"].max():.2f}')
print(f'  最小值: {df["total_population"].min():.2f}')
print(f'  总和: {df["total_population"].sum():.2f}')
print(f'\n密度统计:')
print(f'  平均值: {df["population_density"].mean():.2f} 人/km²')
print(f'  最大值: {df["population_density"].max():.2f} 人/km²')
print(f'  最小值: {df["population_density"].min():.2f} 人/km²')
print(f'\n覆盖比例统计:')
print(f'  平均值: {df["coverage_ratio"].mean():.2%}')
print(f'  最大值: {df["coverage_ratio"].max():.2%}')
print(f'  最小值: {df["coverage_ratio"].min():.2%}')

# 验证数据质量
print("\n" + "="*50 + "\n")
print("数据质量检查:")
print(f'空值数量: {df.isnull().sum().sum()}')
print(f'零人口网格数: {(df["total_population"] == 0).sum()}')
print(f'有效数据网格数: {(df["total_population"] > 0).sum()}')

# 查看是否生成了可视化文件
import os
print("\n结果文件检查:")
print(f'CSV文件大小: {os.path.getsize("西安市主城区人口密度_1km网格.csv")} 字节')
print(f'PNG文件是否存在: {os.path.exists("西安市主城区人口分布_LandScan.png")}')
if os.path.exists("西安市主城区人口分布_LandScan.png"):
    print(f'PNG文件大小: {os.path.getsize("西安市主城区人口分布_LandScan.png")} 字节')
