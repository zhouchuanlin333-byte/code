import pandas as pd
import os

# 定义输入文件路径
morning_file = "早高峰_cleaned.csv"
evening_file = "晚高峰_cleaned.csv"

# 当前工作目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 完整文件路径
morning_path = os.path.join(current_dir, morning_file)
evening_path = os.path.join(current_dir, evening_file)

print(f"开始处理数据文件...")
print(f"工作目录: {current_dir}")

# 读取CSV文件
print(f"正在读取早高峰数据: {morning_file}")
morning_df = pd.read_csv(morning_path)
print(f"正在读取晚高峰数据: {evening_file}")
evening_df = pd.read_csv(evening_path)

# 打印原始数据形状
print(f"早高峰原始数据形状: {morning_df.shape}")
print(f"晚高峰原始数据形状: {evening_df.shape}")

# 打印列名
print("\n早高峰数据列:")
for i, col in enumerate(morning_df.columns, 1):
    print(f"{i}. {col}")

# 定义要删除的列
columns_to_drop = ['公共服务POI数量', '交通设施POI数量']
print(f"\n将删除的列: {columns_to_drop}")

# 决定是否保留grid_id（这里选择保留，因为它在后续分析中可能有用）
keep_grid_id = True
if not keep_grid_id:
    columns_to_drop.append('grid_id')
    print("将同时删除grid_id列")
else:
    print("将保留grid_id列用于后续分析")

# 删除指定列
print("\n正在处理数据...")
morning_cleaned = morning_df.drop(columns=columns_to_drop)
evening_cleaned = evening_df.drop(columns=columns_to_drop)

# 打印处理后的数据形状
print(f"早高峰处理后数据形状: {morning_cleaned.shape}")
print(f"晚高峰处理后数据形状: {evening_cleaned.shape}")

# 打印处理后的列名
print("\n处理后的早高峰数据列:")
for i, col in enumerate(morning_cleaned.columns, 1):
    print(f"{i}. {col}")

# 保存处理后的数据（覆盖原文件）
print("\n正在保存处理后的数据...")
morning_cleaned.to_csv(morning_path, index=False, encoding='utf-8-sig')
evening_cleaned.to_csv(evening_path, index=False, encoding='utf-8-sig')

print(f"早高峰数据已保存到: {morning_file}")
print(f"晚高峰数据已保存到: {evening_file}")
print("\n数据处理完成!")
