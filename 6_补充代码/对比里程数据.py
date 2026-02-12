import pandas as pd
import os

# 设置文件路径
file1_path = r"d:\Desktop\项目论文\早高峰碳排放\晚高峰共享单车数据_裁剪后.csv"
file2_path = r"d:\Desktop\项目论文\网格轨迹段汇总\碳排放计算与可视化\晚高峰_carbon_emission.csv"

# 检查文件是否存在
if not os.path.exists(file1_path):
    print(f"错误：文件不存在 - {file1_path}")
    exit()

if not os.path.exists(file2_path):
    print(f"错误：文件不存在 - {file2_path}")
    exit()

# 读取文件1
print(f"读取文件：{file1_path}")
df1 = pd.read_csv(file1_path)
print(f"文件1包含 {len(df1)} 行数据")

# 读取文件2
print(f"读取文件：{file2_path}")
df2 = pd.read_csv(file2_path)
print(f"文件2包含 {len(df2)} 行数据")

# 计算文件1的里程总和（行驶里程列）
total_mileage1 = df1['行驶里程'].sum()
print(f"\n文件1的总里程（行驶里程）：{total_mileage1:.2f} 米")
print(f"文件1的总里程（行驶里程）：{total_mileage1/1000:.2f} 公里")

# 计算文件2的里程总和（total_length_m列）
total_mileage2 = df2['total_length_m'].sum()
print(f"文件2的总里程（total_length_m）：{total_mileage2:.2f} 米")
print(f"文件2的总里程（total_length_km）：{df2['total_length_km'].sum():.2f} 公里")

# 计算里程差
difference_m = total_mileage1 - total_mileage2
difference_km = difference_m / 1000

print(f"\n里程差（文件1 - 文件2）：{difference_m:.2f} 米")
print(f"里程差（文件1 - 文件2）：{difference_km:.2f} 公里")
print(f"里程差百分比：{(difference_m / total_mileage1 * 100):.2f}%")
