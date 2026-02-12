import pandas as pd
import numpy as np

# 读取原始数据
df = pd.read_csv('d:/Desktop/项目论文/建模/早高峰_统一单位.csv')

# 检查道路密度数据
road_density = df['道路密度 (KM/KM²)']
print("道路密度统计信息:")
print(f"样本数量: {len(road_density)}")
print(f"最小值: {road_density.min()}")
print(f"最大值: {road_density.max()}")
print(f"平均值: {road_density.mean()}")
print(f"中位数: {road_density.median()}")
print(f"标准差: {road_density.std()}")

# 检查空值
print(f"空值数量: {road_density.isnull().sum()}")

# 显示分位数
print("\n分位数信息:")
print(f"25%分位数: {road_density.quantile(0.25)}")
print(f"40%分位数: {road_density.quantile(0.40)}")
print(f"50%分位数: {road_density.quantile(0.50)}")
print(f"75%分位数: {road_density.quantile(0.75)}")
print(f"90%分位数: {road_density.quantile(0.90)}")
print(f"95%分位数: {road_density.quantile(0.95)}")